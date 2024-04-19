#!/usr/bin/env python
# encoding: utf-8

import time
import datetime
import json
from utils import log_config, get_funs
from tools import send_email, DeviceMonitor, Check, iec104_test
from app.app import redis_store, logger, sock
from config import config
import os
from tools.sipping.sipping import Request, Response, b_protocol_data_send


platform_ip = config[os.getenv('MODE', 'dev')].PLATFORM_IP
platform_port = config[os.getenv('MODE', 'dev')].PLATFORM_PORT
platform_code = config[os.getenv('MODE', 'dev')].PLATFORM_CODE
station_cam_code = config[os.getenv('MODE', 'dev')].STATION_CAM_CODE


class Tools:

    def __init__(self):
        self.__get_funs()
            
    def __get_funs(cls):
        cls.funcs = get_funs(cls)

    @staticmethod
    def gene_hw_report_stat_bm(record_id, device, run_config, validate, limit_rate, mail):
        ssh_ip = device.get('ssh_ip')
        ssh_user = device.get('ssh_user')
        ssh_password = device.get('ssh_password')
        run_duration = run_config.get('run_duration')
        docker_checks = validate.get('docker_checks')
        notify = run_config.get('notify')
        log, _ = log_config(filename=f'logs/hw_monitor_check_{ssh_ip.replace(".", "_")}', fix=True)
        kwargs = dict(ip=ssh_ip, user=ssh_user, password=ssh_password,
                      docker_checks=docker_checks, mail_to=mail, log=log)
        start = time.time()
        serial, cpu_usage, mem_usage, iostat_usage, vpp_mem_usage, npu_mem_usage, \
            vpu_info_usage = [], {}, {}, {}, {}, {}, {}
        cpu_warn_count, mem_warn_count, iostat_warn_count, vpp_warn_count, npu_warn_count, \
            vpu_info_warn_count = 0, 0, 0, 0, 0, 0
        check = None
        try:
            while True:
                time.sleep(10)
                try:
                    check = Check()
                    if not check.check_ssh(**kwargs):
                        return
                    if docker_checks:
                        check.check_dockers(**kwargs)
                    serial, cpu_usage, mem_usage, iostat_usage, vpp_mem_usage, npu_mem_usage, vpu_info_usage = \
                        DeviceMonitor.analyse_device_hardware_data(
                            check.ssh_client, serial, cpu_usage=cpu_usage, mem_usage=mem_usage, iostat_usage=iostat_usage,
                            vpp_mem_usage=vpp_mem_usage, npu_mem_usage=npu_mem_usage, vpu_info_usage=vpu_info_usage)
                    warn_list = []
                    # access_limit_key = ['CPU', 'Mem', 'VPP-Mem', 'NPU-Mem', 'VPU-Info'] 其中一种
                    if int(cpu_usage.get('cpu_used_rate')[-1]) > int(limit_rate.get('cpu_used_rate')):
                        cpu_warn_count += 1
                        warn_list.append({'hw_type': 'CPU',
                                          'limit_value': f"{limit_rate.get('cpu_used_rate')}%",
                                          'type': 'hw', 'count': cpu_warn_count})
                    else:
                        cpu_warn_count = 0
                    if int(mem_usage.get('mem_used_rate')[-1]) > int(limit_rate.get('mem_used_rate')):
                        mem_warn_count += 1
                        warn_list.append({'hw_type': 'Mem',
                                          'limit_value': f"{limit_rate.get('mem_used_rate')}%",
                                          'type': 'hw', 'count': mem_warn_count})
                    else:
                        mem_warn_count = 0
                    if int(iostat_usage.get('io_used_rate')[-1]) > int(limit_rate.get('io_used_rate')):
                        iostat_warn_count += 1
                        warn_list.append({'hw_type': 'IOStat',
                                          'limit_value': f"{limit_rate.get('io_used_rate')}%",
                                          'type': 'hw', 'count': iostat_warn_count})
                    else:
                        iostat_warn_count = 0

                    if int(vpp_mem_usage.get('vpp_used_rate')[-1]) > int(limit_rate.get('vpp_used_rate')):
                        vpp_warn_count += 1
                        warn_list.append({'hw_type': 'VPP-MEM',
                                          'limit_value': f"{limit_rate.get('vpp_used_rate')}%",
                                          'type': 'hw', 'count': vpp_warn_count})
                    else:
                        vpp_warn_count = 0
                    if int(npu_mem_usage.get('npu_used_rate')[-1]) > int(limit_rate.get('npu_used_rate')):
                        npu_warn_count += 1
                        warn_list.append({'hw_type': 'NPU-Mem',
                                          'limit_value': f"{limit_rate.get('npu_used_rate')}%",
                                          'type': 'hw', 'count': npu_warn_count})
                    else:
                        npu_warn_count = 0
                    if int(vpu_info_usage.get('vpu_info_used_rate')[-1]) > \
                            int(limit_rate.get('vpu_info_used_rate')):
                        vpu_info_warn_count += 1
                        warn_list.append({'hw_type': 'VPU-Info', 'limit_value': f"{limit_rate.get('vpu_info_used_rate')}%",
                                          'type': 'hw', 'count': vpu_info_warn_count})
                    else:
                        vpu_info_warn_count = 0
                    for warn in warn_list:
                        if warn.get('count') > int(notify):
                            filenames = DeviceMonitor.gene_device_usage_html(
                                serial, cpu_usage, iostat_usage, mem_usage, vpp_mem_usage,
                                npu_mem_usage, vpu_info_usage, access_limit_key=warn.get('hw_type'))
                            warn.update({'hw_charts': filenames[0]})
                            kwargs.update(warn)
                            if not serial:
                                send_email(**kwargs)
                            cpu_warn_count, mem_warn_count, iostat_warn_count, vpp_warn_count, npu_warn_count, \
                                vpu_info_warn_count = 0, 0, 0, 0, 0, 0
                    duration = time.time() - start
                    if duration > int(run_duration):
                        break
                    if redis_store.get(f'run_tool_task:{record_id}'):
                        log.info("发现主动停止硬件监控任务，执行停止操作")
                        break
                finally:
                    if check.ssh_client.ssh:
                        check.ssh_client.ssh.close()
                        log.info(f"释放SSH链接: {check.ssh_client}")
        # 以下为生成硬件资源的使用情况状况
        finally:
            if not serial:
                return
            filenames = DeviceMonitor.gene_device_usage_html(serial, cpu_usage, mem_usage, iostat_usage,
                                                             vpp_mem_usage, npu_mem_usage, vpu_info_usage)
            kwargs.update({'charts': filenames, 'type': 'report'})
            send_email(**kwargs)

    @staticmethod
    def gene_hw_report_stat_x86(record_id, device, run_config, validate, limit_rate, mail):
        ssh_ip = device.get('ssh_ip')
        ssh_user = device.get('ssh_user')
        ssh_password = device.get('ssh_password')
        run_duration = run_config.get('run_duration')
        notify = run_config.get('notify')
        docker_checks = validate.get('docker_checks')
        log, _ = log_config(filename=f'logs/hw_monitor_check_{ssh_ip.replace(".", "_")}', fix=True)
        kwargs = dict(ip=ssh_ip, user=ssh_user, password=ssh_password,
                      docker_checks=docker_checks, mail_to=mail, log=log)
        start = time.time()
        serial, cpu_usage, mem_usage, gpu_usage = [], {}, {}, {}
        log, _ = log_config(filename='logs/x86_hw_analysis', fix=True)
        cpu_warn_count, mem_warn_count, gpu_warn_count = 0, 0, 0
        check = None
        try:
            while True:
                time.sleep(5)
                try:
                    check = Check()
                    if not check.check_ssh(**kwargs):
                        break
                    if docker_checks:
                        check.check_dockers(**kwargs)
                    serial, cpu_usage, mem_usage, gpu_usage = \
                        DeviceMonitor.analyse_x86_device_hardware_data(
                            check.ssh_client, serial, cpu_usage=cpu_usage, mem_usage=mem_usage, gpu_usage=gpu_usage)
                    warn_list = []
                    # access_limit_key = ['CPU', 'Mem', 'VPP-Mem', 'NPU-Mem', 'VPU-Info'] 其中一种
                    if int(cpu_usage.get('cpu_used_rate')[-1]) > int(limit_rate.get('cpu_used_rate')):
                        cpu_warn_count += 1
                        warn_list.append({'hw_type': 'CPU',
                                          'limit_value': f"{limit_rate.get('cpu_used_rate')}%",
                                          'type': 'hw', 'count': cpu_warn_count})
                    else:
                        cpu_warn_count = 0
                    if int(mem_usage.get('mem_used_rate')[-1]) > int(limit_rate.get('mem_used_rate')):
                        mem_warn_count += 1
                        warn_list.append({'hw_type': 'Mem',
                                          'limit_value': f"{limit_rate.get('mem_used_rate')}%",
                                          'type': 'hw', 'count': mem_warn_count})
                    else:
                        mem_warn_count = 0
                    if int(gpu_usage.get('gpu_mem_used_rate')[-1]) > int(limit_rate.get('gpu_mem_used_rate')):
                        gpu_warn_count += 1
                        warn_list.append({'hw_type': 'GPU-Mem',
                                          'limit_value': f"{limit_rate.get('gpu_mem_used_rate')}%",
                                          'type': 'hw', 'count': gpu_warn_count})
                    else:
                        gpu_warn_count = 0
                    for warn in warn_list:
                        if warn.get('count') > int(notify):
                            filenames = DeviceMonitor.gene_x86_device_usage_html(
                                serial, cpu_usage, mem_usage, gpu_usage, access_limit_key=warn.get('hw_type'))
                            warn.update({'hw_charts': filenames[0]})
                            kwargs.update(warn)
                            if not serial:
                                send_email(**kwargs)
                            cpu_warn_count, mem_warn_count, gpu_warn_count = 0, 0, 0
                    duration = time.time() - start
                    if duration > int(run_duration):
                        break
                    if redis_store.get(f'run_tool_task:{record_id}'):
                        log.info("发现主动停止硬件监控任务，执行停止操作")
                        break
                finally:
                    if check.ssh_client.ssh:
                        check.ssh_client.ssh.close()
                        log.info(f"释放SSH链接: {check.ssh_client}")
        # 以下为生成硬件资源的使用情况状况
        finally:
            if not serial:
                return
            filenames = DeviceMonitor.gene_x86_device_usage_html(serial, cpu_usage, mem_usage, gpu_usage)
            kwargs.update({'charts': filenames, 'type': 'report'})
            send_email(**kwargs)

    @staticmethod
    def iec104_sender(dst_ip, dst_port, typ=31, vsq=1, cot=3, info_addr=2336, status='11'):
        error, data, message = iec104_test(logger, (dst_ip, dst_port), typ=typ, date=datetime.datetime.now(), 
                                           vsq=vsq, cot=cot, info_addr=info_addr, status=status)
        return error, data, message

    @staticmethod
    def response_for_req_data(data, station_data):
        logger.info(f"B protocol Receive: {data}")
        try:
            station_resp = False
            resp_func = ''
            try:
                message = Request(data)
            except Exception as e:
                message = Response(data)
            if hasattr(message, 'method'):
                station_resp = True

            if station_resp:
                if message.method == 'REGISTER':
                    authorization = message.headers.get('authorization', '')
                    if authorization:
                        if '1' not in message.headers.get('cseq', ''):
                            resp_func = 'register'
                        else:
                            resp_func = 'register_auth'
            else:
                if 'NOTIFY' in message.headers.get('cseq', '') and message.headers.get('content-length', 0) > 0:
                    resp_func = 'notify'
            if resp_func:
                Tools.b_protocol_send(resp_func, message.__dict__, station_data, True)
        except Exception as e:
            print(e.__str__())

    @staticmethod
    def b_protocol_send(func, message, station_data, redirect=False):
        tsf = SIPMessageTrasfer()
        record_id = station_data.get('record_id')
        result_redis_key = f'b_protocol:recv:{record_id}'
        data = getattr(tsf, func)(message, station_data, redirect)
        if isinstance(data, bytes):
            data = str(getattr(tsf, func)(message, station_data, redirect), 'utf-8')
        redis_store.set(result_redis_key, json.dumps(data))
        return data
        
