import time
import jwt
import os
from config import config

ak = config[os.getenv('MODE', 'dev')].LLM_ACCESS_KEY
sk = config[os.getenv('MODE', 'dev')].LLM_SECRET_KEY
nova_llm_server = config[os.getenv('MODE', 'dev')].NOVA_LLM_SERVER

def get_auth_bearer():
    headers = {
        "alg": "HS256",
        "typ": "JWT"
    }
    payload = {
        "iss": ak,
        "exp": int(time.time()) + 1800, # 填写您期望的有效时间，此处示例代表当前时间+30分钟
        "nbf": int(time.time()) - 5 # 填写您期望的生效时间，此处示例代表当前时间-5秒
    }
    token = jwt.encode(payload, sk, headers=headers)
    return {"Authorization": f"Bearer {token}"}

# authorization = get_auth_bearer(ak, sk)
# print(authorization) # 打印生成的API_TOKEN
