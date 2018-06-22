# 制作镜像

初学docker总是有点疑惑，镜像是什么？容器又是什么？它们之间有什么区别，它们之间有什么联系？怎么制作镜像，怎么运行容器？在这篇文章里就来总结一下。

## 一、什么是镜像，什么是容器

镜像（docker image）就是一个打包好的安装文件，镜像中不仅包含你的应用，还包含应用运行需要的所有依赖和环境，上至一些library，下至操作系统。而容器（docker container）就是我们在docker Engine环境中启动的镜像实例，容器和操作系统中其它进程没有区别，只不过拥有自己的网络和存储，与系统中其它的进程实现隔离，同时也与其它容器隔离。

镜像名称的格式是`url/directory/name:tag`，例如`sample.com/busybox:v3.2`，当我们拉取该镜像时，docker engine会尝试从`sample.com`拉取该镜像，如果镜像名字中没有指定url，会从docker engine配置中的镜像仓库拉取，默认docker hub；名字中的tag并不是必须的，如果不指定，默认为"latest"。

已经有很多人制作了很多应用的镜像，共享在了DockerHub或者其他公共镜像仓库（例如国内的阿里云镜像仓库），我们没有必要重复造轮子，DockerHub就像GitHub一样，我们可以从中拉取已有镜像来使用，如果现有镜像不能满足需求，就需要自己制作镜像，那么下面我们来说说制作镜像的方法。

## 二、制作镜像

docker制作镜像有两种方法：

1. 利用dockerfile，将构建流程写入dockerfile文件，然后执行，`docker build -f docker_file_name`；
2. 现有容器基础上构建，`docker commit container_name/container_id new_image_name`。

### 2.1 dockerfile

dockerfile是一个配置文件，它告诉docker如何构建镜像，docker会根据dockerfile中的指令，一步一步的完成镜像。一个典型的nodejs后端API项目dockerfile如下：

```lang=yaml

FROM base_image
WORKDIR /var/apps/app_name

# 安装项目依赖包
COPY ./package.json ./
RUN cnpm install --production

# 拷贝项目文件
COPY ./ ./

EXPOSE 3000
CMD [ "node", "app.js" ]

```

`FROM`关键字确定了基础镜像，很多时候，我们不需要自己从头开始制作，我们可以基于已有的轮子来做，基础镜像可以是操作系统，也可以是安装了一些依赖的操作系统，后面的命令都是基于这个基础，在这个基础镜像提供的环境中执行命令，进行操作。例如`WORKDIR`是在镜像中指定了一个项目目录，如果目录不存在，会自动创建；`COPY`是将文件拷贝到镜像内，这些文件时docker开始构建镜像时读取的，docker开始构建镜像时会读取dockerfile所在目录的所有文件至docker engine中，不过有一个`.dockerignore`文件可以配置docker忽略读取的文件，类似于`.gitignore`，`./`当前路径即表示dockerfile所在的文件夹；`RUN`表示在镜像中执行shell命令，`cnpm install --production`则表示安装nodejs项目的依赖；接下来又有一个copy，拷贝所有项目文件；`EXPOSE`则是暴露项目的监听端口；最后`CMD`表示镜像启动时执行的命令，这个命令必须是不被挂起的，不能以Service的形式，否则容器启动就会马上退出。

这里大家可能会有疑问，为什么copy分为两部分，不在一个copy命令中一次性拷贝完成呢？这是因为docker镜像是分层构建的，每个命令都对应着镜像的一层，而在两次构建中某一层没有改变时，则不会重新构建这一层，nodejs项目的依赖包很少变动，所以选择放在镜像的下一层，其它代码文件频繁变动，所以选择和package.json的拷贝分开。

### 2.2 docker commit

在一个运行的容器中，有时候你需要添加一些依赖，或者修改某些文件，想下次启动容器时依然保留改动，不想从头构建，那可以使用`docker commit`基于容器生成一个镜像。

```lang=shell
docker commit [OPTIONS] container_id_or_name image:tag
```

下次启动容器直接从`image:tag`这个镜像启动即可。

> 注：在容器中做了修改，需要重新启动容器，然后执行`docker commit`才能生效。

## 三、管理镜像

镜像作为一种资源，docker提供了方便的管理方法，具体说来，假设我们机器上有一个名为`busybox:test`的镜像，我们可以使用下面的方法对其进行增删改查：

- 查，使用`docker images`或`docker image ls`查看所有镜像的列表；
- 使用`docker tag busybox:test yet_another_name:new_tag`取一个别名，这时再`docker images`会发现多了一个镜像，不要被表象迷惑，该操作并不会重新创建镜像，而是添加了一个引用，就像刘备和刘皇叔都是刘备一样；
- 使用`docker rmi busybox:test`删除镜像；
- 使用`docker pull busybox:test`拉取镜像；
- 使用`docker push busybox:test`推送镜像到镜像仓库。

## 四、总结

两种镜像制作方法，建议经常使用第一种。制作完镜像，就可以启动容器了，启动容器也有很多选项，很多时候启动的容器并不会完全按照你的设想工作，这就要求你必须指定正确的启动选项，尤其是容器需要额外的存储和网络时，这一部分内容也比较多，下一篇再讲。