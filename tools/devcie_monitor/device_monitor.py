#!/usr/bin/python
# -*- coding: UTF-8 -*-

import re
import time
import os
import subprocess
from tools import send_email, SSH


def get_docker_container_id(client, query):
    if isinstance(query, list):
        query = " | grep  ".join(query)
    cmd = f"docker  ps  |  grep  {query}  |  grep  -v  grep |  awk " + "'{print $1}'"
    for _ in range(10):
        docker_data = client.run(cmd)
        try:
            container_id = docker_data[0].replace('\n', '')
            if not container_id:
                time.sleep(10)
                continue
            return container_id
        except Exception as e:
            time.sleep(10)
            continue
    return False


def get_docker_container_status(client, container_id):
    cmd = "docker  inspect --format='{{.State.Status}}' " + container_id
    status_data = client.run(cmd)
    try:
        if not status_data[0] != 'runninng':
            return False, 'Docker is not runnig.'
    except Exception as e:
        return False, e.__str__()
    return True, ''


class Check(object):
    current_query_docker = None
    ssh_client = None

    def check_ssh(cls, **kwargs):
        ssh_ip = kwargs.get('ip')
        ssh_user = kwargs.get('user')
        ssh_password = kwargs.get('password')
        log = kwargs.get('log')
        # ssh_client = None
        print(kwargs)
        # breakpoint()
        try:
            for i in range(10):
                print(f'SSH 连接重试第{i + 1}次')
                cls.ssh_client = SSH(ip=ssh_ip, port=22, user=ssh_user, password=ssh_password, log=log)
                if cls.ssh_client.ssh:
                    log.info(f'SSH 连接重试第{i + 1}次 成功，{cls.ssh_client}')
                    return True
                # ssh重试
                else:
                    time.sleep(10)
            msg = 'SSH 连接重试10间隔10S后仍然无法连接，测试发布警告'
            log.error(msg)
            kwargs.update({'type': 'ssh', 'message': msg})
            send_email(**kwargs)
            return False
        except Exception as e:
            log.error(e.__str__())
            kwargs.update({'type': 'ssh', 'message': e.__str__()})
            send_email(**kwargs)
            return False

    def check_dockers(cls, **kwargs):
        msgs = []
        try:
            for docker_query in kwargs.get('docker_checks'):
                container_id = get_docker_container_id(cls.ssh_client, query=docker_query)
                cls.ssh_client.log.info(f"{docker_query}: {container_id}")
                if not container_id:
                    message = f'SSH grep docker {docker_query} 检查10次，间隔10s仍然找不到对应的容器ID'
                    print(message)
                    cls.ssh_client.log.error(message)
                    msgs.append(message)
                else:
                    cls.ssh_client.log.info(f'结果: SSH grep docker {docker_query}，发现Docker服务起来，正常')
                    running_status, ret_msg = get_docker_container_status(cls.ssh_client, container_id)
                    if not running_status:
                        message = f'结果: SSH 检查Docker服务运行状态，为非running状态，发出警告! {ret_msg}'
                        cls.ssh_client.log.error(message)
                        msgs.append(message)
            if msgs:
                msg = f'\n<br>'.join(msgs)
                kwargs.update({'type': 'docker', 'message': msg})
                send_email(**kwargs)
        except Exception as e:
            kwargs.update(
                {'type': 'ssh', 'message': f'检测docker过程, SSH session not active, 连接阻断! {e.__str__()}'})
            send_email(**kwargs)
            return False
        # finally:
        #     if ssh_client.ssh:
        #         ssh_client.ssh.close()



