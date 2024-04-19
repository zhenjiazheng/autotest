
import multiprocessing
import os
import socket


def host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


timeout = 3600
home = os.path.split(os.path.realpath(__file__))[0]
log_root = os.path.join(home, "logs")
ip = os.environ.get("HOST", host_ip())
port = os.environ.get("PORT", 5100)
bind = '{0}:{1}'.format(ip, port)
logfile = '{0}/app.log'.format(log_root)
accesslog = '{0}/gunicorn_acess.log'.format(log_root)
errorlog = '{0}/gunicorn_error.log'.format(log_root)

workers = multiprocessing.cpu_count() * 3 + 1

worker_class = 'gunicorn.workers.ggevent.GeventWorker'

x_forwarded_for_header = 'X-FORWARDED-FOR'
