FROM docker:latest
FROM python:3.8.16-slim-bullseye@sha256:f4efb39d02df8cdc44485a0956ea62e63aab6bf2a1dcfb12fb5710bf95583e72

RUN apt-get update && apt-get install -y \
    gcc libc-dev \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY --from=0 /usr/local/bin/docker /usr/bin/docker


ENV HOST 10.9.112.153
ENV PORT 5100
ENV PGHOST 10.9.112.153
ENV PGUSER postgres
ENV PGPASS 88st2023
ENV PGPORT 15433
ENV SER_TYPE 1
ENV POETRY_VERSION 1.4
ENV PLATFORM_IP 0.0.0.0
ENV PLATFORM_PORT  39001
ENV PLATFORM_CODE 091600000000000000
ENV STATION_CAM_CODE 0916000001030100XX


WORKDIR /autotest
COPY . /autotest


RUN set -ex; pip install --no-cache-dir poetry==$POETRY_VERSION;
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi


ENTRYPOINT ["/bin/bash", "-c", "cd /autotest && ./start_service.sh"]

