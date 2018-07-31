# Docker Compose

## 一些需要注意的问题

1. `docker-compose`根据`docker-compose.yml`的配置启动容器，因此必须与`docker-compose.yml`文件在统一路径下。

2. `docker-compose up`不会更新原有镜像，所以如果镜像有更新，需要首先执行`docker-compose pull service_name`或`docker pull image_name`。