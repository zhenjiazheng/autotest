#!/bin/bash

echo "started activate service"
# shellcheck disable=SC2154
echo "$SER_TYPE, $MODE, $HOST, $PORT, $WORKERS"

if [ ${SER_TYPE} == 1 ]
then
  echo "启动API服务"
  echo "poetry run gunicorn --workers=${WORKERS} start_app:app --preload"
  poetry run gunicorn --workers=${WORKERS} start_app:app --preload
  # shellcheck disable=SC2034
elif [ ${SER_TYPE} == 2 ]
then
  echo "启动Celery任务调度服务"
  echo "poetry run celery worker -A start_app.celery --without-mingle -O fair --autoscale=20,10 -Q TASKQUEEN"
  poetry run celery worker -A start_app.celery --without-mingle -O fair --autoscale=20,10 -Q TASKQUEEN
  # shellcheck disable=SC2034
fi
