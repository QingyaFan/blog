# 容器资源限制

docker容器默认对于资源的使用没有限制，如果容器占用宿主机太多资源，可能会造成主机无响应，甚至宕机。拿内存使用来讲，由于OOME(Out Of Memmory Exception)机制的存在，当内存耗尽时，内核就会杀死一些进程释放内存，理论上任何进程都可能被杀死，包括docker daemon。杀死进程的规则是进程的评分，所以我们要保证服务不会因为资源耗尽而宕机，应该对容器限制可以使用的资源。

限制的方法有几种。

## docker

`docker run --help`，分别查看CPU和内存的配置参数：

```sh
--cpu-period int                 Limit CPU CFS (Completely Fair Scheduler) period
--cpu-quota int                  Limit CPU CFS (Completely Fair Scheduler) quota
--cpu-rt-period int              Limit CPU real-time period in microseconds
--cpu-rt-runtime int             Limit CPU real-time runtime in microseconds
--cpu-shares int                 CPU shares (relative weight)
--cpus decimal                   Number of CPUs
--cpuset-cpus string             CPUs in which to allow execution (0-3, 0,1)
--cpuset-mems string             MEMs in which to allow execution (0-3, 0,1)
```

```sh
--memory bytes                   Memory limit
--memory-reservation bytes       Memory soft limit
--memory-swap bytes              Swap limit equal to memory plus swap: '-1' to enable unlimited swap
--memory-swappiness int          Tune container memory swappiness (0 to 100) (default -1)
```

## docker-compose

```yml
version: '3'
services:
  redis:
    image: redis:alpine
    deploy:
      resources:
        limits:
          cpus: '0.50'
          memory: 50M
        reservations:
          cpus: '0.25'
          memory: 20M
```

## kubernetes

当指定了容器的资源限制，调度器将容器调度到哪个节点的决策会更容易做出。

```yml
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: redis-deploy
spec:
  replicas: 2
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:alpine
        imagePullPolicy: Always
        ports:
        - containerPort: 6379
      resources:
        limits:
          cpu:
          memory:
        requests:
          cpu:
          memory:
      imagePullSecrets:
      - name: regsecret
      dnsPolicy: ClusterFirst
```