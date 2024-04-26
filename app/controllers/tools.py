# -*- coding: utf-8 -*-
# Import flask dependencies

from flask import Blueprint, request, current_app
from app.services.tools import Tools
# from gun import home, bind
from app.app import redis_store, return_result
from app.celery_register.register import run_tool_task
from app.dbs.common import RunToolRecord
import json
import time


mod_tools = Blueprint('tools', __name__, url_prefix='/autotest')


@mod_tools.route('/tools', methods=['GET'])
def tool_task_list():
    """
    @api {post} /autotest/tools  任务记录列表
    @apiVersion 1.0.0
    @apiName records
    @apiGroup tools
    @apiParam {int}  page_no      (非必须)    页码
    @apiParam {int}  page_size    (非必须)    页大小
    @apiParamExample {json} Request-Example:
         {
            "page_no":1,
            "page_size":10
        }

    @apiSuccess (回参) {datetime} created_time  创建时间
    @apiSuccess (回参) {string} description  描述
    @apiSuccess (回参) {int} id  编号
    @apiSuccess (回参) {string} params  参数
    @apiSuccess (回参) {int} type  类型
    @apiSuccess (回参) {datetime} updated_time  更新时间
    @apiSuccessExample {json} Success-Response:
        {
            "code": 0,
            "msg": "",
            "page": 1,
            "current": 1,
            "limit": 7,
            "data": [
                {
                    "created_time": "Fri, 01 Feb 2019 16:15:35 GMT",
                    "params": "{}",
                    "id": 7,
                    "type": 1,
                    "updated_time": "Fri, 01 Feb 2019 16:15:48 GMT"
                }
            ],
            "total": 7
        }

    """
    page = request.values.get("page", type=int)
    limit = request.values.get("limit", type=int)
    query = RunToolRecord.list()
    total = len(query.all())
    if total == 0:
        return return_result(data=[], total=total, page=page, limit=limit)
    page_count = total / limit
    pages = 0
    if page_count < 1:
        pages = 1
    elif pages > int(pages):
        pages += 1
    pages = int(pages)
    record = RunToolRecord.page(query, page, limit)
    records = []
    for item in record.items:
        rec = item.to_dict()
        rec['params'] = json.loads(rec['params'])
        records.append(rec)
    return return_result(data=records, total=total, page=page, limit=limit, current=page, pages=pages)


@mod_tools.route('/tools/hw_monitor', methods=['POST'])
def bm_monitor_task():
    """
    @api {post} /autotest/tools/hw_monitor  硬件性能监控工具
    @apiVersion 1.0.0
    @apiName bm_monitor
    @apiGroup tasks
    @apiParam {int}  body      (必须)
    @apiParamExample {json} Request-Example:
        {
            "device": {
                "type": "BM",
                "ssh_ip": "10.9.112.146",
                "ssh_port": 22,
                "ssh_user": "xxx",
                "ssh_password": "xxx"
                },
            "run_config": {
                "run_duration": 300,
                "notify": 10
            },
            "validate":{
                "docker_checks": [
                    "dockera",
                    ["dockerb", "0.0.0.0:8104-8105"]
                ]
            },
            "limit_rate": {
                "cpu_used_rate": 85, # X86, BM
                "mem_used_rate": 90, X86, BM
                "vpp_used_rate": 90, #BM
                "npu_used_rate": 90, #BM
                "vpu_info_used_rate": 90, #BM
                "gpu_mem_used_rate": 90  # X86
            },
            "email": []
        }
    @apiSuccess (回参) {page_no} page_no  分页
    @apiSuccess (回参) {page_size} page_size  页面数量
    @apiSuccess (回参) {string}   data          Task信息列表
    @apiSuccess (回参) {int} total       模块总数
    @apiSuccessExample {json} Success-Response:

        {
            "code": 0,
            "msg": "",
            "data": {}
        }
    """
    device = request.json.get("device", {})
    run_config = request.json.get("run_config", {})
    validate = request.json.get("validate", {})
    limit_rate = request.json.get("limit_rate", {})
    mail = request.json.get("email", [])
    if not device or device.get('type') not in ['X86', "BM"]:
        return return_result(code=3, msg="设备类型必带并且只能是'X86', 'BM'】其中一个选项")
    params = {'type': 1, 'params': json.dumps(request.json)}
    record_id = RunToolRecord.create(**params).id
    run_tool_task.apply_async(
            (record_id, device, run_config, validate, limit_rate, mail), queue=current_app.config['TASKQUEEN'])
    data = {"id": record_id}
    return return_result(data=data)


@mod_tools.route('/tools/hw_monitor/stop', methods=['POST'])
def stop_bm_monitor_task():
    """
    @api {post} /autotest/hw_monitor/stop  停止硬件性能监控任务
    @apiVersion 1.0.0
    @apiName bm_monitor
    @apiGroup tasks
    @apiParam {int}  body      (必须)
    @apiParamExample {json} Request-Example:
    {
        "id":  10
    }
    @apiSuccess (回参) {string}   data       
    @apiSuccess (回参) {int} code       
    @apiSuccessExample {json} Success-Response:
        {
            "code": 0,
            "msg": "",
            "data": {}
        }
    """
    record_id = request.json.get("id", {})
    redis_store.set(f'run_tool_task:{record_id}', 1)
    return return_result()

@mod_tools.route("/tools/iec104/send", methods=['POST'])
def iec104_sender():
    dst_ip = request.json.get("ip")
    dst_port = request.json.get("port")
    typ = request.json.get("indentifier", 31)
    vsq = request.json.get("number", 1)
    cot = request.json.get("cause", 3)
    info_addr= request.json.get("point", 2336)
    status= request.json.get("status", "10")
    # breakpoint()
    if not dst_ip or not dst_port:
        return return_result(code=3, msg="Dst ip and port must require")
    if not typ:
        return return_result(code=3, msg="IEC104 indentifier must require")
    params = {'type': 2, 'params': json.dumps(request.json)}
    record_id = RunToolRecord.create(**params).id
    error, hex_data, message = Tools.iec104_sender(dst_ip, dst_port, typ, vsq, cot, info_addr, status)
    data = {'error': error, "data": hex_data, "message": message.split('\n')}
    return return_result(data=data)


@mod_tools.route("/tools/b_protocol/send", methods=['POST'])
def b_protocol_sender():
    # {"platform_ip": "10.9.114.4", "platform_port": 5900, "platform_code": "091600000000000000",
    # "sip_auth_password":"12345", "station_code": "091600000100000000", 
    # "station_cam_code":"0916000001030100XX", "station_ip": "10.9.114.4", "station_port":6000,
    # "count": 1, "func": "register", "index":1, "start":0, "end":1, 'from_side': 'platform', 'response_mark': False}
    func = request.json.get("func", 'register')
    resp_mark = request.json.get("resp_mark", False)
    params = {'type': 3, 'params': json.dumps(request.json)}
    record_id = RunToolRecord.create(**params).id
    station_data = request.json
    station_data.update({'record_id': record_id})
    redis_store.set(f'b_protocol:send:{record_id}', json.dumps(station_data))
    message = Tools.b_protocol_send(func, request.json, station_data)
    st = time.time()
    recv = []
    if resp_mark:
        while 1:
            recv = json.loads(redis_store.get(f'b_protocol:recv:{record_id}') or '[]')
            if recv:
                break
            elif time.time() - st > 100:
                break
    data = {"send": message, 'recv': recv, 'record_id': record_id} # 'params': request.json, 
    return return_result(data=data)