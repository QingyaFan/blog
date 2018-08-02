# Docker-Compose

## 什么时候使用`depends_on`

当在一个服务器上放置所有应用容器时，我们可以利用`depends_on`来管理依赖，例如：

```yml

service_name_a
  container_name: service_name_a
  image: image_uri
  networks:
    - xxx
  volumes:
    - ""
  expose:
    - "8080"
  ports:
    - "8000:8080"
  depends_on:
    - service_name_b
  restarts: always

service_name_b
  container_name: service_name_b
  image: image_uri
  networks:
    - xxx
  volumes:
    - ""
  expose:
    - "9000"
  ports:
    - "9000:9000"
  restarts: always

```

启动`service_name_a`时，会首先检查`service_name_b`是否启动，如果没有，则首先启动`service_name_b`。

但这种便利可能成为一种禁锢，有时我们想将应用分别放在不同的服务器上时，假设存在依赖关系的两个容器分布在不同的服务器上，如果配置了`depends_on`，会先将依赖的容器在相同服务器启动，反而不灵活。

总结： 当在一台服务器上部署所有应用，使用`depends_on`声明依赖关系较好，当存在依赖关系的应用要分布到不同的服务器上时，不使用`depends_on`反而会更灵活。

## 为什么使用`extra_hosts`

容器网络使用`host`模式时，容器会使用宿主机`/etc/hosts`中配置的条目，但往往`bridge`网络模式更加实用，但不能使用宿主机的`/etc/hosts`规则，假设我们要让在服务器A部署的服务a访问服务器B部署的数据库b，那么就需要配置`extra_hosts`，借助该参数，我们可以让每个容器都可以使用配置定制的`IP -> name`映射。

![extra_hosts](./image/docker-extra-hosts.png)