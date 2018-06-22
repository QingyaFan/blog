# 离线私有部署

在完全离线的情况下，给用户私有部署基于docker的系统。

## 一、docker环境

### 1.1 安装docker engine 和 docker client

预先下载docker的binary，编写docker的service配置文件，

```lang=text
[Unit]
Description=Docker Application Container Engine
Documentation=https://docs.docker.com
After=network-online.target firewalld.service
Wants=network-online.target

[Service]
Type=notify
# the default is not to use systemd for cgroups because the delegate issues still
# exists and systemd currently does not support the cgroup feature set required
# for containers run by docker
ExecStart=/usr/local/bin/dockerd
ExecReload=/bin/kill -s HUP $MAINPID
# Having non-zero Limit*s causes performance problems due to accounting overhead
# in the kernel. We recommend using cgroups to do container-local accounting.
LimitNOFILE=infinity
LimitNPROC=infinity
LimitCORE=infinity
# Uncomment TasksMax if your systemd version supports it.
# Only systemd 226 and above support this version.
#TasksMax=infinity
TimeoutStartSec=0
# set delegate yes so that systemd does not reset the cgroups of docker containers
Delegate=yes
# kill only the docker process, not all processes in the cgroup
KillMode=process
# restart the docker process if it exits prematurely
Restart=on-failure
StartLimitBurst=3
StartLimitInterval=60s

[Install]
WantedBy=multi-user.target
```

然后依次进行如下操作：

tar zxvf ../docker-18.03.1-ce.tgz
cp docker/* /usr/local/bin/
cp docker.service /usr/lib/systemd/system/
systemctl enable docker.service
systemctl start docker.service

运行`docker info`之后报错

```lang=text
WARNING: bridge-nf-call-iptables is disabled
WARNING: bridge-nf-call-ip6tables is disabled
```

可以执行

```lang=shell
sysctl net.bridge.bridge-nf-call-iptables=1
sysctl net.bridge.bridge-nf-call-ip6tables=1
```

但是这样的更改并不持久，如果reboot，问题会再次出现。所以，如果想做一个持久的更改，应该编辑`/etc/sysctl.conf`文件，添加如下内容：

```lang=text
net.bridge.bridge-nf-call-iptables = 1
net.bridge.bridge-nf-call-ip6tables = 1
```

最后执行`sysctl -p`即可。

### 1.2 安装docker-compose

GitHub下载二进制文件：`https://github.com/docker/compose/releases`

更改执行权限即可

```shell
cp docker-compose-Linux-x86_64 /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

## 2. 安装应用

`docker save -o app.tar example.com/dev/app:tag`
`docker load -i app.tar`
`docker-compose up -d app`