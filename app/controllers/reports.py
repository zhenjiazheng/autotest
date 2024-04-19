# -*- coding: utf-8 -*-
# Import flask dependencies

from flask import Blueprint, request, Response
from app.app import return_result
from gun import home
from app.dbs.common import Reports
import os


mod_reports = Blueprint('reports', __name__, url_prefix='/autotest')


@mod_reports.route("/report/<path:report_name>", methods=['GET'])
def report_view(report_name):
    """
    @api {get} /autotest/task/{report_name}  任务状态
    @apiVersion 1.0.0
    @apiName task_status
    @apiGroup tasks
    @apiParam {int}  pipeline_id    (必须)    pipeline_id + job_id
    @apiParamExample {json} Request-Example:
        {
            "report_name": "111111_22222"
        }
    @apiSuccess (回参) {string}   data          Status
    @apiSuccessExample {json} Success-Response:
        Response Data
    """
    ext = {
        "jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
        "gif": "image/gif", "webp": "image/webp", "cr2": "image/x-canon-cr2",
        "tiff": "image/tiff", "bmp": "image/bmp", "jxr": "image/vnd.ms-photo",
        "psd": "image/vnd.adobe.photoshop", "ico": "image/x-icon", "epub": "application/epub+zip",
        "zip": "application/zip", "tar": "application/x-tar", "rar": "application/x-rar-compressed",
        "pdf": "application/pdf", "doc": "application/msword", "rtf": "application/rtf",
        "html": "text/html", "htm": "text/html", "stm": "text/html",
        "xlsx": "application/vnd.ms-excel", "xls": "application/vnd.ms-excel", "css": "text/css"
    }
    mine = report_name.split(".")[-1]
    minetype = "text/plain"
    if mine in list(ext.keys()):
        minetype = ext[mine]
    # print(minetype)
    report_allpath = os.path.join(home, 'report', report_name)
    if not os.path.exists(report_allpath):
        return return_result(code=3, msg="Report Not Exists")
    response = Response(open(report_allpath, "rb").read(), mimetype=minetype)
    return response


@mod_reports.route("/report/link", methods=['POST'])
def get_report_link():
    task_ids = request.json.get("task_ids")
    reports = Reports.query.filter(Reports.task_id.in_(task_ids)).all()
    urls = list(set([item.url for item in reports]))
    data = {'urls': urls}
    return return_result(data=data)
