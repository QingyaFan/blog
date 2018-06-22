# 自动部署

之前的技术栈基于jenkins持续集成，现在基于虚拟机的后端应用都迁移到了Kubernetes集群中，如何让基于jenkins的持续集成流水线适应Kubernetes集群呢？

目前的方法：

1. ci服务器感知push操作，触发应用镜像的自动构建过程，构建完成推送到registry；
2. 到Kubernetes Master节点执行shell脚本`kubectl delete -f app.yaml`，`kubectl craete -f app.yaml`，其中app.yaml中的配置是每次create都重新pull镜像。

TODO:

以上方案的问题是每次都要停止服务，执行替换的过程中，应用不应该停止服务，使用蓝绿部署？