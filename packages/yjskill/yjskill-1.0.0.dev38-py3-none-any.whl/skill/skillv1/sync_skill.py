"""
distribute_skill.py
Authors: leibin01(leibin01@baidu.com)
Date: 2024/12/10
"""
import bcelogger
import traceback
import os
import json
from argparse import ArgumentParser
from typing import Optional, List

from baidubce.exception import BceHttpClientError
from .skill_client import SkillClient
from .skill_api_skill import (
    CreateSkillRequest, GetSkillRequest, UpdateSkillRequest)
from devicev1.client.device_client import DeviceClient
from devicev1.client.device_api import (
    UpdateDeviceRequest, InvokeMethodHTTPRequest, ListDeviceRequest, GetConfigurationRequest, parse_device_name)
from jobv1.client.job_api_event import EventKind
from jobv1.client.job_api_metric import (
    MetricKind, CounterKind, MetricLocalName, DataType)
from jobv1.client.job_client import (
    JobClient,
    CreateJobRequest, CreateTaskRequest, CreateEventRequest, UpdateJobRequest,
    CreateMetricRequest, GetJobRequest, DeleteMetricRequest, DeleteJobRequest,
)


JOB_METRIC_DISPLAY_NAME = "技能下发"
MODEL_TASK_METRIC_DISPLAY_NAME = "模型下发任务"
SKILL_TASK_METRIC_DISPLAY_NAME = "技能下发任务"

JOB_NAME = os.getenv("SKILL_SYNC_JOB_NAME", "")
SKILL_TASK_NAME = os.getenv("SKILL_SYNC_TASK_NAME", "")
MODEL_TASK_NAME = os.getenv("MODEL_SYNC_TASK_NAME", "")

EVENT_REASON = "{}（{}）{}"  # 中文名（id）成功/失败原因

MODEL_SUCCEED_COUNT = 0
SKILL_SUCCEED_COUNT = 0
JOB_SUCCEED_COUNT = 0
MODEL_FAILED_COUNT = 0
SKILL_FAILED_COUNT = 0
JOB_FAILED_COUNT = 0


def parse_args():
    """
    Parse arguments.
    """
    parser = ArgumentParser()
    parser.add_argument("--workspace_id", required=True, type=str, default="")
    parser.add_argument("--skill_name",
                        required=True, type=str, default="")
    parser.add_argument("--version", required=True, type=str, default="")
    parser.add_argument("--edge_names", required=True, type=str, default="")

    args, _ = parser.parse_known_args()
    return args


