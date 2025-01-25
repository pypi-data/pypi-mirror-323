# -*- coding: utf-8 -*-
"""
Copyright(C) 2024 baidu, Inc. All Rights Reserved

# @Time : 2024/12/9 15:58
# @Author : leibin01
# @Email: leibin01@baidu.com
"""
import unittest
import time
import json
import traceback
from .sync_skill import SkillClient, check_edge, list_devices, get_device_configuration
from .skill_api_skill import CreateSkillRequest, GetSkillRequest, UpdateSkillRequest
from devicev1.client.device_client import DeviceClient
from devicev1.client.device_api import (
    UpdateDeviceRequest, InvokeMethodHTTPRequest, ListDeviceRequest, GetConfigurationRequest, parse_device_name)
from jobv1.client.job_client import (
    JobClient,
    CreateJobRequest, CreateTaskRequest, CreateEventRequest, UpdateJobRequest,
    CreateMetricRequest, GetJobRequest, DeleteMetricRequest, DeleteJobRequest
)
from jobv1.client.job_api_event import EventKind
from jobv1.client.job_api_metric import MetricKind, CounterKind, MetricLocalName, DataType

workspace_id = "wsgdessn"
job_local_name = "leibin_test_job_1"
# job_endpoint = "127.0.0.1:80"
job_endpoint = "10.224.41.35:8340"
device_endpoint = "10.224.41.35:8340"
org_id = "ab87a18d6bdf4fc39f35ddc880ac1989"
user_id = "7e0c86dd01ae4402aa0f4e003f3480fd"
skill_endpoint = "10.224.41.35:8440"
skill_name = "sk-pwWM11Ao"
skill_version = "1"