class SIPMessageTrasfer():

    def __init__(self) -> None:
        pass

    def register(self, message, station_data, redirect=False):
        print(message)
        logger.info('register')
        if redirect:
            b_from = message.get('headers').get('from').split(";")[0]
            station_code = b_from.split("@")[0].split(':')[-1]
            station_ip = b_from.split("@")[-1].split(':')[0]
            station_port = int(b_from.split(":")[-1].split('>')[0])
            call_id = message.get('headers').get('call-id') 
            cseq = message.get('headers').get('cseq')
            www_authenticate = message.get('headers').get('www-authenticate')
            authorization = message.get('headers').get('authorization')
            expires = message.get('headers').get('expires') or station_data.get('expires')
            b_data = message.get('data')
            body = message.get('body')
        else:
            station_code = station_data.get('station_code')
            station_ip = station_data.get('station_ip')
            station_port = station_data.get('station_port')
        station_cam_code = station_data.get('station_cam_code')
        
        kwargs = {"platform_ip": platform_ip, "platform_port": platform_port, "platform_code": platform_code, 
                "sip_auth_password":"12345", "station_code": station_code, 
                "station_cam_code":station_cam_code, "station_ip": station_ip, "station_port":station_port,
                "count": 1, "func": 'register', "index":1, "start":0, "end":1, 'from_side': 'platform'}
        for data in b_protocol_data_send(sock=sock, dest=(station_ip, station_port), wait=1, **kwargs):
            logger.info(f'B protocol Send: {data}')
            return data

    def register_auth(self, message):
        pass
        logger.info('test_register_auth')

    def notify(self, message):
        pass
        logger.info('test_notify')