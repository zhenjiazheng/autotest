# -*- coding: utf-8 -*-
# Import flask dependencies

from flask import Blueprint, request, Response, current_app
from app.app import return_result
from gun import bind
from app.dbs.common import db, Project
from app.services.tasks import *
from app.celery_register.register import run_ci_task

mod_tasks = Blueprint('tasks', __name__, url_prefix='/autotest')


@mod_tasks.route('/tasks', methods=['GET'])
def tasks_list():
    """
    @api {get} /autotest/tasks?page_no=1&page_size=1&project_id=1  任务列表
    @apiVersion 1.0.0
    @apiName task_list
    @apiGroup tasks
    @apiParam {int}  page_no      (非必须)    页码
    @apiParam {int}  page_size    (非必须)    页大小
    @apiParam {int}  project_id   (非必须)    项目id
    @apiParam {int}  image        (非必须)    镜像关键字
    @apiParamExample {json} Request-Example:
        {
            "page_no": 1,
            "page_size": 20,
            "project_id": 1,
            "image": "registry"
        }
    @apiSuccess (回参) {page_no} page_no  分页
    @apiSuccess (回参) {page_size} page_size  页面数量
    @apiSuccess (回参) {string}   data          Task信息列表
    @apiSuccess (回参) {int} total       模块总数
    @apiSuccessExample {json} Success-Response:

        {
            "code": 0,
            "msg": "",
            "data": [
            {
                "image": "",
                "created_time": "2019-04-25 16:42:56",
                "env": {},
                "id": 1,
                'vol": {},
                "pipeline_id": 111,
                "status": 1,
                "project_id": 1,
                "updated_time": "2019-11-21 16:25:58"
            }
            ],
            "total": 1,
            "page_no": 1,
            "page_size": 10
        }
    """
    page = request.values.get("page", type=int)
    limit = request.values.get("limit", type=int)
    project_id = request.values.get("project_id", type=int)
    image_filter = request.values.get("image", type=str)

    query = Tasks.list()
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
    if project_id:
        query = query.filter_by(project_id=project_id)
    if image_filter:
        query = query.filter(Tasks.title.like("%{0}%".format(
            image_filter.replace('%', '\\%').replace('_', '\_'))))
    total = len(query.all())
    data = []
    for item in query:
        data.append(item.to_dict())
    return return_result(data=data, total=total, page=page, limit=limit, current=page, pages=pages)


@mod_tasks.route('/tasks/run', methods=['POST'])
def tasks_run():
    """
    @api {get} /autotest/run_task  任务运行
    @apiVersion 1.0.0
    @apiName task_run
    @apiGroup tasks
    @apiParam {string}  image    (必须)    镜像
    @apiParam {string}  mark   (非必须)     测试过滤
    @apiParam {json}  env   (非必须)     环境变量
    @apiParam {string}  command   (非必须)   运行指令
    @apiParam {json}  vol   (非必须)   挂载目录
    @apiParam {string}  pipeline_id   (非必须)  任务管道ID
    @apiParam {string}  test_location   (非必须)  测试指定目录
    @apiParamExample {json} Request-Example:
        {
            "image": "image_name:v1",
            "mark": "regression"
            "env": {},
            "vol": {}，
            “command”: "test_command",
            "pipelie_id": "abc",
            "test_location": "tests"
        }
    @apiSuccess (回参) {string}   data          Dockers信息列表
    @apiSuccessExample {json} Success-Response:

        {
            "code": 0,
            "msg": "成功",
            "data": {"log": "logxxx.log"}
        }
    """
    project_id = request.json.get("project_id")  # 1
    image = request.json.get("image")  # "testabc:v1"
    env = request.json.get("env")
    mark = request.json.get("mark")
    vol = request.json.get("vol")
    pipeline_id = request.json.get('pipeline_id')
    location = request.json.get('test_location')
    command = request.json.get('command')
    log = os.path.join("report", "docker_logs", f"{pipeline_id}.log")
    prj = Project.get(id=project_id)
    prj = prj.to_dict() if prj else {}
    if 'id' not in request.json:
        Tasks.create(**request.json)
    run_ci_task.apply_async(
        (prj, image, pipeline_id, log, location, mark, env, vol, command), queue=current_app.config['TASKQUEEN'])
    return return_result(data={"log": log})

@mod_tasks.route('/tasks/edit', methods=['POST'])
def tasks_edit():
    """
    @api {post} /autotest/tasks/edit  任务编辑
    @apiVersion 1.0.0
    @apiName task_edit
    @apiGroup tasks
    @apiParam {string}  id    (必须)    任务id
    @apiParam {json}  data    (必须)    任务参数
    @apiParamExample {json} Request-Example:
        {   "id": 1, 
            "image": "image_name:v1",
            "mark": "regression"
            "env": {},
            "vol": {}，
            “command”: "test_command",
            "pipelie_id": "abc",
            "test_location": "tests"
            }
        }
    @apiSuccess (回参) {string}   data          
    @apiSuccessExample {json} Success-Response:

        {
            "code": 0,
            "msg": "成功",
            "data": {
                "image": "image_name:v1",
                "mark": "regression"
                "env": {},
                "vol": {}，
                “command”: "test_command",
                "pipelie_id": "abc",
                "test_location": "tests"
            }
        }
    """
    task_id = request.json.get("id")  # 1
    task_params = request.json
    task_params.pop('id')
    task = Tasks.get(id=task_id)
    task.update(**task_params)
    return return_result(data=task.to_dict())


@mod_tasks.route('/tasks/status', methods=['POST'])
def tasks_status():
    """
    @api {post} /autotest/task_status  任务状态
    @apiVersion 1.0.0
    @apiName task_status
    @apiGroup tasks
    @apiParam {int}  pipeline_id    (必须)    pipeline_id + job_id
    @apiParamExample {json} Request-Example:
        {
            "pipeline_id": "111111_22222"
        }
    @apiSuccess (回参) {string}   data          Status
    @apiSuccessExample {json} Success-Response:

        {
            "code": 0,
            "msg": "成功",
            "data": {"status": 2, "report_url": "test_url"}
        }
    """
    pipeline_id = request.json.get('pipeline_id')
    task = db.session.query(Tasks).filter_by(pipeline_id=pipeline_id).first()
    report_url = f'http://{bind}/task/{task.report}' if task.report else ''
    return return_result(data={"status": task.status, 'report_url': report_url})


@mod_tasks.route('/tasks/log', methods=['GET'])
def download_log():
    """
    @api {get} /autotest/task_log  任务状态
    @apiVersion 1.0.0
    @apiName task_status
    @apiGroup tasks
    @apiParam {int}  pipeline_id    (必须)    pipeline_id + job_id
    @apiParamExample {json} Request-Example:
        {
            "pipeline_id": "111111_22222"
        }
    @apiSuccess (回参) {string}   data          Status
    @apiSuccessExample {json} Success-Response:
        Response Data
    """
    filename = request.args.get('pipeline_id')
    path = os.path.join('report', 'docker_logs', f'{filename}.log')

    def file_send():
        store_path = path
        with open(store_path, 'rb') as targetfile:
            while 1:
                data = targetfile.read(20 * 1024 * 1024)  # 每次读取20M
                if not data:
                    break
                yield data

    response = Response(file_send(), content_type='text/plain')
    response.headers["Content-disposition"] = f'attachment; filename={filename}.log'  # 如果不加上这行代码，导致下图的问题
    return response
