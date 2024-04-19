# -*- coding: utf-8 -*-
import sys
import os

from app.app import create_app
# from gun import *
from celery import Celery, platforms
from urllib3.util.ssl_ import create_urllib3_context
from config import config

platforms.C_FORCE_ROOT = True
create_urllib3_context()


def make_celery(application):
    application.config.from_object(config[os.getenv('MODE', 'dev')])
    celery_instance = Celery(
        application.import_name,
        broker=application.config['CELERY_BROKER_URL'],
        backend=application.config['CELERY_BROKER_URL']
    )
    celery_config = {}
    for item_key, item_value in application.config.items():
        if item_key.startswith("CELERY") or item_key.startswith("RDS") or item_key == "SQLALCHEMY" \
                or item_key.startswith("REDIS") or item_key.startswith("BROKER"):
            celery_config.update({item_key: item_value})
    celery_instance.conf.update(celery_config)
    Taskbase = celery_instance.Task

    class ContextTask(Taskbase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with application.app_context():
                # print(application.app_context())
                print(args, kwargs)
                return Taskbase.__call__(self, *args, **kwargs)

    class MyTask(ContextTask):
        def on_success(self, retval, task_id, args, kwargs):
            print('task done: {0}'.format(retval))
            return super(MyTask, self).on_success(retval, task_id, args, kwargs)

        def on_failure(self, exc, task_id, args, kwargs, einfo):
            print('task fail, reason: {0}'.format(exc))
            return super(MyTask, self).on_failure(exc, task_id, args, kwargs, einfo)

    celery_instance.Task = MyTask
    return celery_instance


if __name__ == '__main__':
    mode = "dev" if len(sys.argv) < 2 else sys.argv[1]
    ip = '0.0.0.0' if len(sys.argv) < 3 else sys.argv[2]
    port = 5100 if len(sys.argv) < 4 else int(sys.argv[3])
    os.environ.setdefault("MODE", mode)
    app = create_app(mode)
    app.logger.info("Start Running:" + mode)
    use_reloader = False
    if mode == 'dev' or mode == 'test':
        use_reloader = True
        os.environ.setdefault("mode", "dev")
        for key, value in app.config.items():
            if key.startswith('CELERY') or key.startswith('REDIS') or key.startswith('SQLALCHEMY'):
                print(f"{key} ====> {value}")
    app.run(host=ip, port=port, debug=use_reloader)
else:
    mode = os.environ.get("MODE", "prod")
    host = os.environ.get("HOST", "0.0.0.0")
    port = os.environ.get("PORT", 5100)
    app = create_app(mode)
    celery = make_celery(app)