def run():
    """
    sync skill.
    """

    global MODEL_FAILED_COUNT
    global SKILL_FAILED_COUNT
    global JOB_FAILED_COUNT
    global JOB_SUCCEED_COUNT

    bcelogger.info("SyncSkill Start")

    sync_model_succeed_result_path = os.getenv(
        "PF_INPUT_ARTIFACT_SYNC_MODEL_SUCCEED_RESULT", "")
    bcelogger.info("SyncSkill sync_model_succeed_result: %s",
                   sync_model_succeed_result_path)

    with open(f'{sync_model_succeed_result_path}/data', 'r', encoding='utf-8') as file:
        model_succeed_result = json.load(file)
        bcelogger.info("SyncSkill ModelSucceedResult: %s",
                       model_succeed_result)

    args = parse_args()
    bcelogger.info("SyncSkill Args: %s", args)

    org_id = os.getenv("ORG_ID", "")
    user_id = os.getenv("USER_ID", "")

    skill_endpoint = os.getenv("SKILL_ENDPOINT", "")
    job_endpoint = os.getenv("JOB_ENDPOINT", "")
    device_endpoint = os.getenv("DEVICE_ENDPOINT", "")
    bcelogger.info("SyncSkill envs, \n \
                   org_id: %s, \n \
                   user_id: %s, \n \
                   job_name: %s, \n \
                   skill_task_name: %s, \n \
                   model_task_name: %s, \n \
                   skill_endpoint: %s, \n \
                   job_endpoint: %s, \n \
                   device_endpoint: %s", org_id, user_id,
                   JOB_NAME, SKILL_TASK_NAME, MODEL_TASK_NAME,
                   skill_endpoint, job_endpoint, device_endpoint)

    skill_client = SkillClient(endpoint=skill_endpoint,
                               context={"OrgID": org_id, "UserID": user_id})
    job_client = JobClient(endpoint=job_endpoint,
                           context={"OrgID": org_id, "UserID": user_id})
    device_client = DeviceClient(endpoint=device_endpoint,
                                 context={"OrgID": org_id, "UserID": user_id})

    skill = {}
    tags = {}
    ok, err, skill = get_skill(skill_client=skill_client,
                               workspace_id=args.workspace_id,
                               local_name=args.skill_name,
                               version=args.version)
    if not ok:
        update_job_failed(job_client=job_client,
                          workspace_id=args.workspace_id,
                          job_name=JOB_NAME,
                          metric_local_name=MetricLocalName.Failed,
                          reason=err["reason"],
                          message=err["error"][:500])
        return

    bcelogger.debug("SyncSkillGetSkill Succeed, skill:%s", skill)

    ok, err, device_config = get_device_configuration(device_client=device_client,
                                                      workspace_id=args.workspace_id)
    if not ok:
        update_job_failed(job_client=job_client,
                          workspace_id=args.workspace_id,
                          job_name=JOB_NAME,
                          metric_local_name=MetricLocalName.Failed,
                          reason=err["reason"],
                          message=err["error"][:500])
        return

    bcelogger.info(
        "SyncSkillGetDeviceConfig Succeed, device_config:%s", device_config)

    edge_names = args.edge_names.split(",")
    edge_local_names = []
    for edge_name in edge_names:
        device_name = parse_device_name(edge_name)
        if device_name is not None:
            edge_local_names.append(device_name.local_name)

    bcelogger.info("SyncSkillEdgeLocalNames: %s", edge_local_names)

    ok, err, edges = list_devices(
        device_client=device_client,
        workspace_id=args.workspace_id,
        selects=edge_local_names)
    if not ok:
        update_job_failed(job_client=job_client,
                          workspace_id=args.workspace_id,
                          job_name=JOB_NAME,
                          metric_local_name=MetricLocalName.Failed,
                          reason=err["reason"],
                          message=err["error"][:500])
        return

    bcelogger.debug("SyncSkillListDevices Succeed, edges:%s", edges)

    # 要从Artifact的tag取，因为下发是指定了技能的版本
    skill_tag = []
    if skill.graph is not None and 'artifact' in skill.graph:
        skill_tag = skill.graph['artifact']['tags']
    bcelogger.debug("SyncSkillSkillTags: %s", skill_tag)

    for edge in edges:
        bcelogger.info("SyncSkillEdgeInfo: %s", edge)

        edge_local_name = edge["localName"]
        edge_workspace = edge["workspaceID"]
        edge_display_name = edge["displayName"]

        ok, check_result = check_edge(skill_tag=skill_tag,
                                      device_config=device_config,
                                      edge=edge)
        if not ok:
            MODEL_FAILED_COUNT += 1
            SKILL_FAILED_COUNT += 1
            JOB_FAILED_COUNT += 1
            bcelogger.error(
                f"SyncSkillCheckEdgeFailed: {check_result}, edge:{edge_local_name}")

            model_skill_task_and_job_failed(job_client=job_client,
                                            workspace_id=args.workspace_id,
                                            job_name=JOB_NAME,
                                            model_task_name=MODEL_TASK_NAME,
                                            skill_task_name=SKILL_TASK_NAME,
                                            event_kind=EventKind.Failed,
                                            message=check_result,
                                            reason=EVENT_REASON.format(
                                                edge_display_name, edge_local_name, check_result),
                                            metric_local_name=MetricLocalName.Failed,
                                            model_failed_count=MODEL_FAILED_COUNT,
                                            skill_failed_count=SKILL_FAILED_COUNT,
                                            job_failed_count=JOB_FAILED_COUNT)
            continue

        # 盒子状态改为下发中
        ok, err = update_device_status(client=device_client,
                                       workspace_id=edge["workspaceID"],
                                       device_hub_name=edge["deviceHubName"],
                                       device_name=edge["localName"],
                                       status="Processing")
        if not ok:
            MODEL_FAILED_COUNT += 1
            SKILL_FAILED_COUNT += 1
            JOB_FAILED_COUNT += 1
            model_skill_task_and_job_failed(job_client=job_client,
                                            workspace_id=args.workspace_id,
                                            job_name=JOB_NAME,
                                            model_task_name=MODEL_TASK_NAME,
                                            skill_task_name=SKILL_TASK_NAME,
                                            event_kind=EventKind.Failed,
                                            message=err["error"][:500],
                                            reason=err["reason"],
                                            metric_local_name=MetricLocalName.Failed,
                                            model_failed_count=MODEL_FAILED_COUNT,
                                            skill_failed_count=SKILL_FAILED_COUNT,
                                            job_failed_count=JOB_FAILED_COUNT)
            continue

        # TODO 下发模型
        ok, err = sync_model(job_client=job_client,
                             device_client=device_client,
                             edge=edge)
        if not ok:
            SKILL_FAILED_COUNT += 1
            JOB_FAILED_COUNT += 1
            # TODO 1. 模型下发失败，模型失败event，模型失败metric，技能失败metric

            # skill task metric
            create_metric(job_client=job_client,
                          workspace_id=edge_workspace,
                          job_name=JOB_NAME,
                          task_name=SKILL_TASK_NAME,
                          display_name=SKILL_TASK_METRIC_DISPLAY_NAME,
                          local_name=MetricLocalName.Failed,
                          kind=MetricKind.Counter,
                          data_type=DataType.Int,
                          value=[str(SKILL_FAILED_COUNT)])

            # job evnet and metric
            update_job_event_and_metric_failed(job_client=job_client,
                                               workspace_id=edge_workspace,
                                               message=err["error"][:500],
                                               reason=EVENT_REASON.format(
                                                   edge_display_name, edge_local_name, err["reason"]),
                                               job_failed_count=JOB_FAILED_COUNT)
            continue

        ok, err = sync_skill(skill=skill,
                             edge=edge,
                             device_client=device_client,
                             job_client=job_client)
        if not ok:
            JOB_FAILED_COUNT += 1
            update_job_event_and_metric_failed(job_client=job_client,
                                               workspace_id=edge_workspace,
                                               message=err["error"][:500],
                                               reason=EVENT_REASON.format(
                                                   edge_display_name, edge_local_name, err["reason"]),
                                               job_failed_count=JOB_FAILED_COUNT)
            continue

        # job下发成功
        JOB_SUCCEED_COUNT += 1
        create_metric(job_client=job_client,
                      workspace_id=edge_workspace,
                      job_name=JOB_NAME,
                      local_name=MetricLocalName.Success,
                      display_name=JOB_METRIC_DISPLAY_NAME,
                      kind=MetricKind.Counter,
                      data_type=DataType.Int,
                      value=[str(JOB_SUCCEED_COUNT)])

        # 盒子状态恢复
        update_device_status(client=device_client,
                             workspace_id=edge["workspaceID"],
                             device_hub_name=edge["deviceHubName"],
                             device_name=edge["localName"],
                             status="Connected")


