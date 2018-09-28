# Docker中的Loopback

## Loopback概念

TCP/IP协议族中包含一个`虚拟网络接口(virtual network interface)`，通过这个接口同一主机上的不同网络应用就可以相互通信，发送到`loopback`IP地址的通信会直接发送到本机的网络通信栈，被本机接受，不会真的发出去，而接受到这个通信的应用就像这个通信是来自其它主机一样消费它。

我们常用的`127.0.0.1`和`localhost`都是loopback的，在unix-like的系统里这个loopback接口一般简写为`lo`或者`lo0`，我们可以通过`ifconfig`来检查：

```txt
lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        inet 127.0.0.1  netmask 255.0.0.0
        loop  txqueuelen 1000  (Local Loopback)
        RX packets 8122999  bytes 16921605838 (16.9 GB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 8122999  bytes 16921605838 (16.9 GB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```

## Docker容器中的loopback

Docker镜像中应用的依赖在镜像中都包括，这是docker简化安装与部署的关键，应用的依赖包括系统环境，往往一个docker镜像的第一层（最底层）就是操作系统，操作系统我们可以选择`Ubuntu`、`CentOS`或者`Alpine`等等，其中`Alpine`因为体积小被广泛使用。

所以，Docker容器中也存在`loopback`机制，所以我们在容器中使用`localhost`或者`127.0.0.1`试图访问`宿主机`的其它网络应用的时候，会失败，因为`localhost`和`127.0.0.1`都是`loopback`IP，所以访问的是容器内部，请求不能到达宿主机。

## 如何在容器中访问宿主机？

Docker启动容器默认在一个名为`docker0`的`bridge`网络里，那么我们就可以通过`docker0`访问宿主机，比如使用`ifconfig`：

```txt
docker0: flags=4099<UP,BROADCAST,MULTICAST>  mtu 1500
        inet 172.18.0.1  netmask 255.255.0.0  broadcast 172.18.255.255
        ether 02:42:77:24:4c:a3  txqueuelen 0  (Ethernet)
        RX packets 0  bytes 0 (0.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 0  bytes 0 (0.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```

可以看到`172.18.0.1`是`docker0`的IP，那么在容器内访问`172.18.0.1`就相当于访问宿主机了。

## 应用中注意`hostname`的绑定

既然容器内有`loopbak`的存在，所以我们启动应用的时候绑定`hostname`就要避免`localhost`和`127.0.0.1`的使用。例如我们在容器中打包一个nodejs的应用，使用koa启动时有一个可选的参数是`hostname`，若不指定，默认为`0.0.0.0`，如果你指定了`localhost`或者`127.0.0.1`，那么即使你将容器中的端口映射到宿主机，你也不能访问，但是在容器中可以访问。所以如果指定，也要指定`0.0.0.0`。代码如下：

```js
const Koa = require("koa");
const app = new Koa();

app.listen(3000, '0.0.0.0', () => {
    console.log('service started!');
});
```

## 总结

本文主要介绍了`Loopback`的概念，Docker容器中的`Loopback`带来的问题及解决的方法。