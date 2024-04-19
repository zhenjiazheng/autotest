# -*- coding: utf-8 -*-
# Import flask dependencies
from flask import Blueprint, request
from app.app import return_result
from app.dbs.common import Project

mod_project = Blueprint('projects', __name__, url_prefix='/autotest')


@mod_project.route('/projects', methods=['GET'])
def project_list():
    """
    @api {get} /autotest/projects?page_no=1&page_size=10 项目列表
    @apiVersion 1.0.0
    @apiName projects_list
    @apiGroup projects
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
    @apiSuccess (回参) {string} name  名称
    @apiSuccess (回参) {string} owner  创建人
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
                    "description": "特征网关接口测试",
                    "id": 7,
                    "name": "特征网关",
                    "updated_time": "Fri, 01 Feb 2019 16:15:48 GMT"
                }
            ],
            "total": 7
        }

    """
    page = request.values.get("page", type=int)
    limit = request.values.get("limit", type=int)
    pro_query = Project.list()
    total = len(pro_query.all())
    if total == 0:
        return return_result(data=[], total=total, page=page, limit=limit)
    page_count = total / limit
    pages = 0
    if page_count < 1:
        pages = 1
    elif pages > int(pages):
        pages += 1
    pages = int(pages)
    prjs = Project.page(pro_query, page, limit)
    projects = []
    for item in prjs.items:
        project = item.to_dict()
        projects.append(project)
    return return_result(data=projects, total=total, page=page, limit=limit, current=page, pages=pages)


@mod_project.route('/projects', methods=['POST'])
def project_add():
    """
     @api {post} /autotest/projects 项目创建
     @apiVersion 3.1.0
     @apiName project_add
     @apiGroup projects
     @apiParam {string}  name     (必须)    名称
     @apiParam {string}  description    (非必须)   描述
     @apiParamExample {json} Request-Example:
         {
            "name":"litest",
            "description":"test project"
         }

    @apiSuccess (回参) {datetime} created_time  创建时间
    @apiSuccess (回参) {string} description  描述
    @apiSuccess (回参) {int} id  编号
    @apiSuccess (回参) {string} name  名称
    @apiSuccess (回参) {string} owner  创建人
    @apiSuccess (回参) {datetime} updated_time  更新时间
    @apiSuccessExample {json} Success-Response:
        {
            "code": 0,
            "msg": "添加成功！",
            "project": {
                "created_time": "Sun, 10 Mar 2019 19:35:41 GMT",
                "description": "test project",
                "id": 9,
                "name": "litest",
                "updated_time": "Sun, 10 Mar 2019 19:35:41 GMT"
            }
        }

    @apiErrorExample {json} Error-Response:
        {
          "code": 3,
          "msg": "该项目名已经在列表中存在。"
        }

      """
    name = request.json.get("name")
    description = request.json.get("description", "")
    if not str(name).replace(" ", "") or len(str(name)) > 40:
        return return_result(code=3, msg="项目名称为空或长度过长")
    project_title = Project.query.filter(Project.name == name).first()
    if project_title:
        return return_result(code=3, msg="项目名称已经存在,请更换名称")
    new_project = Project.create(**request.json)
    return return_result(data=new_project.to_dict())