def sync_model(edge: dict,
               device_client: DeviceClient,
               job_client: JobClient):
    """
    下发模型

    Returns:
        bool: 是否下发成功
        dict: 错误信息, 例如：{"error": "Internal Server Error xxxx", "reason": "技能上线失败"}
    """

    edge_workspace = edge["workspaceID"]

    # TODO 下发模型失败
    # MODEL_FAILED_COUNT += 1

    # TODO 下发模型成功
    global MODEL_SUCCEED_COUNT
    MODEL_SUCCEED_COUNT += 1
    # 模型下发成功
    create_metric(job_client=job_client,
                  workspace_id=edge_workspace,
                  job_name=JOB_NAME,
                  task_name=MODEL_TASK_NAME,
                  local_name=MetricLocalName.Success,
                  display_name=MODEL_TASK_METRIC_DISPLAY_NAME,
                  kind=MetricKind.Counter,
                  data_type=DataType.Int,
                  value=[str(MODEL_SUCCEED_COUNT)])
    return True, {}


def sync_skill(skill: dict,
               edge: dict,
               device_client: DeviceClient,
               job_client: JobClient):
    """
    下发技能

    Returns:
        bool: 是否下发成功
        dict: 错误信息, 例如：{"error": "Internal Server Error xxxx", "reason": "技能上线失败"}
    """

    global SKILL_FAILED_COUNT
    global SKILL_SUCCEED_COUNT

    edge_workspace = edge["workspaceID"]

    # 技能下发
    # 修改graph中的workspaceID
    graph = build_graph(
        origin_graph=skill.graph,
        replace={skill.workspaceID: edge_workspace})

    create_skill_req = CreateSkillRequest(
        workspaceID=edge_workspace,
        localName=skill.localName,
        displayName=skill.displayName,
        description=skill.description,
        kind="Video",
        fromKind="Edge",
        createKind="Sync",
        tags=skill.tags,
        graph=graph,
        artifact=skill.graph['artifact'],
        imageURI=skill.imageURI,
        defaultLevel=skill.defaultLevel,
        alarmConfigs=skill.alarmConfigs)

    ok, err, skill_resp = create_skill(
        device_hub_name=edge["deviceHubName"],
        device_name=edge["localName"],
        client=device_client,
        req=create_skill_req)
    if not ok:
        SKILL_FAILED_COUNT += 1
        bcelogger.error("SyncSkillCreateSKillFailed: skill=%s,device=%s",
                        skill.localName,
                        edge['localName'])

        # skill task metric
        create_metric(job_client=job_client,
                      workspace_id=edge_workspace,
                      job_name=JOB_NAME,
                      task_name=SKILL_TASK_NAME,
                      display_name=SKILL_TASK_METRIC_DISPLAY_NAME,
                      local_name=MetricLocalName.Failed,
                      kind=MetricKind.Counter,
                      data_type=DataType.Int,
                      value=[str(SKILL_FAILED_COUNT)])
        return False, err

    # 技能下发成功后，技能热更新
    artifact_version = None
    if skill_resp.graph is not None and 'artifact' in skill_resp.graph:
        artifact_version = skill_resp.graph['artifact']['version']
    if artifact_version is not None:
        ok, err = release_skill(client=device_client,
                                workspace_id=edge_workspace,
                                device_hub_name=edge["deviceHubName"],
                                device_name=edge["localName"],
                                skill_local_name=skill.localName,
                                released_version=artifact_version)
        if not ok:
            SKILL_FAILED_COUNT += 1
            # skill task metric
            create_metric(job_client=job_client,
                          workspace_id=edge_workspace,
                          job_name=JOB_NAME,
                          task_name=SKILL_TASK_NAME,
                          display_name=SKILL_TASK_METRIC_DISPLAY_NAME,
                          local_name=MetricLocalName.Failed,
                          kind=MetricKind.Counter,
                          data_type=DataType.Int,
                          value=[str(SKILL_FAILED_COUNT)])
            return False, err

    SKILL_SUCCEED_COUNT += 1
    # 技能下发成功
    create_metric(job_client=job_client,
                  workspace_id=edge_workspace,
                  job_name=JOB_NAME,
                  task_name=SKILL_TASK_NAME,
                  local_name=MetricLocalName.Success,
                  display_name=SKILL_TASK_METRIC_DISPLAY_NAME,
                  kind=MetricKind.Counter,
                  data_type=DataType.Int,
                  value=[str(SKILL_SUCCEED_COUNT)])
    return True, {}


