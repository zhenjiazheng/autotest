# Instruction:
## Design Rules：
    1. Docker[AutoTest Service Docker] run Docker[Test Framework Docker]  <br>
    2. 自动化测试框架 集成 docker + 【pytest + allure】，另外支持【unittest + htmlrunner】等其他docker运行  <br>
    3. 测试脚本等输出Docker并与项目关联  <br>
    4. 提供API外部触发测试，指定项目id  <br>
## 运行：
### Docker启动方式：
    1. docker network create autotest 
    2. 启动pg docker:
        docker run --net=autotest --name postgres_autotest --publish 5433:5432 -e POSTGRES_PASSWORD=88st2023 -e POSTGRES_DB=autotest -e PGDATA=/var/lib/postgresql/data/pgdata -e ALLOW_IP_RANGE=0.0.0.0/0 -v /data/pg_autotest:/var/lib/postgresql/data -d postgres[imageId]
    3. 启动服务docker: 
        docker run -d --net=autotest -e MODE=prod -e PGHOST=0.0.0.0 -e PGUSER=postgres -e PGPASSWORD=88st2023 -e PGPORT=15432 -e PORT=5100 -e SERTYPE=1 --name=autotestserver --publish 0.0.0.0:5100:5100 /var/run/docker.sock:/var/run/docker.sock -v /data/report:/autotest/report registry.sensetime.com:v1 
### 使用docker-compose启动
    1. docker-compose up -d