class TestDistributeSkill(unittest.TestCase):
    """
    Test WindmillDevice Python SDK
    """

    def __init__(self, methodName='runTest'):
        super().__init__(methodName=methodName)
        self.job_client = JobClient(endpoint=job_endpoint,
                                    context={"OrgID": org_id, "UserID": user_id})
        self.device_client = DeviceClient(endpoint=device_endpoint,
                                          context={"OrgID": org_id, "UserID": user_id})
        self.skill_client = SkillClient(endpoint=skill_endpoint,
                                        context={"OrgID": org_id, "UserID": user_id})
        self.skill_task_local_name = ""
        self.model_task_local_name = ""

    def test_get_skill(self):
        """
        Test Get Skill
        """

        get_skill_req = GetSkillRequest(
            workspaceID=workspace_id,
            localName=skill_name,
            version=skill_version)
        skill = self.skill_client.get_skill(req=get_skill_req)
        print(f"\nskill:\n{skill}")
        print(f'\nskill.loacalName:\n{skill.localName}')
        print(f"\nskill.graph:\n{skill.graph}")
        skill_tag = []
        artifact_version = ""
        if skill.graph is not None and 'artifact' in skill.graph:
            skill_tag = skill.graph['artifact']['tags']
            artifact_version = skill.graph['artifact']['version']
        print(f"\nskill_tag:\n{skill_tag}")
        print(
            f"\nartifact_version:\n{type(artifact_version)}_{artifact_version}")

        update_skill_req = UpdateSkillRequest(
            workspaceID=workspace_id,
            localName=skill_name,
            releasedVersion=str(artifact_version))
        print(f'update_skill_req:\n{update_skill_req}')

        device_config = {'DB-SH2': 'BM1684', 'DB-SH3': 'BM1688',
                         'DB-SL4': 'CV186', 'DB-SH5': 'BM1684X'}
        edge = {
            'kind': 'DB-SH3',
            'status': 'Online',
        }
        check_result, msg = check_edge(
            skill_tag=skill_tag, device_config=device_config, edge=edge)
        print(f'check result: {check_result}, message: {msg}')

    def test_build_graph(self):
        """
        Test Build Graph
        """

    def test_parse_device_name(self):
        """
        parse device name
        """
        edge_name = "workspaces/wsgdessn/devicehubs/default/devices/dbsh3000snc24g0017"
        device_name = parse_device_name(edge_name)
        print(f'device_name: {device_name}')
        print(device_name.local_name)

    def test_get_device_config(self):
        """
        Test Get Device Config
        """

        resp, tags = get_device_configuration(
            device_client=self.device_client, workspace_id=workspace_id)
        print(f"\nresp:\n{resp}")
        print(f"\ntags:\n{tags}")

    def test_list_devices(self):
        """
        Test List Devices
        """
        device_client = DeviceClient(endpoint=device_endpoint,
                                     context={"OrgID": "org_id", "UserID": "user_id"})
        devices, tag = list_devices(
            device_client=device_client,
            workspace_id=workspace_id,
            selects=[
                "dbsh3000snc24g0017"]
        )
        print(f"tags: {tag}")
        print(f"device length: {len(devices)}")
        print(json.dumps(devices))

    def test_create_job(self):
        """
        Test Job Service
        """

        job_client = self.job_client

        self.test_del_job()

        create_job_req = CreateJobRequest(
            workspace_id=workspace_id,
            display_name="leibin_test_job",
            local_name=job_local_name,
            tasks=[
                CreateTaskRequest(
                    workspace_id=workspace_id,
                    display_name="技能下发",
                    kind="Distribute/Skill"
                ),
                CreateTaskRequest(
                    workspace_id=workspace_id,
                    display_name="模型下发",
                    kind="Distribute/Model"
                ),
            ],
            tags={"SkillName": "lb测试技能"},
        )
        create_job_resp = job_client.create_job(create_job_req)
        print(f'\ncreate_job_resp:\n{create_job_resp}')

        self.skill_task_local_name = create_job_resp.tasks[0].local_name
        print(f'\nskill_task_name:\n{self.skill_task_local_name}')
        self.model_task_local_name = create_job_resp.tasks[1].local_name
        print(f'\nmodel_task_name:\n{self.model_task_local_name}')

    def test_create_skill_task_event(self):
        """
        Test Create Skill Task Event
        """

        print(f'skill_task_name:{self.skill_task_local_name}')

        job_client = JobClient(endpoint=job_endpoint,
                               context={"OrgID": "org_id", "UserID": "user_id"})

        create_skill_task_event_req = CreateEventRequest(
            workspace_id=workspace_id,
            job_name=job_local_name,
            task_name=self.skill_task_local_name,
            kind=EventKind.Succeed,
            reason="手动更新技能task",
            message="就手动")
        create_skill_task_event_resp = job_client.create_event(
            create_skill_task_event_req)
        print(create_skill_task_event_resp)

    def test_del_job(self):
        """
        Test del job
        """
        try:

            job_client = JobClient(endpoint=job_endpoint,
                                   context={"OrgID": "org_id", "UserID": "user_id"})

            job = self.test_get_job()
            if job is None or job.name == "":
                print(f'\njob not exist\n')
                return

            create_metric_req = CreateMetricRequest(
                workspace_id=workspace_id,
                job_name=job_local_name,
                local_name=MetricLocalName.Status,
                kind=MetricKind.Gauge,
                data_type=DataType.String,
                value=['Failed']
            )
            create_metric_resp = job_client.create_metric(create_metric_req)
            print(f'\ncreate_metric_resp:\n {create_metric_resp}')

            time.sleep(5)
            del_job_req = DeleteJobRequest(
                workspace_id=workspace_id,
                local_name=job_local_name,
            )
            del_job_resp = job_client.delete_job(del_job_req)
            print(f'\ndel_job_resp:\n{del_job_resp}')
        except Exception as e:
            print(e)
            print(f'{traceback.format_exc()}')

    def test_get_job(self):
        """
        Test get job
        """

        get_job_req = GetJobRequest(
            workspace_id=workspace_id,
            local_name=job_local_name
        )
        job_client = JobClient(endpoint=job_endpoint,
                               context={"OrgID": "org_id", "UserID": "user_id"})
        get_job_resp = job_client.get_job(get_job_req)
        print(f'\nget_job_resp:\n{get_job_resp}')
        print(f'\njob status: {get_job_resp.status}')
        print(
            f'\ntask {get_job_resp.tasks[0].name} status: {get_job_resp.tasks[0].status}')
        print(
            f'\ntask {get_job_resp.tasks[1].name} status: {get_job_resp.tasks[1].status}')
        return get_job_resp

    def test_metric(self):
        """
        Test metric
        """

        print(f'begin test_metric')
        self.test_create_job()

        job_client = JobClient(endpoint=job_endpoint,
                               context={"OrgID": "org_id", "UserID": "user_id"})
        # del skill task metric
        del_metric_req = DeleteMetricRequest(
            workspace_id=workspace_id,
            job_name=job_local_name,
            task_name=self.skill_task_local_name,
            local_name=MetricLocalName.Total)
        del_metric_resp = job_client.delete_metric(del_metric_req)
        print(
            f'\ndel skill task metric total del_metric_resp: \n{del_metric_resp}')
        del_metric_req = DeleteMetricRequest(
            workspace_id=workspace_id,
            job_name=job_local_name,
            task_name=self.skill_task_local_name,
            local_name=MetricLocalName.Success)
        del_metric_resp = job_client.delete_metric(del_metric_req)
        print(
            f'\ndel skill task metric success del_metric_resp: \n{del_metric_resp}')
        # del model task metric
        del_metric_req = DeleteMetricRequest(
            workspace_id=workspace_id,
            job_name=job_local_name,
            task_name=self.model_task_local_name,
            local_name=MetricLocalName.Total)
        del_metric_resp = job_client.delete_metric(del_metric_req)
        print(f'\ndel model task total del_metric_resp: \n{del_metric_resp}')
        del_metric_req = DeleteMetricRequest(
            workspace_id=workspace_id,
            job_name=job_local_name,
            task_name=self.model_task_local_name,
            local_name=MetricLocalName.Success)
        del_metric_resp = job_client.delete_metric(del_metric_req)
        print(f'\ndel model task success del_metric_resp: \n{del_metric_resp}')

        # create skill task metric
        create_metric_total_req = CreateMetricRequest(
            workspace_id=workspace_id,
            job_name=job_local_name,
            task_name=self.skill_task_local_name,
            display_name="技能下发metric",
            local_name=MetricLocalName.Total,
            kind=MetricKind.Counter,
            counter_kind=CounterKind.Cumulative,
            value=['2']
        )
        create_metric_total_resp = job_client.create_metric(
            create_metric_total_req)
        print(f'\ncreate_metric_total_resp:\n{create_metric_total_resp}')

        # create model task metric
        create_metric_total_req = CreateMetricRequest(
            workspace_id=workspace_id,
            job_name=job_local_name,
            task_name=self.model_task_local_name,
            display_name="模型下发metric",
            local_name=MetricLocalName.Total,
            kind=MetricKind.Counter,
            counter_kind=CounterKind.Cumulative,
            value=['2']
        )
        create_metric_total_resp = job_client.create_metric(
            create_metric_total_req)
        print(f'\ncreate_metric_total_resp:\n{create_metric_total_resp}')

        time.sleep(5)
        # 模型metric +2
        create_metric_total_req = CreateMetricRequest(
            workspace_id=workspace_id,
            job_name=job_local_name,
            task_name=self.model_task_local_name,
            display_name="模型下发metric",
            local_name=MetricLocalName.Success,
            kind=MetricKind.Counter,
            counter_kind=CounterKind.Cumulative,
            value=['1']
        )
        job_client.create_metric(create_metric_total_req)
        print(f'\ncreate_metric_total_resp:\n{create_metric_total_resp}')

        self.test_get_job()


def suite():
    """
    suite
    """
    suite = unittest.TestSuite()
    # suite.addTest(TestDistributeSkill('test_job_service'))
    # suite.addTest(TestDistributeSkill('test_create_skill_task_event'))
    # suite.addTest(TestDistributeSkill('test_metric'))
    # suite.addTest(TestDistributeSkill('test_del_job'))
    # suite.addTest(TestDistributeSkill('test_get_job'))
    # suite.addTest(TestDistributeSkill('test_get_device_config'))
    # suite.addTest(TestDistributeSkill('test_list_devices'))
    # suite.addTest(TestDistributeSkill('test_parse_device_name'))
    suite.addTest(TestDistributeSkill('test_get_skill'))
    return suite


if __name__ == '__main__':
    print('starting tests...')
    unittest.main(defaultTest='suite')