def update_job_event_and_metric_failed(job_client: JobClient,
                                       workspace_id: str,
                                       message: str,
                                       reason: str,
                                       job_failed_count: int):
    """
    更新job的失败event和metric
    """

    # job metric
    create_metric(job_client=job_client,
                  workspace_id=workspace_id,
                  job_name=JOB_NAME,
                  display_name=JOB_METRIC_DISPLAY_NAME,
                  local_name=MetricLocalName.Failed,
                  kind=MetricKind.Counter,
                  data_type=DataType.Int,
                  value=[str(job_failed_count)])

    # job event
    create_event(job_client=job_client,
                 workspace_id=workspace_id,
                 job_name=JOB_NAME,
                 kind=EventKind.Failed,
                 message=message,
                 reason=reason)


def model_skill_task_and_job_failed(job_client: JobClient,
                                    workspace_id: str,
                                    job_name: str,
                                    model_task_name: str,
                                    skill_task_name: str,
                                    event_kind: EventKind,
                                    message: str,
                                    reason: str,
                                    metric_local_name: MetricLocalName,
                                    model_failed_count: int,
                                    skill_failed_count: int,
                                    job_failed_count: int):
    """
    模型任务失败，技能任务失败，job失败
    """

    # model task metric
    create_metric(job_client=job_client,
                  workspace_id=workspace_id,
                  job_name=job_name,
                  task_name=model_task_name,
                  display_name=MODEL_TASK_METRIC_DISPLAY_NAME,
                  local_name=metric_local_name,
                  kind=MetricKind.Counter,
                  data_type=DataType.Int,
                  value=[str(model_failed_count)])

    # skill task metric
    create_metric(job_client=job_client,
                  workspace_id=workspace_id,
                  job_name=job_name,
                  task_name=skill_task_name,
                  display_name=SKILL_TASK_METRIC_DISPLAY_NAME,
                  local_name=metric_local_name,
                  kind=MetricKind.Counter,
                  data_type=DataType.Int,
                  value=[str(skill_failed_count)])

    # job metric
    create_metric(job_client=job_client,
                  workspace_id=workspace_id,
                  job_name=job_name,
                  display_name=JOB_METRIC_DISPLAY_NAME,
                  local_name=metric_local_name,
                  kind=MetricKind.Counter,
                  data_type=DataType.Int,
                  value=[str(job_failed_count)])

    # job event
    create_event(job_client=job_client,
                 workspace_id=workspace_id,
                 job_name=job_name,
                 kind=event_kind,
                 message=message,
                 reason=reason)


