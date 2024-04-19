# coding=UTF-8
# __author__ = 'Zheng Zhenjia'

import json
import logging
import functools
import inspect
import os
import time
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import ast
import socket
import requests
from datetime import datetime



def log_config(f_level=logging.INFO, out_path='', filename='app', fix=False, log_type=2):
    logfile = os.path.join(out_path, filename) + '-' + time.strftime('%Y_%m%d_%H%M%S', time.localtime()) + '.log' \
        if not fix else os.path.join(out_path, filename) + '.log'
    if out_path and not os.path.exists(out_path):
        os.makedirs(out_path)
    logger = logging.getLogger('app')
    if logger.handlers:
        for each in logger.handlers:
            logger.removeHandler(each)
    logger.setLevel(f_level)

    rfh = RotatingFileHandler(filename=logfile, maxBytes=1024 * 1024 * 1024, backupCount=10, encoding='utf-8') \
        if log_type == 2 else TimedRotatingFileHandler(filename=logfile, when="D", interval=7, backupCount=10)
    
    ch = logging.StreamHandler()
    
    formatter = logging.Formatter(
        '[%(levelname)s][%(process)d][%(thread)d]--%(asctime)s--[%(filename)s %(funcName)s %(lineno)d]: %(message)s')
    rfh.setLevel(f_level)
    ch.setLevel(logging.DEBUG)
    rfh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(rfh)
    logger.addHandler(ch)

    return logger, logfile


def log_handler(filename=None, level=logging.INFO):
    logger = logging.getLogger(filename)
    logger.handlers.clear()
    logger.setLevel(level)
    fh = RotatingFileHandler(filename, maxBytes=1024 *
                             1024 * 1024, backupCount=50, encoding='utf-8')
    formatter = logging.Formatter(
        '[%(levelname)s][%(process)d][%(thread)d]--%(asctime)s--[%(filename)s %(funcName)s %(lineno)d]: %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


def split_list(_list, n): return [_list[i * n:(i + 1) * n]
                                  for i in range(int((len(_list) + n - 1) / n))]


def serialization_obj(content, encoding='utf-8'):
    try:
        return json.dumps(content, encoding=encoding, ensure_ascii=False, indent=4)
    except Exception as e:
        print(e.__str__())
        return str(content)


def register_dispatch(func):

    registry = {}

    @functools.wraps(func)
    def wrapper(arg0, *args, **kwargs):
        delegate = registry.get(args[0])
        if not delegate:
            return "Function Not register, please check register decorator."
        else:
            return delegate(arg0, **kwargs)

    def register(value):
        def wrap(run_func):
            if value in registry:
                raise ValueError(
                    f"@register_dispatch: there is already a handler registered for {value}"
                )
            registry[value] = run_func
            return run_func
        return wrap

    wrapper.register = register
    return wrapper


def get_dict_from_value(data):
    """
    字符转dict
    :param data:
    :return:
    """
    value = {}
    try:
        value = json.loads(data)
    except Exception as e:
        print(e.__str__())
        try:
            data = data.decode("utf-8") if isinstance(data, bytes) else data
            value = ast.literal_eval(data)
        except Exception as e:
            print(e.__str__())
            value = json.loads(data.replace("false", "False").replace("null", "None").replace("true", "True"))
    return value


def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


def post_result(url, json, **kwargs):
    """
    :param url: 接口请求地址url
    :param json:  请求的参数
    :param kwargs: 其他需要的kwargs
    :return: 请求返回数据
    """
    ret = requests.post(url, json=json, **kwargs)
    return ret


def run_func(cls, func, **kwargs):
    fun = None
    try:
        fun = getattr(cls, func)
    except Exception as e:
        return e.__str__()
    if not fun:
        return ''
    return fun(**kwargs)

def get_funs(cls):
    return [func[0] for func in inspect.getmembers(cls, predicate=inspect.isroutine) 
            if callable(getattr(cls, func[0])) if not func[0].startswith('_')]
        

def compare_time(end, start):
    end_time = datetime.fromisoformat(end.split('+')[0])
    start_time = datetime.fromisoformat(start.split('+')[0])
    return (end_time - start_time).seconds