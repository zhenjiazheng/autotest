# -*- coding: utf-8 -*-
# Import flask dependencies

from flask import Blueprint, request
from app.app import return_result


result_collect = Blueprint('case_collect', __name__, url_prefix='/autotest')


@result_collect.route('/case_collect', methods=['GET'])
def case_collect():
    """
    @api {post} /autotest/case_collect  收集测试用例结果
    @apiVersion 1.0.0
    @apiName case_collect
    @apiGroup Case_Collect
    @apiParam {dict}  result      (必须)    测试结果
    @apiParam {str}  serial      (必须)    测试序列
    @apiParam {int}  project_id  (必须)    项目id
    @apiParamExample {json} Request-Example:
        {
            "result": {},
            "serial": "serialA",
            "project_id": 1,
        }
    @apiSuccess (回参) {int} code     0
    @apiSuccess (回参) {str} msg      message
    @apiSuccessExample {json} Success-Response:

        {
            "code": 0,
            "msg": "",
        }
    """
    result = request.json.get("result")
    serial = request.json.get("serial")
    project_id = request.json.get("project_id")
 
    print(result)
    print(serial)
    print(project_id)
    return return_result()