def get_skill(skill_client: SkillClient,
              workspace_id: str,
              local_name: str,
              version: str = ""):
    """
    获取技能信息

    Returns:
        boolean: 是否成功
        dict: 错误信息, 例如：{"error": "Internal Server Error xxxx", "reason": "技能上线失败"}
        resp: 技能信息
    """

    req = GetSkillRequest(
        workspaceID=workspace_id,
        localName=local_name,
        version=version)
    resp = {}
    try:
        resp = skill_client.get_skill(req=req)
        return True, {}, resp
    except Exception as e:
        bcelogger.error("SyncSkillGetSkill %s Failed: %s",
                        local_name,
                        traceback.format_exc())
        return False, {"error": str(e), "reason": "获取技能失败"}, resp


def get_device_configuration(device_client: DeviceClient,
                             workspace_id: str):
    """
    获取设备配置

    Returns:
        boolean: 是否成功
        str: 错误信息, 例如：{"error": "Internal Server Error xxxx", "reason": "技能上线失败"}
        dict: 设备硬件-显卡对应关系
    """

    req = GetConfigurationRequest(
        workspace_id=workspace_id,
        device_hub_name="default",
        local_name="default")
    resp = {}
    try:
        resp = device_client.get_configuration(req=req)
    except Exception as e:
        bcelogger.error("SyncSkillGetDeviceConfiguration get_configuration_req=%s Failed: %s",
                        req.model_dump(by_alias=True),
                        traceback.format_exc())
        return False, {"error": str(e), "reason": "查询设备配置失败"}, resp

    deviceAcceleratorConfig = {}
    if resp is not None and resp.device_configs is not None:
        for item in resp.device_configs:
            deviceAcceleratorConfig[item.kind] = item.gpu
    return True, {}, deviceAcceleratorConfig


def list_devices(
        device_client: DeviceClient,
        workspace_id: str,
        selects: Optional[list[str]] = None):
    """
    获取设备列表

    Args:
        device_client: DeviceClient 设备客户端
        workspace_id: str 工作空间ID
        selects: list[str] 设备名称列表,localName
    Returns:
        bool: 是否成功
        dict: 错误信息, 例如：{"error": "Internal Server Error xxxx", "reason": "技能上线失败"}
        list[dict]: 设备列表
    """

    list_device_req = ListDeviceRequest(
        workspaceID=workspace_id,
        deviceHubName="default",
        pageSize=200,
        pageNo=1,
        selects=selects)
    try:
        total = 0
        devices = []
        bcelogger.debug("origin req is %s",
                        list_device_req.model_dump(by_alias=True))

        resp = device_client.list_device(req=list_device_req)
        if resp is not None:
            if resp.totalCount is not None:
                total = resp.totalCount
            if resp.result is not None:
                devices.extend(resp.result)
        bcelogger.trace("SyncSkillListDevice: totalCount=%d pageNo=%d",
                        total,
                        list_device_req.page_no)
        return True, {}, devices
    except Exception as e:
        bcelogger.error("SyncSkillListDevice list_device_req=%s Failed: %s",
                        list_device_req.model_dump(by_alias=True),
                        traceback.format_exc())
        return False, {"error": str(e), "reason": "查询设备失败"}, []


def build_graph(
        origin_graph: dict,
        replace: dict):
    """
    构建graph

    Args:
        origin_graph: dict 原始图
        replace: dict 替换关系<old,new>
    """

    origin_graph_json = json.dumps(origin_graph)
    for old, new in replace.items():
        origin_graph_json = origin_graph_json.replace(old, new)
    return json.loads(origin_graph_json)


