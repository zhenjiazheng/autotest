#!/usr/bin/env python
# encoding: utf-8
"""
@author: Zhengzhenjia
@desc:
"""

import os
import traceback
from functools import wraps
from flask import Flask, request, g, make_response, jsonify
from flask_apidoc import ApiDoc
from flask_cors import *
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker
from flask_redis import FlaskRedis
from celery import Celery
from sqlalchemy.ext.declarative import DeclarativeMeta
from urllib import parse
import json
from config import config
from utils import log_config
from gun import home
from tools import open_sock
import threading


class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                try:
                    json.dumps(data)
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            # a json-encodable dict
            return fields
        return json.JSONEncoder.default(self, obj)


def return_result(code=0, msg='success', show_type=0, data={}, **kwargs):
    success = True
    if code != 0:
        show_type = 2
        success = False
    res = dict(code=code, msg=msg, data=data, success=success, showType=show_type, **kwargs)
    return jsonify(res)


db = SQLAlchemy(use_native_unicode="utf8")
# uploaded_photos = UploadSet()
redis_store = FlaskRedis()

celery = Celery()

logger, _ = log_config(filename='logs/app', fix=True)

report_folder_path = os.path.join(home, 'report')

platform_ip = config[os.getenv('MODE', 'dev')].PLATFORM_IP
platform_port = int(config[os.getenv('MODE', 'dev')].PLATFORM_PORT)
socket_wait = config[os.getenv('MODE', 'dev')].SOCKET_TIMEOUT
task_queue = config[os.getenv('MODE', 'dev')].TASKQUEEN

res, sock = open_sock(platform_ip, platform_port, socket_wait)
if not res:
    logger.error(sock)

DB_ENGINE = create_engine(
    config[os.getenv('MODE', 'dev')].SQLALCHEMY_DATABASE_URI,
    echo=False,
    pool_recycle=100,
    pool_size=50,
    max_overflow=0,
    encoding='utf-8')

SESS = sessionmaker(bind=DB_ENGINE)


def db_handler(function):
    """Wrap a database handle function."""

    @wraps(function)
    def wrapper(*args, **kwargs):
        """Function that wrapped."""

        session = SESS()
        try:
            res = function(sess=session, *args, **kwargs)
            return res
        except exc.IntegrityError as exception:
            res = dict(code=3, msg=str(exception.orig))
            return res
        except exc.ProgrammingError as exception:
            res = dict(code=3, msg=str(exception.orig))
            return res
        except exc.ResourceClosedError as exception:
            res = dict(code=3, msg=str(exception))
            return res
        except exc.OperationalError as exception:
            res = dict(code=3, msg=str(exception.orig))
            return res
        except UnicodeEncodeError as exception:
            res = dict(code=3, msg=str(exception))
            return res
        except Exception as e:
            print(e.__str__())
            traceback.print_exc()
            print('=' * 80, '/n/n')
            res = dict(
                code=3, msg='Unknown Error.'
            )
            return res
        finally:
            try:
                session.close()
            except Exception as e:
                logger.error(e.__str__())

    return wrapper


# monkey.patch_all()

async_mode = 'gevent'
application = None

def init_celery(app, celery_instance):
    """Add flask app context to celery.Task"""
    task_base = celery_instance.Task

    class ContextTask(task_base):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return task_base.__call__(self, *args, **kwargs)

    celery_instance.Task = ContextTask
    return celery_instance


def create_app(conf):
    global logger, db, celery, application, redis_store, sock
    application = Flask(__name__)


    ApiDoc(app=application)
    application.config.from_object(config[conf])
    application.config["mode"] = conf
    # configure_uploads(application, uploaded_photos)
    application.json_encoder = AlchemyEncoder
    db.init_app(app=application)

    celery = Celery(application.import_name, broker=application.config['CELERY_BROKER_URL'],
                    backend=application.config['CELERY_BROKER_URL'])
    init_celery(app=application, celery_instance=celery)
    redis_store.init_app(application)



    @application.before_request
    def before_request_func():
        path = parse.urlparse(request.url)
        if any(["/autotest/internal" in path.path, 
                "/autotest/report/" in path.path, 
                "/autotest/tools/" in path.path,
                "/autotest/hooks/" in path.path,
                "/autotest/llm/" in path.path,
                "/picAnalyseRetNotify" in path.path,
                path.path in config[os.getenv('MODE', 'dev')].URI_WHITE_LIST]):
            return
        if request.headers.get('ignore'):
            return
        if not request.headers.get('token'):
            return return_result(code=401, msg="Missing Token")
        if request.headers.get('token') == 'undefined' and 'logout' in path.path:
            return return_result()
        token_key = f"token:{request.headers.get('token')}"
        token_value = redis_store.get(token_key)
        if not token_value:
            return return_result(code=401, msg="Login Expired")
        
        redis_store.expire(f"token:{request.headers.get('token')}", config[os.getenv('MODE', 'dev')].TOKEN_TIMEOUT)
        g.user_data = json.loads(token_value)


    @application.after_request
    def after_request_func(response):
        # origin = request.headers.get('Origin')
        if request.method == 'OPTIONS':
            response = make_response()
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
            response.headers.add('Access-Control-Allow-Headers', 'x-csrf-token')
            response.headers.add('Access-Control-Allow-Headers', 'Token')
            response.headers.add('Access-Control-Allow-Methods',
                                'GET, POST, OPTIONS, PUT, PATCH, DELETE')
        else:
            response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Origin', '*')

        return response

    from app.controllers import mod_project, mod_tasks, result_collect, mod_reports, mod_tools, mod_users, hook_app, llm_hook, callback_notify_app
    bp_list = [mod_project, mod_tasks, result_collect, mod_tools, mod_reports, mod_users, hook_app, llm_hook, callback_notify_app]
    for item in bp_list:
        application.register_blueprint(item)
    # CORS(application, supports_credentials=True)
    # cors = CORS(application, resource={
    #     r"/*":{
    #         "origins":"*"
    #     }
    # })

    def monitor_sip_data_start_next_flow(task_queue):
        global sock
        from .celery_register.register import run_monitor_socket_transfer
        from tools import listen_sock
        for data in listen_sock(sock):
            run_monitor_socket_transfer.apply_async(([data]), queue=task_queue)

    # 后台启动socket
    task_queue = config[os.getenv('MODE', 'dev')].TASKQUEEN
    # listen_socket(platform_ip, platform_port, socket_wait, task_queue)
    th = threading.Thread(target=monitor_sip_data_start_next_flow, args=(task_queue,))
    th.start()

    return application
