from flask import Blueprint, request
from app.app import return_result, redis_store, logger
from app.services.keys import *
from utils import compare_time
import json


hook_app = Blueprint('hook_api', __name__, url_prefix='/autotest')
        


@hook_app.route('/hooks/nanwang/task', methods=['POST'])
def nanwang_task_callback_uri():  
    data = request.get_json()
    print(data)
    # data = json.dumps(data) if isinstance(data, dict) else data
    logger.info(f"\nGet Latest Data from test service: {data}\n")
    task_id = data.get('task_id', 'callback')
    logger.info(f"\nTask Id : {task_id}\n")
    task_callback_data = json.loads(redis_store.get(f'{NanwangKey.nw_callback_store_key}:{task_id}') or '[]')
    task_callback_data.append(data)
    redis_store.set(f'{NanwangKey.nw_callback_store_key}:{task_id}', json.dumps(task_callback_data))
    return return_result(data=data)


@hook_app.route('/hooks/nanwang/task/stage_data', methods=['POST'])
def nanwang_task_store_data():  
    data = request.get_json()
    task_id = data.get('task_id', 'callback')
    # print(task_id)
    task_callback_data = json.loads(redis_store.get(f'{NanwangKey.nw_callback_store_key}:{task_id}') or '[]')
    logger.info(f"\nQuery Data from cache with Task id : {task_id}, Value is : {task_callback_data}\n")
    if task_callback_data:
        status = task_callback_data[-1].get('status', 20)
        logger.info(f"Current Task Status: {status}")
    return return_result(data=task_callback_data)


@hook_app.route('/hooks/nanwang/task/stage_efficiency', methods=['POST'])
def nanwang_task_stage_efficiency():  
    data = request.get_json()
    task_ids = data.get('task_ids', [])

    def get_stage_run_duration(stage_data_list):
        stage_efficiency = {}
        for data in stage_data_list:
            stage = data.get('stage')
            if stage in stage_efficiency:
                stage_efficiency[stage].append(data.get('timestamp'))
            else:
                stage_efficiency[stage] = [data.get('timestamp')]
            sorted(stage_efficiency[stage])
            if len(stage_efficiency[stage]) == 2:
                duration = compare_time(stage_efficiency[stage][1], stage_efficiency[stage][0])
                stage_efficiency[stage] = duration
        return stage_efficiency
    
    efficiency_data_list = []

    for task_id in task_ids:
        efficiency_data = json.loads(redis_store.get(f'{NanwangKey.nw_callback_store_key}:{task_id}') or '[]')
        performance_data = get_stage_run_duration(efficiency_data)
        efficiency_data_list.append({task_id: performance_data})
        logger.info(f"\nGet Stage Efficiency Result with TaskId: {task_id}\n")
        logger.info(f"\nTask Id : {task_id}\n")

    logger.info(f"\nPerformance Result:\n{efficiency_data_list}")
    return return_result(data=efficiency_data_list)


@hook_app.route('/hooks/nanwang/task/clear', methods=['POST'])
def nanwang_task_stage_efficiency_clear():  
    data = request.get_json()
    task_id = data.get('task_id')
    logger.info(f"\nTask Id : {task_id}\n")
    if redis_store.exists(f'{NanwangKey.nw_callback_store_key}:{task_id}'):
        redis_store.delete(f'{NanwangKey.nw_callback_store_key}:{task_id}')
    if redis_store.exists(f'{NanwangKey.nw_callback_run_result_key}:{task_id}'):
        redis_store.delete(f'{NanwangKey.nw_callback_run_result_key}:{task_id}')
    return return_result()


@hook_app.route('/hooks/nanwang/task/result', methods=['POST'])
def nanwang_task_task_result():  
    data = request.get_json()
    logger.info(f"\nGet Performance Result from  performance test result: {data.get('data')}\n")
    task_id = data.get('data').get('task_id')
    logger.info(f"\nTask Id : {task_id}\n")
    task_result_data = json.loads(redis_store.get(f'{NanwangKey.nw_callback_run_result_key}:{task_id}') or '[]')
    task_result_data.append(data.get('data'))
    redis_store.set(f'{NanwangKey.nw_callback_run_result_key}:{task_id}', json.dumps(task_result_data))
    logger.info(f"\nPerformance Result:\n{task_result_data}")
    return return_result(data=task_result_data)
