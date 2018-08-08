# Docker使用中的小技巧

## 设置 Docker 存储路径

Docker默认的存储路径是`/var/lib/docker`，那么随着镜像和容器的增多，系统空间被压缩，存储耗尽，系统的各项服务会出一些奇怪的问题，所以我们要妥善处理储存。我们可以外挂一块磁盘到`/var/lib/docker`目录，或者更改docker默认的存储目录。

更改docker默认存储目录，需要修改`/etc/docker/daemon.json`配置文件，默认情况下这个文件不存在，`/etc/docker`中只有`key.json`，没有`daemon.json`，docker会使用默认配置，有则会覆盖默认配置。

## Docker可以将容器内的多个端口同时映射出来

例如nginx在docker可以将HTTP(80)和HTTPS(443)都暴露出来，在`docker-compose.yml`中可以如下配置：

```yml
nginx:
    container_name: nginx
    image: nginx:v1.0
    networks:
      - "host"
    volumes:
      - "~/nginx:/etc/nginx"
    ports:
      - "8000:80"
      - "8001:443"
    restart: always
```