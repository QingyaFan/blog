# 自动部署

之前的技术栈基于jenkins持续集成，现在基于虚拟机的后端应用都迁移到了Kubernetes集群中，如何让基于jenkins的持续集成流水线适应Kubernetes集群呢？

目前的方法：

1. ci服务器感知push操作，触发应用镜像的自动构建过程，构建完成推送到registry；
2. 到Kubernetes Master节点执行shell脚本`kubectl delete -f app.yaml`，`kubectl create -f app.yaml`，其中app.yaml中的配置是每次create都重新pull镜像。

## 服务不间断部署的方法

Kubernetes中，使用`kubectl apply -f app-config.yaml`可以将yaml的更改应用到指定的资源，但要求资源启动的时候使用`--save-config`参数，且yaml必须有更改，否则直接忽略不更新。

yaml配置文件的更改只能来自于镜像的名称，镜像的名称包含镜像仓库和tag，所以我们可以将版本控制引入到镜像中，每次tag与版本相关或者说是一个不重复的字符串序列，将版本更新到yaml配置文件，下面我使用一个随机的字符串序列来举例。

```yml
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: frontend-deploy
spec:
  replicas: 2
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: registry/frontend:12345
        imagePullPolicy: Always
        ports:
        - containerPort: 8080
      imagePullSecrets:
      - name: regsecret
```