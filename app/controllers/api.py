# -*- coding: utf-8 -*-
# Import flask dependencies

from flask import Blueprint, request
from app.app import return_result
from tools.http.request import ApiRequest
from app.services.keys import RequestMethod
import json


mod_request = Blueprint('request', __name__, url_prefix='/autotest')


@mod_request.route('/request', methods=['POST'])
def api_request():
    """
    @api {post} /autotest/request   接口请求
    @apiVersion 1.0.0
    @apiName request
    @apiGroup request
    @apiParam {dict}  params      (必须)   请求数据参数
    @apiParam {str}  files      (必须)    文件
    @apiParam {int}  cert  (必须)    鉴权
    @apiParamExample {json} Request-Example:
        {
            "params": {"method": "post", "url": "http://baidu.com", "json": {}},
            "file": {"name": "test": "streams"},
            "cert": "files",
        }
    @apiSuccess (回参) {int} code     0
    @apiSuccess (回参) {str} msg      message
    @apiSuccessExample {json} Success-Response:

        {
            "code": 0,
            "msg": "",
            "data": {}
        }
    """
    url = request.json.get("url")
    method = request.json.get("method")
    method = RequestMethod[method] if isinstance(method, int) else method
    headers = request.json.get("headers", None)
    headers = json.loads(headers) if isinstance(headers , str) else headers or  None
    params = request.json.get("params")
    params = json.loads(params) if params and isinstance(params, str) else params or {}
    file = request.json.get("file")
    cert = request.json.get("cert")
    api_req = ApiRequest()
    ret = api_req.api(url, method, params=params, files=None, headers=headers, cookies=None, cert=None, timeout=100,
                log=None, verify=False)
 
    print(params)
    print(file)
    print(cert)
    return return_result(data=ret)
