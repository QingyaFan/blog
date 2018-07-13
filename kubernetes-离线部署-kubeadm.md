# 使用kubeadm离线部署Kubernetes集群

1. 安装Docker，可以参照 `docker-离线私有部署`。
2. `kubeadm init`。
3. `kubeadm join`。

## 安装kubeadm

在所有机器上安装`kubeadm`、`kubelet`和`kubectl`，因为要求离线安装，我们下载每个的rpm包进行安装。首先

## `kubeadm init`

`sudo /usr/local/bin/kubeadm --kubernetes-version=v1.9.9`

需要root运行，需要指定`kubernetes-version`参数，kubeadm首先首先检查docker和kubelet是否是合适的版本且已经启动，所以需要首先安装`docker`和`kubelet`。其次会检查`socat`和`crictl`是否在系统路径中。

保证`/etc/kubernetes/manifests`目录不存在

## `kubeadm join`