def create_metric(job_client: JobClient,
                  workspace_id: str,
                  job_name: str,
                  display_name: str,
                  local_name: MetricLocalName,
                  kind: MetricKind,
                  data_type: DataType,
                  value: List[str],
                  task_name: Optional[str] = None,
                  ):
    """
    创建metric
    """

    create_metric_req = CreateMetricRequest(workspace_id=workspace_id,
                                            job_name=job_name,
                                            display_name=display_name,
                                            local_name=local_name,
                                            kind=kind,
                                            data_type=data_type,
                                            value=value)
    if task_name is not None:
        create_metric_req.task_name = task_name
    try:
        create_metric_resp = job_client.create_metric(create_metric_req)
        bcelogger.debug("create_metric success, response is %s",
                        create_metric_resp.model_dump(by_alias=True))
    except BceHttpClientError as bce_error:
        tags = {
            "errorMessage": bce_error.last_error.args[0]
        }
        if hasattr(bce_error.last_error, 'status_code'):
            tags["errorCode"] = str(bce_error.last_error.status_code)
        else:
            tags["errorCode"] = "500"
        bcelogger.error("create_metric create_metric_req= %s Failed: %s",
                        create_metric_req.model_dump(by_alias=True),
                        traceback.format_exc())
        return [], tags
    except Exception as e:
        tags = {
            "errorCode": "400",
            "errorMessage": "创建指标失败"
        }
        bcelogger.error("create_metric create_metric_req= %s, Failed: %s",
                        create_metric_req.model_dump(by_alias=True),
                        traceback.format_exc())
        return [], tags


def create_event(
    job_client: JobClient,
    workspace_id: str,
    job_name: str,
    kind: EventKind,
    reason: str,
    message: str,
    task_name: Optional[str] = None,
):
    """
    更新job和device的状态
    """

    create_event_req = CreateEventRequest(
        workspace_id=workspace_id,
        job_name=job_name,
        kind=kind,
        reason=reason,
        message=message)
    if task_name is not None:
        create_event_req.task_name = task_name
    try:
        create_skill_task_event_resp = job_client.create_event(
            create_event_req)
        bcelogger.debug("create_event success, response is %s",
                        create_skill_task_event_resp.model_dump(by_alias=True))
    except BceHttpClientError as bce_error:
        tags = {
            "errorMessage": bce_error.last_error.args[0]
        }
        if hasattr(bce_error.last_error, 'status_code'):
            tags["errorCode"] = str(bce_error.last_error.status_code)
        else:
            tags["errorCode"] = "500"
        bcelogger.error("create_event create_event_req= %s Failed: %s",
                        create_event_req.model_dump(by_alias=True),
                        traceback.format_exc())
        return [], tags
    except Exception as e:
        tags = {
            "errorCode": "400",
            "errorMessage": "创建事件失败"
        }
        bcelogger.error("create_event create_event_req=%s Failed: %s",
                        create_event_req.model_dump(by_alias=True),
                        traceback.format_exc())
        return [], tags


def release_skill(client: DeviceClient,
                  workspace_id: str,
                  skill_local_name: str,
                  released_version: int,
                  device_hub_name: str,
                  device_name: str):
    """
    技能上线

    Returns:
        bool: 是否成功
        dict: 错误信息, 例如：{"error": "Internal Server Error xxxx", "reason": "技能上线失败"}
    """

    update_skill_request = UpdateSkillRequest(
        workspaceID=workspace_id,
        localName=skill_local_name,
        releasedVersion=released_version)
    try:
        # 通过BIE调用盒子的create skill HTTP接口
        skill_url = f'api/vistudio/v1/workspaces/{workspace_id}/skills/{skill_local_name}/put'
        invoke_method_req = InvokeMethodHTTPRequest(
            workspaceID=workspace_id,
            deviceHubName=device_hub_name,
            deviceName=device_name,
            uri=skill_url,
            body=update_skill_request.model_dump(by_alias=True),
        )
        skill_resp = client.invoke_method_http(
            request=invoke_method_req)
        bcelogger.info('SyncSkillReleaseSkill req=%s, resp=%s',
                       invoke_method_req, skill_resp)
        if hasattr(skill_resp, 'success') and skill_resp.success == False:
            raise Exception(skill_resp.message)
        return True, {}
    except Exception as e:
        bcelogger.error("SyncSkillReleaseSkill device=%s Failed: %s",
                        device_name, traceback.format_exc())
        return False, {"error": str(e), "reason": "技能上线失败"}