@mod_project.route('/projects/<project_id>', methods=['GET', 'PUT', 'DELETE'])
def project_get(project_id):
    """
    @api {get} /autotest/projects/1 项目详情查询
    @apiVersion 1.9.0
    @apiName project_get
    @apiGroup projects
    @apiParam {int}  project_id      (必须)    项目编号
    @apiParamExample {json} Request-Example:
         {
            "project_id":1
         }
    @apiSuccess (回参) {int} id            项目id
    @apiSuccess (回参) {string} name       项目名称
    @apiSuccessExample {json} Success-Response:
          {
            "code": 0,
            "msg": "获取成功",
            "data": {
                    "description": "SCG-SEP效能平台",
                    "name": "单接口功能"
                }
        }
    @apiErrorExample {json} Error-Response:
        {
            "code":3,
            "msg": "项目不存在"
        }

     @api {put} /autotest/projects/9 项目修改
     @apiVersion 1.0.0
     @apiName project_update
     @apiGroup projects
     @apiParam {string}  name     (必须)    名称
     @apiParam {dict}  repos    (非必须)     代码仓
     @apiParam {string}  description    (非必须)   描述
     @apiParam {json}  related_project    (非必须)  关联项目(key为平台id,value为项目列表)
     @apiParamExample {json} Request-Example:
         {
            "name":"litest",
            "description":"edit project"
         }

    @apiSuccess (回参) {datetime} created_time  创建时间
    @apiSuccess (回参) {string} description  描述
    @apiSuccess (回参) {int} id  编号
    @apiSuccess (回参) {string} name  名称
    @apiSuccess (回参) {string} owner  创建人
    @apiSuccess (回参) {datetime} updated_time  更新时间
    @apiSuccessExample {json} Success-Response:
        {
            "code": 0,
            "msg": "更新成功！",
            "data": {
                "created_time": "Sun, 10 Mar 2019 19:35:41 GMT",
                "description": "edit project",
                "id": 9,
                "name": "litest",
                "updated_time": "Sun, 10 Mar 2019 20:20:51 GMT"
            }
        }

    @apiErrorExample {json} Error-Response:
        {
          "code": 3,
          "msg": "项目名称已存在！"
        }

     @api {delete} /autotest/projects/9 项目删除
     @apiVersion 1.0.0
     @apiName project_del
     @apiGroup projects
     @apiParam {int}  project_id     (必须)    项目编号
     @apiParamExample {json} Request-Example:
        {}

    @apiSuccessExample {json} Success-Response:
        {
            "code": 0,
            "msg": ""
        }

    @apiErrorExample {json} Error-Response:
        {
          "code": 3,
          "msg": "请先删除项目关联的配置及参数。"
        }
    """
    project = Project.get(id=project_id)
    if not project:
        return return_result(code=3, msg="项目不存在")
    if request.method == 'GET':
        return return_result(data=project.to_dict())
    elif request.method == 'PUT':
        name = request.json.get("name", project.name)
        if not str(name).replace(" ", "") or len(str(name)) > 40:
            return return_result(code=3, msg="项目名称为空或长度过长")
        obj = project.update(**request.json)
        return return_result(data=obj.to_dict())
    elif request.method == 'DELETE':
        project.delete(_hard=True)
        return return_result()
    else:
        return return_result()

@mod_project.route('/projects', methods=['PUT'])
def project_update():
    """
     @api {post} /autotest/projects 项目更新
     @apiVersion 1.3
     @apiName project_update
     @apiGroup projects
     @apiParam {string}  name     (必须)    名称
     @apiParam {string}  description    (非必须)   描述
     @apiParamExample {json} Request-Example:
         {  
            "id": 1,
            "name":"litest",
            "description":"test project"
         }

    @apiSuccess (回参) {datetime} created_time  创建时间
    @apiSuccess (回参) {string} description  描述
    @apiSuccess (回参) {int} id  编号
    @apiSuccess (回参) {string} name  名称
    @apiSuccess (回参) {datetime} updated_time  更新时间
    @apiSuccessExample {json} Success-Response:
        {
            "code": 0,
            "msg": "更新成功！",
            "project": {
                "created_time": "Sun, 10 Mar 2019 19:35:41 GMT",
                "description": "test project",
                "id": 9,
                "name": "litest",
                "updated_time": "Sun, 10 Mar 2019 19:35:41 GMT"
            }
        }

    @apiErrorExample {json} Error-Response:
        {
          "code": 3,
          "msg": "该项目名已经在列表中存在。"
        }

      """
    pid = request.json.get("id")
    description = request.json.get("description", "")
    project = Project.query.filter(Project.id == pid).first()
    if not project:
        return return_result(code=3, msg="项目不存在")
    project.update(description=description)
    return return_result(data=project.to_dict())
