# -*- coding: utf-8 -*-
# Import flask dependencies

from flask import Blueprint, request
import json
from app.app import redis_store, return_result
from tools import AESCrypto
from config import Config
from app.dbs.common import Users


mod_users = Blueprint('users', __name__, url_prefix='/autotest')


@mod_users.route('/user/login', methods=['POST'])
def user_login():
    """
    @api {post} /autotest/user/login  用户登陆
    @apiVersion 1.0.0
    @apiName user_login
    @apiGroup users
    @apiParam {dict}  account      (必须)    用户邮箱
    @apiParam {str}  passsword      (必须)    密码
    @apiParamExample {json} Request-Example:
        {
            "account": "test@test.com",
            "password": "hshshshsjkskslslss"
        }
    @apiSuccess (回参) {int} code     0
    @apiSuccess (回参) {str} msg      message
    @apiSuccessExample {json} Success-Response:

        {
            "code": 0,
            "data": {"toke": "casdassjsdkahkdhalhdadhadada"},
            "msg": ""
        }
    """
    account = request.json.get("account")
    password = request.json.get("password")
    aes = AESCrypto()
    secret_key = Config.SECRET_KEY
    try:
        data = aes.decrypt(secret_key, password)
        print(data)
    except Exception as e:
        print(e.__str__())
        return return_result(code=3, msg=e.__str__())
    users = Users.get_with_kwargs(account=account).all()
    if not users:
        return return_result(code=3, msg='user not exist, please register first')
    if users[0].password != aes.ecb_decrypt(secret_key, password):
        return return_result(code=3, msg='password is wrong')
    
    user_dict = users[0].to_dict()
    token = aes.ecb_encrypt(secret_key, json.dumps(user_dict))
    user_key = f"token:{token}"
    redis_store.set(user_key, json.dumps(user_dict))
    redis_store.expire(user_key, Config.TOKEN_TIMEOUT)
    
    return return_result(data={'token': token, 'user_info': user_dict, 'perms': ['menu1', 'menu2', 'menu3', 'menu1-sub1']})


@mod_users.route('/user/logout', methods=['POST'])
def user_logout():
    """
    @api {post} /autotest/user/logout  用户登出
    @apiVersion 1.0.0
    @apiName user_logout
    @apiGroup users
    @apiParamExample {json} Request-Example:
        {}
    @apiSuccess (回参) {int} code     0
    @apiSuccess (回参) {str} msg      message
    @apiSuccessExample {json} Success-Response:

        {
            "code": 0,
            "msg": ""
        }
    """
    token_key = f"token:{request.headers.get('token')}"
    redis_store.delete(token_key)
    return return_result()


@mod_users.route('/user/register', methods=['POST'])
def user_register():
    """
    @api {post} /autotest/user/login  用户注册
    @apiVersion 1.0.0
    @apiName user_login
    @apiGroup users
    @apiParam {dict}  account      (必须)    用户邮箱
    @apiParam {str}  password      (必须)    密码
    @apiParamExample {json} Request-Example:
        {
            "account": "test@test.com",
            "password": "hshshshsjkskslslss",
            "username": "test"
        }
    @apiSuccess (回参) {int} code     0
    @apiSuccess (回参) {str} msg      message
    @apiSuccessExample {json} Success-Response:

        {
            "code": 0,
            "msg": ""
        }
    """
    account = request.json.get("account")
    password = request.json.get("password")
    username = request.json.get("username")
    if not account  or not password or not username:
        return return_result(code=3, msg='Require param miss')
    aes = AESCrypto()
    secret_key = Config.SECRET_KEY
    password = aes.ecb_decrypt(secret_key, password) if password else ''
    user = Users.create(account=account, password=password,username=username )
    return return_result(data=user.to_dict())

@mod_users.route('/user/update_password', methods=['POST'])
def user_update_password():
    """
    @api {post} /autotest/user/update_password  用户修改密码
    @apiVersion 1.0.0
    @apiName user_login
    @apiGroup users
    @apiParam {dict}  password      (必须)    用户邮箱
    @apiParam {str}  new_password      (必须)    密码
    @apiParamExample {json} Request-Example:
        {
            "password": "hshshshsjkskslslss",
            "new_password": "hshshshsjkskslslss"
        }
    @apiSuccess (回参) {int} code     0
    @apiSuccess (回参) {str} msg      message
    @apiSuccessExample {json} Success-Response:

        {
            "code": 0,,
            "msg": ""
        }
    """
    new_password = request.json.get("new_password")
    password = request.json.get("password")
    user_id = request.json.get("user_id")
    token = request.headers.get("token")
    aes = AESCrypto()
    secret_key = Config.SECRET_KEY
    old_password = aes.ecb_decrypt(secret_key, password)
    user_key = f"token:{token}"
    user_info = json.loads(redis_store.get(user_key))
    user = Users.get_with_kwargs(account=user_info.get('account'), id=user_id).first()
    if not user:
        return return_result(code=3, msg='user not exist, update password fail')
    if user.password != old_password:
        return return_result(code=3, msg='password is wrong')
    breakpoint()
    update_pass = aes.ecb_decrypt(secret_key, new_password)
    user.update(password=update_pass)
    return return_result()