def create_skill(
        device_hub_name: str,
        device_name: str,
        client: DeviceClient,
        req: CreateSkillRequest):
    """
    创建技能

    Returns:
        bool: 是否成功
        dict: 错误信息, 例如：{"error": "Internal Server Error xxxx", "reason": "创建技能失败"}
        skill_resp: 技能信息
    """

    skill_resp = {}
    try:
        # 通过BIE调用盒子的create skill HTTP接口
        device_url = f'v1/workspaces/{req.workspace_id}/skills'
        invoke_method_req = InvokeMethodHTTPRequest(
            workspaceID=req.workspace_id,
            deviceHubName=device_hub_name,
            deviceName=device_name,
            uri=device_url,
            body=req.model_dump(by_alias=True),
        )
        skill_resp = client.invoke_method_http(
            request=invoke_method_req)
        bcelogger.info('SyncSkillCreateSkill req=%s, resp=%s',
                       invoke_method_req, skill_resp)
        return True, {}, skill_resp
    except Exception as e:
        bcelogger.error("SyncSkillCreateSkill device=%s Failed: %s",
                        device_name, traceback.format_exc())
        return False, {"error": str(e), "reason": "创建技能失败"}, skill_resp


def update_job_failed(job_client: JobClient,
                      workspace_id: str,
                      job_name: str,
                      reason: str,
                      message: str):
    """
    更新job状态为失败
    """

    # job status failed
    create_metric(job_client=job_client,
                  workspace_id=workspace_id,
                  job_name=job_name,
                  display_name=JOB_METRIC_DISPLAY_NAME,
                  local_name=MetricLocalName.JobStatus,
                  kind=MetricKind.Gauge,
                  data_type=DataType.String,
                  value=["Failed"])
    # 失败原因
    create_event(job_client=job_client,
                 workspace_id=workspace_id,
                 job_name=job_name,
                 kind=EventKind.Failed,
                 reason=reason,
                 message=message)


def update_device_status(client: DeviceClient,
                         workspace_id: str,
                         device_hub_name: str,
                         device_name: str,
                         status: str):
    """
    更新设备状态

    Returns:
        bool: 是否成功
        dict: 错误信息, 例如：{"error": "Internal Server Error xxxx", "reason": "创建技能失败"}
    """

    try:
        update_device_req = UpdateDeviceRequest(
            workspaceID=workspace_id,
            deviceHubName=device_hub_name,
            deviceName=device_name,
            status=status,
        )
        update_device_resp = client.update_device(
            request=update_device_req)
        bcelogger.info('SyncSkillUpdateDevice req=%s, resp=%s',
                       update_device_req, update_device_resp)
        return True, {}
    except Exception as e:
        bcelogger.error("SyncSkillGetSkill device=%s Failed: %s",
                        device_name, traceback.format_exc())
        return False, {"error": str(e), "reason": f'更新设备状态为{status}失败'}


def check_edge(
        skill_tag: dict,
        device_config: dict,
        edge: dict,
):
    """
    检查技能是否能下发到盒子

    Args:
        skill_tag (dict): 技能标签
        device_config (dict): 设备配置
        edge (dict): 盒子
    """

    if edge["status"] == "Disconnected":
        return False, "设备已断开连接"

    # TODO 下发中，认为失败 (联调阶段先不校验)
    # if edge["status"] == "Processing":
    #     return False, "设备正在下发中"

    if edge["kind"] not in device_config:
        return False, "未找到设备的硬件信息"

    return check_accelerators(
        skill_accelerator=skill_tag["accelerator"], device_accelelator=device_config[edge["kind"]])


def check_accelerators(
        skill_accelerator: str,
        device_accelelator: str,
):
    """
    检查硬件是否匹配

    Args:
        skill_accelerator(str): 技能硬件信息(tag['accelerator'])
        device_accelelator(str): 设备硬件型号
    """

    if skill_accelerator == "":
        return True, ""

    if device_accelelator == "":
        return False, "设备硬件不适配"

    # 将技能硬件信息转换为列表
    skill_accelerators = json.loads(skill_accelerator)
    device_accelerators = [device_accelelator]

    for sac in skill_accelerators:
        if sac not in device_accelerators:
            return False, "设备硬件不适配"

    return True, ""


if __name__ == "__main__":
    run()
