# -*- coding: utf-8 -*-
#
import os


class PublicEmailConfig(object):
    Server = 'smtp.partner.outlook.cn'
    User = "eig.alarm@sensetime.com"
    Password = "djIU4&ksy!0O"
    EmailPort = 587


class LDAPConfig(object):
    LDAP_HOST = "ldap://rwdc.sz.sensetime.com"
    LDAP_BASE_DN = "dc=domain,dc=sensetime, dc=com"
    LDAP_BIND_USER_DN = "cn=%s,ou=people,dc=domain,dc=sensetime,dc=com"
    LDAP_SEARCH_FILTER = "cn=%s"
    LDAP_USER = "senselighting"
    LDAP_PASS = "vsyuIiR-W1exc-ki"


class PGConfig(object):
    PGHOST = os.environ.get("PGHOST", '10.9.114.7')
    PGUSER = os.environ.get("PGUSER", "postgres")
    PGPASS = os.environ.get("PGPASS", "88st2023")
    PGPORT = os.environ.get("PGPORT", 15432)


class CELERYConfig(object):

    RDSHOST = os.environ.get("RDSHOST", '10.9.114.7')
    RDSPASS = os.environ.get("RDSPASS", "ODhzdElWQTIwMTc=")
    CELERY_TASK_SERIALIZER = 'json',
    CELERY_ACCEPT_CONTENT = ['json']
    CELERYD_MAX_TASKS_PER_CHILD = 20
    CELERY_TASK_IGNORE_RESULT = True
    # CELERYD_CONCURRENCY = 80  # 并发worker数
    CELERY_TIMEZONE = 'Asia/Shanghai'
    # CELERY_ACKS_LATE = True
    BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 86400}
    # New config add to validate the celery worker
    CELERYD_PREFETCH_MULTIPLIER = 1
    # CELERYD_WORKER_LOST_WAIT = 600
    CELERY_SEND_EVENTS = True
    # BROKER_HEARTBEAT = 24 * 60 * 60 * 2
    CELERY_TRACK_STARTED = True
    TASKQUEEN = "TASKQUEEN"


class SocketSIPConig(object):
    PLATFORM_IP = os.environ.get("PLATFORM_IP", '0.0.0.0')
    PLATFORM_PORT = os.environ.get("PLATFORM_PORT", 39001)
    SOCKET_TIMEOUT = 10
    PLATFORM_CODE = os.environ.get("PLATFORM_CODE", "091600000000000000")
    SIP_PROTOCOL = os.environ.get("SIP_PROTOCOL", "UDP")
    STATION_CAM_CODE = os.environ.get("STATION_CAM_CODE", "0916000001030100XX")

class LLMCONFIG(object):
    LLM_ACCESS_KEY = "2XyMvjTtbEU4z0nnRlIsGpcWQ6Y" # 填写您的ak
    LLM_SECRET_KEY = "OxtVzKcPm126OpEE23HD8hzIhhuuAXKN" # 填写您的sk
    NOVA_LLM_SERVER = 'https://api.sensenova.cn'

class Config(LDAPConfig, PGConfig, CELERYConfig, SocketSIPConig, LLMCONFIG):
    CSRF_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    THREADS_PER_PAGE = 2
    OUSI_POSTS_PER_PAGE = 5
    DATABASE_CONNECT_OPTIONS = {}
    UPLOADED_FILES_ALLOW = ['jpg', 'png', 'bmp', 'xls', 'xlsx', 'zip']
    SQLALCHEMY_POOL_SIZE = 100
    SQLALCHEMY_POOL_RECYCLE = 1200
    JSON_SORT_KEYS = False  # Prevent Flask jsonify from sorting the data
    MAX_WORKERS = 200
    SON_AS_ASCII = False
    SECRET_KEY = '3JaTAURKQn0evWEw'
    REGISTRY="registry.sensetime.com"
    TOKEN_TIMEOUT = 24 * 3600
    URI_WHITE_LIST = ['/autotest/user/login', '/autotest/user/register']

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:88st2023@10.9.242.41:15432/autotest"
    REDIS_URL = "redis://:ODhzdElWQTIwMTc=@10.9.242.41:16379/0"
    CELERY_BROKER_URL = "redis://:ODhzdElWQTIwMTc=@10.9.242.41:16379/1"


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = f"postgresql://{Config.PGUSER}:{Config.PGPASS}@{Config.PGHOST}:{Config.PGPORT}/autotest"
    REDIS_URL = f"redis://:{Config.RDSPASS}@{Config.RDSHOST}:16379/0"
    CELERY_BROKER_URL = f"redis://:{Config.RDSPASS}@{Config.RDSHOST}:16379/1"


config = {
    'dev': DevelopmentConfig,
    'prod': ProductionConfig
}
