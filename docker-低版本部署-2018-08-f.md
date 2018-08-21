# Docker低版本部署

本文主要是将docker高版本制作的镜像部署到低版本的docker会遇到的问题及其解决方法。

Docker低版本是指`< 1.10`的版本，在docker发布1.10时有一些不兼容的改进和更新，彼时，docker团队发了一篇博客来说明这次更新，感兴趣的可以看看： https://blog.docker.com/2016/02/docker-1-10/。

涉及兼容性的主要更新有：

- 新增内置的DNS，
- 镜像的读写层也有更改。

## DNS兼容性

如果依赖于DNS进行容器间访问的应用会出现问题，可以采用在宿主机的`/etc/hosts`添加规则来解决，例如：应用A访问应用B的服务，应用A的配置文件中使用`svcB`来访问应用B的容器，在Docker没有支持DNS的低版本里，我们可以在`/etc/hosts`中添加：

```conf
127.0.0.1       localhost
127.0.0.1       svcB
```

由于docker容器都继承了宿主机的`/etc/hosts`，因此，容器间可以通过svcB直接转换为`127.0.0.1`。

## 镜像读写层

高版本的Docker环境下制作的PostgreSQL镜像，在低版本启动出现问题：

> docker could not resize shared memory segment bytes: Not supported

Google一圈，说`/dev/shm`分配的太小占大多数，想试试，发现低版本docker没办法配置`/dev/shm`的大小。于是将PostgreSQL的Dockerfile放到低版本的docker中构建了一遍，结果可用了。