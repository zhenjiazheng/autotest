from flask import Blueprint, request
from app.app import return_result, logger
from llm_integration.nova import *


llm_hook = Blueprint('llm', __name__, url_prefix='/autotest')
        

llm_api = CVLM_LLM_FLM

@llm_hook.route('/llm/models', methods=['GET'])
def llm_models():  
    type = request.values.get('type','nova')
    if type != 'nova':
        return return_result(msg=f'{type} not integration.')
    ret = llm_api.models()
    # data = json.dumps(data) if isinstance(data, dict) else data
    logger.info(f"\nGet Latest Models list: {ret.json()}\n")
    return return_result(data=ret.json().get('data'))

@llm_hook.route('/llm/models/detail', methods=['GET'])
def llm_models_detail():  
    type = request.values.get('type','nova')
    model_id = request.values.get('id')
    if type != 'nova':
        return return_result(msg=f'{type} not integration.')
    ret = llm_api.model_detail(model_id=model_id)
    # data = json.dumps(data) if isinstance(data, dict) else data
    logger.info(f"\nGet Latest Models detail: {ret.json()}\n")
    return return_result(data=ret.json().get('data'))


@llm_hook.route('/llm/chat_completions', methods=['POST'])
def llm_chat_completions():  
    model_id = request.json.get('model_id')
    if not model_id:
        return return_result(msg='model_id is required.')
    messages = request.json.get('messages') # {"role": "user", "content": "this is test"}
    ret = llm_api.completions(model=model_id, messages=messages)
    logger.info(f"\nGet Response: {ret.json()}\n")
    return return_result(data=ret.json().get('data'))

@llm_hook.route('/llm/chat_sessions', methods=['POST'])
def llm_chat_sessions():  
    system_prompt = request.json.get('system_prompt')
    ret = llm_api.chat_session(system_prompt=system_prompt)
    logger.info(f"\nGet Response: {ret.json()}\n")
    return return_result(data=ret.json())

@llm_hook.route('/llm/chat_conversations', methods=['POST'])
def llm_chat_conversations():  
    session_id = request.json.get('session_id')
    # action = request.json.get('action') # next or regeneration
    if not session_id:
        return return_result(msg='session_id is required.')
    content = request.json.get('content')
    if not content:
        return return_result(msg='content is required.')
    # stream = request.json.get('stream', False)
    model = request.json.get('model')
    if not model:
        return return_result(msg='model is required.')
    ret = llm_api.chat_conversations(**request.json)
    logger.info(f"\nGet Response: {ret.json()}\n")
    return return_result(data=ret.json())