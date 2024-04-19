#!/usr/bin/env python
# encoding: utf-8
"""
@author: Zhengzhenjia
@desc:
"""

from billiard.exceptions import WorkerLostError
from app.app import celery, redis_store
from app.services.tools import Tools
from app.services.tasks import create_docker


@celery.task(bind=True, autoretry_for=(WorkerLostError,), name="run_tool_task", max_retries=15)
def run_tool_task(self, record_id, device, run_config, validate, limit_rate, mail):
    """
    执行任务的celery入口函数
    :param record_id:
    :param device:
    :param run_config:
    :param validate:
    :param limit_rate:
    :param mail:
    :return:
    """
    print(record_id)
    task_params = dict(device=device, run_config=run_config,
                       validate=validate, limit_rate=limit_rate, mail=mail, record_id=record_id)
    if device.get('type') == 'BM':
        Tools.gene_hw_report_stat_bm(**task_params)
    elif device.get('type') == 'X86':
        Tools.gene_hw_report_stat_x86(**task_params)
    self.update_state(state="SUCCESS")


@celery.task(bind=True, autoretry_for=(WorkerLostError,), name="run_ci_task", max_retries=15)
def run_ci_task(self, prj, image, name, log, location=None, mark=None, env=None, vol=None, command=None):
    """
    执行任务的celery入口函数
    :param self:
    :param prj:
    :param image:
    :param name:
    :param log:
    :param location:
    :param mark:
    :param env:
    :param vol:
    :param command:
    :return:
    """
    create_docker(prj, image, name, log, location=location, mark=mark, env=env, vol=vol, command=command)
    self.update_state(state="SUCCESS")


@celery.task(bind=True, autoretry_for=(WorkerLostError,), name="monitor_socket", max_retries=15)
def run_monitor_socket_transfer(self, data):
    print(data)
    redis_store.set('b_protocol', data)
    station_data = redis_store.get('b_protocol:station_params')
    res = Tools.response_for_req_data(data, station_data)
    print(res)
    return True