# 自动部署

之前的技术栈基于jenkins持续集成，现在基于虚拟机的后端应用都迁移到了Kubernetes集群中，如何让基于jenkins的持续集成流水线适应Kubernetes集群呢？

目前的方法：

1. ci服务器感知push操作，触发应用镜像的自动构建过程，构建完成推送到registry；
2. 到Kubernetes Master节点执行shell脚本`kubectl delete -f app.yaml`，`kubectl create -f app.yaml`，其中app.yaml中的配置是每次create都重新pull镜像。

## 服务不间断部署的方法

Kubernetes中，使用`kubectl apply -f app-config.yaml`可以将yaml的更改应用到指定的资源，但要求资源启动的时候使用`--save-config`参数，且yaml必须有更改，否则直接忽略不更新。

yaml配置文件的更改只能来自于镜像的名称，镜像的名称包含镜像仓库和tag，所以我们可以将版本控制引入到镜像中，每次tag与版本相关或者说是一个不重复的字符串序列，将版本更新到yaml配置文件，下面我使用一个随机的字符串序列来举例。

配置文件: backend.yaml

```yml
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: backend-deploy
spec:
  replicas: 2
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: registry/backend:201803181212
        imagePullPolicy: Always
        ports:
        - containerPort: 8080
      imagePullSecrets:
      - name: regsecret
```

1. 通过配置文件启动： `kubectl create --save-config -f backend.yaml`
2. 在jenkins中构建时生成时间记号： `201803181412`，可以通过值执行shell时获取时间并将时间记号写入到文件(假设为 env.sh)。

```sh
echo TIME_PARAM="$(date "+%Y%m%d%H%M%S")" >> ./env.sh
```

3. 然后将文件拷贝到Kubernetes的Master节点，将该环境变量替换yml配置文件中的镜像tag。

```sh
chmod +x ./env.sh
source ./env.sh
sed -i -E "s/registry\/backend:[0-9]+/registry\/backend:$TIME_PARAM/g" ./backend.yaml
kubectl apply -f geohey-cloud.yaml
```

这样Deployment相关的Pod在更新过程中会始终有可用Pod，这个数量可以设置。