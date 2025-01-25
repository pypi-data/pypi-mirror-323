# -*- coding: utf-8 -*-
"""
Copyright(C) 2024 baidu, Inc. All Rights Reserved

# @Time : 2024/12/9 15:58
# @Author : leibin01
# @Email: leibin01@baidu.com
"""
import unittest
import json
from .skill_api_skill import CreateSkillRequest
from .sync_skill import build_graph, check_accelerators, check_edge


class TestSkillAPI(unittest.TestCase):
    """
    Test Device
    """

    def test_check_edge(self):
        """
        检查技能是否能下发到盒子
        """
        skill_tag = {}
        model_accelerators = ["T4", ["gpu1"]]
        json.dumps(model_accelerators)
        skill_tag["accelerator"] = json.dumps(model_accelerators)

        edge = {
            "status": "Disconnected",
            "kind": "123"
        }
        device_config = {"abc": "gpu1"}
        ok, msg = check_edge(skill_tag=skill_tag, edge=edge,
                             device_config=device_config)
        self.assertEqual(ok, False)
        self.assertEqual(msg, "设备已断开连接")

        edge["status"] = "Processing"
        ok, msg = check_edge(skill_tag=skill_tag, edge=edge,
                             device_config=device_config)
        self.assertEqual(ok, False)
        self.assertEqual(msg, "设备正在下发中")

        edge["status"] = ""
        ok, msg = check_edge(skill_tag=skill_tag, edge=edge,
                             device_config=device_config)
        self.assertEqual(ok, False)
        self.assertEqual(msg, "未找到设备的硬件信息")

        edge["kind"] = "abc"
        ok, msg = check_edge(skill_tag=skill_tag, edge=edge,
                             device_config=device_config)
        self.assertEqual(ok, True)

    def test_check_accelerator(self):
        """
        检查技能是否能下发到加速器
        """

        skill_tag = ""
        device_tag = ""
        ok, msg = check_accelerators(
            skill_accelerator=skill_tag, device_accelelator=device_tag)
        self.assertEqual(ok, True)

        skill_tag = '[\"T4\",\"A100\"]'
        ok, msg = check_accelerators(
            skill_accelerator=skill_tag, device_accelelator=device_tag)
        self.assertEqual(ok, False)

        device_tag = "abc"
        ok, msg = check_accelerators(
            skill_accelerator=skill_tag, device_accelelator=device_tag)
        self.assertEqual(ok, False)

        device_tag = "A100"
        ok, msg = check_accelerators(
            skill_accelerator=skill_tag, device_accelelator=device_tag)
        self.assertEqual(ok, False)

    def test_build_graph(self):
        """
        Test build graph
        """
        graph = {
            "name": "workspaces/wsnfkyki/modelstores/",
            "content": {
                "name": "workspaces/wsnfkyki/modelstores/",
            }
        }
        graph = build_graph(origin_graph=graph, replace={"wsnfkyki": "123456"})
        self.assertTrue(graph["name"] == "workspaces/123456/modelstores/")
        self.assertTrue(graph["content"]["name"] ==
                        "workspaces/123456/modelstores/")

    def test_create_skill_request(self):
        """
        Test create skill request
        """

        req = CreateSkillRequest(
            workspaceID="ws",
            localName="local",
            displayName="display",
            description="description",
            kind="Video",
            createKind="Manual",
            fromKind="Other",
            tags={"hello_tag": "world_tag"},
            graph={"name": "graph_name"},
            imageURL="http://www.baidu.com",
            defaultLevel=4)
        print(req.model_dump_json(by_alias=True))


def suite():
    """
    suite
    """
    suite = unittest.TestSuite()
    # suite.addTest(TestDistributeSkill('test_job_service'))
    # suite.addTest(TestDistributeSkill('test_create_skill_task_event'))
    suite.addTest(TestSkillAPI('test_check_accelerator'))
    # suite.addTest(TestDistributeSkill('test_del_job'))
    # suite.addTest(TestDistributeSkill('test_get_job'))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
