# Kubernetes集群内容器访问集群外服务

企业内部一般存在很多的微服务，在逐步容器化的过程中，会有部分服务在集群外部，未完成容器化，比如数据库，而部分已经完成容器化的依赖于这些服务的服务，过渡过程中，需要集群内部的容器访问集群外部的服务。

为了在容器化过程中，让服务不中断，就需要让Kubernetes集群内部的容器能访问集群外部的服务，怎么做到呢，在每个应用的配置文件中使用外部IP或者外部rds名字吗？这样做，在外部的应用容器化后，还需要修改之前依赖于该应用的应用的配置文件，重新打包容器，这显然不是一个好的方案。我们的诉求是，在所有应用容器化过程中，所有应用都可以无缝集成，`ExternalName`类型的Service和EndPoint都可以满足我们的要求，下面我们分别看一下。

## ExternalName 类型的 Service

在Docker环境中，由于Docker Engine自带 DNS Server，我们使用`容器名`来访问其它容器，因为容器是不稳定的，当容器宕掉，再重新启动相同镜像的容器，IP地址会改变，所以我们不使用IP访问其它容器；同样的，在Kubernetes集群中，由于我们使用 `kube-DNS`，我们常用Service名称来访问某个服务，Service资源对象能保证其背后的容器副本始终是最新的IP。

因此，我们可以利用这个特性，对Service名称和外部服务地址做一个映射，使之访问Service名称既是访问外部服务。例如下面的例子是将 `svc1` 和 `xxx.xxx.xxx.xxx` 做了对等关系。

```yml
kind: Service
apiVersion: v1
metadata:
  name: svc1
  namespace: default
spec:
  type: ExternalName
  externalName: somedomain.org
```

## 设置 Service 的 EndPoint

在Kubernetes集群中，同一个微服务的不同副本会对集群内或集群外（取决于服务对外暴露类型）暴露统一的服务名称，一个服务背后是多个 `EndPoint`，`EndPoint`解决映射到某个容器的问题，在 `EndPoint` 中不仅可以指定集群内容器的IP，还可以指定集群外的IP，我们可以利用这个特性使用集群外部的服务。

> `EndPoint` 方式的缺点是只能指定IP，不能使用网址，比如网址，比如RDS的地址，这种情况下只能使用`ExternalName`来解决。

```yml
apiVersion: v1
kind: Service
metadata:
  name: mysql-production
spec:
  ports:
    - port: 3306
---
kind: Endpoints
apiVersion: v1
metadata:
  name: mysql-production
  namespace: default
subsets:
  - addresses:
      - ip: 192.168.1.25
    ports:
      - port: 3306
```

## 总结

本文介绍了集群内部访问外部服务的两种方法，`ExternalName` 类型的服务适用于外部服务使用域名的方式，缺点是不能指定端口；而`EndPoint`的方式适合于外部服务是IP的情况，但是可以指定端口。根据需要使用吧！