class DeviceMonitor:

    @staticmethod
    def get_cpu(client):
        p2 = client.run('sar -u 1 10 -p')
        keys = p2[2].split(' ')
        keys = [key.replace('\n', '').replace("%", '') for key in keys if key][-6:]
        averages = p2[-1].split(" ")
        averages = [average.replace('\n', '') for average in averages if average][-6:]
        averages = [round(float(each), 2) for each in averages]
        cpu_result = {key: averages[index] for index, key in enumerate(keys)}
        used_rate = round(100 - cpu_result.get('idle'), 2)
        cpu_result.update({'cpu_used_rate': used_rate})
        return cpu_result

    @staticmethod
    def get_iostat(client):
        data = client.run('sar -d  1 10 -p ')
        keys = []
        values = []
        for each in data:
            mat_k = re.search(".*Average: (?P<keys>.*) DEV$", each)
            if mat_k:
                keys = mat_k.groupdict().get('keys')
            mat_v = re.search(".*Average: (?P<values>.*) mmcblk0$", each)
            if mat_v:
                values = mat_v.groupdict().get('values')
        keys = keys.split(' ')
        keys = [key.replace('\n', '').replace("/", '_').replace("%", '').replace('-', '_') for key in keys if key]
        values = values.split(" ")
        values = [average.replace('\n', '') for average in values if average]
        values = [round(float(each), 2) for each in values]
        io_result = {key: values[index] for index, key in enumerate(keys)}
        io_result.update({'io_used_rate': io_result.get('util'), '_await': io_result.get('await')})
        io_result.pop('util')
        io_result.pop('await')
        return io_result

    @staticmethod
    def get_mem(client):
        # 获取内存使用情况
        data = client.run('sar -r 1 10 -p')
        keys = data[2].split(' ')
        keys = [key.replace('\n', '').replace("%", '') for key in keys if key][1:-2]
        averages = data[-1].split(" ")
        mem = [average.replace('\n', '') for average in averages if average][1:-2]
        mem_result = {}
        for index, key in enumerate(keys):
            if key not in ['memused', 'commit']:
                mem_result.update({f"{key}/MB": round(float(mem[index])/1000, 2)})
            elif key == "memused":
                mem_result.update({f"mem_used_rate": float(mem[index])})
            else:
                mem_result.update({key: float(mem[index])})
        return mem_result

    @staticmethod
    def get_vpp(client):
        vpp_desc_cmd = 'cat /sys/kernel/debug/ion/bm_vpp_heap_dump/summary | head -2'
        p1 = client.run(vpp_desc_cmd)
        summary = p1[1]
        mat = re.search(
            ".* size:(?P<vpp_heap_size>\d+) bytes, used:(?P<vpp_used>\d+) bytesusage rate:(?P<vpp_used_rate>\d+)%, "
            "memory usage peak (?P<vpp_memory_usage_peak>\d+) bytes",
            summary)
        dic = mat.groupdict()
        result = {'vpp_heap_size/MB': int(int(dic.get('vpp_heap_size'))/1000000),
                  'vpp_used/MB': int(int(dic.get('vpp_used'))/1000000),
                  'vpp_memory_usage_peak/MB': int(int(dic.get('vpp_memory_usage_peak'))/1000000),
                  'vpp_used_rate': dic.get('vpp_used_rate')}
        return result

    @staticmethod
    def get_npu(client):
        vpp_desc_cmd = 'cat /sys/kernel/debug/ion/bm_npu_heap_dump/summary | head -2'
        p1 = client.run(vpp_desc_cmd)
        summary = p1[1]
        mat = re.search(
            ".* size:(?P<npu_heap_size>\d+) bytes, used:(?P<npu_used>\d+) bytesusage rate:(?P<npu_used_rate>\d+)%, "
            "memory usage peak (?P<npu_memory_usage_peak>\d+) bytes",
            summary)
        dic = mat.groupdict()
        result = {'npu_heap_size/MB': int(int(dic.get('npu_heap_size'))/1000000),
                  'npu_used/MB': int(int(dic.get('npu_used'))/1000000),
                  'npu_memory_usage_peak/MB': int(int(dic.get('npu_memory_usage_peak'))/1000000),
                  'npu_used_rate': dic.get('npu_used_rate')}
        return result

    @staticmethod
    def get_vpu_info(client):
        vpu_desc_cmd = 'cat /proc/vpuinfo'
        p1 = client.run(vpu_desc_cmd)
        p1 = p1[1:5]
        usage_rate = 0
        for core in p1:
            mat = re.search(
                '.*(instant|long)":/d+%|(?P<vpu_long>\d+)%}.*',
                core)
            usage_rate += float(mat.group('vpu_long'))

        return {'vpu_info_used_rate': usage_rate}

    @staticmethod
    def analyse_device_hardware_data(client, serial, cpu_usage, mem_usage, iostat_usage, vpp_mem_usage, npu_mem_usage,
                                     vpu_info_usage):
        if mem_usage is None:
            mem_usage = {}
        if cpu_usage is None:
            cpu_usage = {}
        if iostat_usage is None:
            iostat_usage = {}
        if vpp_mem_usage is None:
            vpp_mem_usage = {}
        if npu_mem_usage is None:
            npu_mem_usage = {}
        if vpu_info_usage is None:
            vpu_info_usage = {}

        cpu = DeviceMonitor.get_cpu(client)
        mem = DeviceMonitor.get_mem(client)
        iostat = DeviceMonitor.get_iostat(client)
        vpp_mem = DeviceMonitor.get_vpp(client)
        npu_mem = DeviceMonitor.get_npu(client)
        vpu_info = DeviceMonitor.get_vpu_info(client)

        def get_usage(type_data, usage_data):
            for k, v in type_data.items():
                if k not in usage_data:
                    usage_data[k] = [v]
                else:
                    usage_data[k].append(v)
            return usage_data

        serial.append(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        cpu_usage = get_usage(cpu, cpu_usage)
        mem_usage = get_usage(mem, mem_usage)
        iostat_usage = get_usage(iostat, iostat_usage)
        vpp_mem_usage = get_usage(vpp_mem, vpp_mem_usage)
        npu_mem_usage = get_usage(npu_mem, npu_mem_usage)
        vpu_info_usage = get_usage(vpu_info, vpu_info_usage)
        print(serial)
        print(cpu_usage)
        print(mem_usage)
        print(iostat_usage)
        print(vpp_mem_usage)
        print(npu_mem_usage)
        print(vpu_info_usage)
        return serial, cpu_usage, mem_usage, iostat_usage, vpp_mem_usage, npu_mem_usage, vpu_info_usage

    @staticmethod
    def get_x86_cpu(client):
        # sar -u 1 2 获取cpu详情 每一秒采样一次 连续采两次
        cpu_desc_cmd = 'cat /proc/cpuinfo | grep name | cut -f2 -d: | uniq -c'
        p1 = client.run(cpu_desc_cmd)
        desc = p1
        # print(desc)
        p2 = client.run('sar -u 1 2' )
        keys = p2[2].split('   ')[2:]
        averages = p2[-1].split("     ") [2:]
        keys = [each.replace(' ', '').replace('%', '').replace('\n', '') for each in keys]
        averages = [round(float(each.split('\n')[0].split()[0]), 3) for each in averages]
        cpu_result = {key: averages[index] for index, key in enumerate(keys)}
        used_rate = round(100 - averages[-1], 3)
        cpu_result.update({'cpu_used_rate': used_rate})
        return cpu_result

    @staticmethod
    def get_x86_mem(client):
        # 获取内存使用情况
        data = client.run('cat /proc/meminfo')
        keys = [each.split(":")[0] for each in data[:5]]
        mem = [int(each.split()[1]) for each in data[:5]]
        mem_result = {f"{key}/MB": int(mem[index]/1000) for index, key in enumerate(keys)}
        mem_use = mem[0] - mem[1] - mem[3] - mem[4]
        # mem_use = total - free - buffers - cache
        # print(mem[0], mem[1], mem[2], mem[3]) # total, free, av, buffers
        used_rate = round(mem_use * 100 / mem[0], 3)  # 已用多少
        mem_result.update({'mem_used_rate': used_rate})
        # print(mem_result)
        return mem_result

    @staticmethod
    def get_x86_gpu(client):
        # 获取内存使用情况
        data = client.run('nvidia-smi')
        data = ''.join(data)
        all_data = data.split('+-----------------------------------------------------------------------------+\n')
        gpus = all_data[1].split('|===============================+======================+======================|\n')[-1]
        detail_statistics = []
        total_memory_usage = 0
        total_memory_total = 0
        total_gpu_util = 0
        all_gpus = gpus.split('+-------------------------------+----------------------+----------------------+\n')[:-2]
        count = len(all_gpus)
        for i in all_gpus:
            li = i.split('\n')[1].split('|')
            memory_usage = round(float(li[2].split('/')[0].split('MiB')[0]), 3)
            total_memory_usage += memory_usage
            memory_total = round(float(li[2].split('/')[1].split('MiB')[0]), 3)
            total_memory_total += memory_total
            gpu_util = round(float(li[3].split('%')[0].replace(' ', '')), 3)
            total_gpu_util += gpu_util
            item = {'memory_usage': memory_usage, 'gpu_util': gpu_util, 'memory_total': memory_total,
                     "mem_used_rate": round(total_memory_usage * 100 / total_memory_total, 3)}
            detail_statistics.append(item)
        gpu_usage = {f'memory_usage*{count}': total_memory_usage, f'gpu_util*{count}': total_gpu_util, f'memory_total*{count}': total_memory_total, 
                     "gpu_mem_used_rate": round(total_memory_usage * 100 / total_memory_total, 3)}
        return gpu_usage, detail_statistics
        # return {time_stamp: mem_result}

    @staticmethod
    def analyse_x86_device_hardware_data(client, serial, cpu_usage, mem_usage, gpu_usage):
        if gpu_usage is None:
            gpu_usage = {}
        if mem_usage is None:
            mem_usage = {}
        if cpu_usage is None:
            cpu_usage = {}

        cpu = DeviceMonitor.get_x86_cpu(client)
        mem = DeviceMonitor.get_x86_mem(client)
        gpu, _ = DeviceMonitor.get_x86_gpu(client)

        serial.append(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        for k, v in cpu.items():
            if k not in cpu_usage:
                cpu_usage[k] = [v]
            else:
                cpu_usage[k].append(v)
        for k, v in mem.items():
            if k not in mem_usage:
                mem_usage[k] = [v]
            else:
                mem_usage[k].append(v)
        for k, v in gpu.items():
            if k not in gpu_usage:
                gpu_usage[k] = [v]
            else:
                gpu_usage[k].append(v)
        print(serial)
        print(cpu_usage)
        print(mem_usage)
        print(gpu_usage)
        return serial, cpu_usage, mem_usage, gpu_usage

    @staticmethod
    def render_device_monitor_html(serial, data_serial, hw_type='CPU', file_name='GPU.html', py_file='render_cpu.py'):
        serial = [d[5:] for d in serial]
        file_name = file_name.replace('/', os.sep)
        # breakpoint()
        # file_name = os.getcwd() + '\\perf_result\\' + file_name
        y_keys = list(data_serial.keys())
        y_data = list(data_serial.values())
        sep = int(97 / len(y_keys))
        height = int(80 / len(y_keys))
        height_px = 768 * int(len(y_keys) / 2) if len(y_keys) % 2 == 0 else 768 * (int(len(y_keys) / 2) + 1)
        indexs = list([i for i in range(1, len(y_keys) + 1)])

        # Y1 Template
        temp_y1 = """
{y1_key_withoutMB} = (
    Line()
    .add_xaxis(xaxis_data={x_serial})
    .add_yaxis(
        series_name="{y1_key}",
        y_axis={y1_data},
        symbol_size=8,
        is_hover_animation=False,
        label_opts=opts.LabelOpts(is_show=False),
        linestyle_opts=opts.LineStyleOpts(width=1.5),
        is_smooth=True,
    )
    .set_global_opts(
        title_opts=opts.TitleOpts(
            title="Hardware-{hw_type}", subtitle="", pos_left="600px"
        ),
        tooltip_opts=opts.TooltipOpts(trigger="axis"),
        axispointer_opts=opts.AxisPointerOpts(
            is_show=True, link=[{{"xAxisIndex": "all"}}]
        ),
        datazoom_opts=[
            opts.DataZoomOpts(
                is_show=True,
                is_realtime=True,
                start_value=30,
                end_value=70,
                xaxis_index={indexs},
            )
        ],
        xaxis_opts=opts.AxisOpts(
            type_="category",
            boundary_gap=False,
            axisline_opts=opts.AxisLineOpts(is_on_zero=True),
        ),
        yaxis_opts=opts.AxisOpts(max_=500, name="{y1_key}"),
        legend_opts=opts.LegendOpts(pos_left="left"),
        toolbox_opts=opts.ToolboxOpts(
            is_show=True,
            feature={{
                "dataZoom": {{"yAxisIndex": "none"}},
                "restore": {{}},
                "saveAsImage": {{}},
            }},
        ),
    )
)
"""
        # 构建y1的数据line
        y1_line = temp_y1.format(y1_key_withoutMB=y_keys[0].split('/MB')[0], y1_key=y_keys[0], y1_data=y_data[0],
                                 x_serial=serial, hw_type=hw_type, indexs=indexs)

        # Y more template
        temp_y = """
{y1_key_withoutMB} = (
    Line()
    .add_xaxis(xaxis_data={x_serial})
    .add_yaxis(
        series_name="{y_key}",
        y_axis={y_data},
        xaxis_index={index},
        yaxis_index={index},
        symbol_size=8,
        is_hover_animation=False,
        label_opts=opts.LabelOpts(is_show=False),
        linestyle_opts=opts.LineStyleOpts(width=1.5),
        is_smooth=True,
    )
    .set_global_opts(
        axispointer_opts=opts.AxisPointerOpts(
            is_show=True, link=[{{"xAxisIndex": "all"}}]
        ),
        tooltip_opts=opts.TooltipOpts(trigger="axis"),
        xaxis_opts=opts.AxisOpts(
            grid_index={index},
            type_="category",
            boundary_gap=False,
            axisline_opts=opts.AxisLineOpts(is_on_zero=True),
            position="behind",
        ),
        datazoom_opts=[
            opts.DataZoomOpts(
                is_realtime=True,
                type_="inside",
                start_value=30,
                end_value=70,
                xaxis_index={indexs},
            )
        ],
        yaxis_opts=opts.AxisOpts(is_inverse=False, name="{y_key}"),
        legend_opts=opts.LegendOpts(pos_left="{pos_left}%"),
    )
)"""
        y_lines = ''
        for index, v in enumerate(y_data[1:], 1):
            pos_left = 7 * index
            y_lines += temp_y.format(y1_key_withoutMB=y_keys[index].split('/MB')[0], y_key=y_keys[index], y_data=v,
                                     index=index, x_serial=serial, indexs=indexs, pos_left=pos_left)

        temp_grid = """
    .add(
        chart={y_key},
        grid_opts=opts.GridOpts(pos_left=50, pos_right=50, pos_top="{pos_top}%", height="{height}%"),
    )
        """
        grids = ''
        for index, key in enumerate(y_keys[1:], 1):
            pos_top = sep * index + 4
            grids += temp_grid.format(y_key=key.split('/MB')[0], pos_top=pos_top, height=height)

        temp = """
# -*- coding: utf-8 -*-

import os
import pyecharts.options as opts
from pyecharts.charts import Line, Grid

perf_result_path = os.path.join(os.getcwd(), 'report/perf_result')
if not os.path.exists(perf_result_path):
    os.makedirs(perf_result_path)

{y1_line}
{y_lines}

(
    Grid(init_opts=opts.InitOpts(width="1024px", height="{height_px}px"))
    .add(chart={y1_key}, grid_opts=opts.GridOpts(pos_left=50, pos_right=50, height="{height}%"))
    {grid}
    .render(os.path.join(perf_result_path, '{file_name}'))
)
"""

        temp = temp.format(y1_line=y1_line, y_lines=y_lines, y1_key=y_keys[0].split('/MB')[0], grid=grids, height=height,
                           height_px=height_px, file_name=file_name)
        # print(temp)
        with open(py_file, 'w') as py:
            py.write(temp)

    @staticmethod
    def get_serial_data_render(serial, data_serial, hw_type, file_name='usage.html'):
        py_file = "render_temp.py"
        DeviceMonitor.render_device_monitor_html(serial=serial, data_serial=data_serial, hw_type=hw_type,
                                                 file_name=file_name, py_file=py_file)
        cmd = f'poetry run python {py_file} && rm -f {py_file}'
        print(cmd)
        status, ret = subprocess.getstatusoutput(cmd)
        print(status)
        print(ret)

    @staticmethod
    def gene_device_usage_html(serial, cpu_usage, mem_usage, iostat_usage, vpp_mem_usage, npu_mem_usage, vpu_info_usage,
                               access_limit_key=None):

        data_dict = {'CPU': cpu_usage, 'Mem': mem_usage, 'VPP-Mem': vpp_mem_usage, 'IOStat': iostat_usage,
                     'NPU-Mem': npu_mem_usage, 'VPU-Info': vpu_info_usage}
        if access_limit_key:
            data_dict = {access_limit_key: data_dict.get(access_limit_key)}
        filenames = []
        for key, value in data_dict.items():
            if not value:
                continue
            filename = f'{key}-{time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())}.html' \
                if not access_limit_key else \
                f'Warning_BMDevice_{key}_AccessLimit-{time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())}.html'
            DeviceMonitor.get_serial_data_render(serial, data_serial=value, hw_type=key, file_name=filename)
            filenames.append(filename)
        return filenames

    @staticmethod
    def gene_x86_device_usage_html(serial, cpu_usage, mem_usage, gpu_usage, access_limit_key=None):
        data_dict = {'CPU': cpu_usage, 'Mem': mem_usage, 'GPU-Mem': gpu_usage}
        if access_limit_key:
            data_dict = {access_limit_key: data_dict.get(access_limit_key)}
        filenames = []
        for key, value in data_dict.items():
            if not value:
                continue
            filename = f'{key}-{time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())}.html' \
                if not access_limit_key else \
                f'Warning_X86Device_{key}_AccessLimit-{time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())}.html'
            DeviceMonitor.get_serial_data_render(serial, data_serial=value, hw_type=key, file_name=filename)
            filenames.append(filename)
        return filenames

