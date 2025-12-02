# Kubernetes 部署指南

## 快速部署

### 1. 准备密钥

```bash
# 复制示例文件
cp k8s/secret.yaml.example k8s/secret.yaml

# 编辑并填入你的API密钥
# 注意：不要将包含真实密钥的文件提交到版本控制
```

### 2. 创建密钥

```bash
kubectl apply -f k8s/secret.yaml
```

### 3. 部署应用

```bash
# 应用所有配置
kubectl apply -f k8s/

# 或者单独应用
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/pvc.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml
```

### 4. 检查部署状态

```bash
# 查看Pod状态
kubectl get pods

# 查看服务
kubectl get svc

# 查看HPA
kubectl get hpa

# 查看Pod日志
kubectl logs -f deployment/desktop-pet
```

### 5. 监控资源使用

```bash
# 查看Pod资源使用
kubectl top pods

# 查看HPA状态
kubectl describe hpa desktop-pet-hpa
```

## 本地开发（Minikube）

### 启动Minikube

```bash
minikube start --cpus=2 --memory=8192 --driver=docker
minikube addons enable metrics-server
```

### 构建和加载镜像

```bash
# 构建Docker镜像
docker build -t desktop-pet:latest .

# 加载镜像到Minikube
minikube image load desktop-pet:latest
```

### 部署

```bash
kubectl apply -f k8s/
```

## 清理

```bash
# 删除所有资源
kubectl delete -f k8s/

# 删除PVC（会删除数据）
kubectl delete pvc desktop-pet-data-pvc desktop-pet-chromadb-pvc
```

