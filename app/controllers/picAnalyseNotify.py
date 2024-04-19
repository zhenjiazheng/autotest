from flask import Blueprint, request
from app.app import return_result, redis_store, logger
from app.services.keys import *
from utils import compare_time
import json


callback_notify_app = Blueprint('callback_notify_app', __name__, url_prefix='')
        

@callback_notify_app.route('/picAnalyseRetNotify', methods=['POST'])
def picAnalyseRetNotify():  
    data = request.get_json()
    print(data)
    # data = json.dumps(data) if isinstance(data, dict) else data
    logger.info(f"\nGet Latest Data from service under test: {data}\n")
    request_id = data.get('requestId', 'default')
    logger.info(f"request_id Id : {request_id}\n")
    redis_store.set(f'{PicAnalyseKey.pic_analyse_key}:{request_id}', json.dumps(data))
    return return_result(data=data)


@callback_notify_app.route('/picAnalyseRetNotify/getDataWithRequestId', methods=['POST'])
def getPicAnalyseRetNotifyData():  
    data = request.get_json()
    request_id = data.get('requestId', 'default')
    logger.info(f"\nGet Latest Data from service under test: {data}\n")
    request_id = data.get('requestId', 'default')
    logger.info(f"request_id Id : {request_id}\n")
    data = redis_store.get(f'{PicAnalyseKey.pic_analyse_key}:{request_id}')
    # print(data)
    data = json.loads(redis_store.get(f'{PicAnalyseKey.pic_analyse_key}:{request_id}') or '{}')
    return return_result(data=data)
