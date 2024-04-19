#!/usr/bin/env python
# encoding: utf-8
"""
@author: Zhengzhenjia
@desc:
"""
from app.app import db_handler, config
from app.dbs.common import Tasks
# from config import Config
import subprocess
import os


ldap_user = config[os.getenv('MODE', 'dev')].LDAP_USER
ldap_pass = config[os.getenv('MODE', 'dev')].LDAP_PASS
registry = config[os.getenv('MODE', 'dev')].REGISTRY

@db_handler
def create_docker(prj, image, name, log, location=None, mark=None, env=None, vol=None, command=None, **kwargs):
    """
        作用: 运行docker
                prj_name=None,
        参数: docker_name为容器的名称
        返回：容器对象
    """
    if not env:
        env = {}
    if not vol:
        vol = {}
    run_status = 2
    try:
        if command is None:
            command = f'pytest -s -v --disable-warnings {location}' \
                if location is not None else 'pytest -s -v --disable-warnings tests'
            command = command + f" -m {mark}" if mark is not None else command
            print(command)
        
        cmd = f"docker login {registry} -u {ldap_user} -p {ldap_pass} " \
              f"&& rm -f {log} && docker run --rm --pull missing --name {name}"
        for k, v in env.items():
            cmd = cmd + f' -e {k}={v}'
        for k, v in vol.items():
            cmd = cmd + f' -v {k}:{v}'
        cmd = f"{cmd} {image}  {command} >> {log}"
        print(cmd)
        status, ret = subprocess.getstatusoutput(cmd)
        print(status)
        if status != 1:
            run_status = 3
    except Exception as e:
        print(e.__str__())
        run_status = 3
    finally:
        session = kwargs.pop("sess")
        with session.no_autoflush:
            task = session.query(Tasks).filter_by(pipeline_id=name).first()
            task.status = run_status # 3代表异常
            task.report = ''
            session.commit()
