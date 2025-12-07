#!/bin/bash
# 快速部署脚本 - 适用于本地开发和测试

set -e

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🚀 Quick Deploy Script${NC}"
echo "This script is for quick local deployment."
echo "For production, use Jenkins CI/CD pipeline or scripts/deploy.sh"
echo ""

# 检查是否在项目根目录
if [ ! -f "Dockerfile" ]; then
    echo "Error: Please run this script from the project root directory"
    exit 1
fi

# 配置
NAMESPACE=${K8S_NAMESPACE:-default}
IMAGE_NAME="desktop-pet"
IMAGE_TAG="local-$(date +%s)"

echo "Building Docker image..."
docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:latest

# 如果是 Minikube，加载镜像
if command -v minikube &> /dev/null && minikube status &> /dev/null; then
    echo "Loading image into Minikube..."
    minikube image load ${IMAGE_NAME}:${IMAGE_TAG}
    minikube image load ${IMAGE_NAME}:latest
fi

# 更新 deployment.yaml 中的镜像
echo "Updating deployment configuration..."
cp k8s/deployment.yaml k8s/deployment.yaml.bak

if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "s|image:.*desktop-pet:.*|image: ${IMAGE_NAME}:${IMAGE_TAG}|g" k8s/deployment.yaml
else
    sed -i "s|image:.*desktop-pet:.*|image: ${IMAGE_NAME}:${IMAGE_TAG}|g" k8s/deployment.yaml
fi

# 应用配置
echo "Applying Kubernetes configurations..."
kubectl apply -f k8s/configmap.yaml -n ${NAMESPACE} || echo "ConfigMap already exists"
kubectl apply -f k8s/secret.yaml -n ${NAMESPACE} || echo "Secret already exists (or not configured)"
kubectl apply -f k8s/pvc.yaml -n ${NAMESPACE} || echo "PVC already exists"
kubectl apply -f k8s/service.yaml -n ${NAMESPACE}
kubectl apply -f k8s/pdb.yaml -n ${NAMESPACE} || echo "PDB already exists"
kubectl apply -f k8s/deployment.yaml -n ${NAMESPACE}
kubectl apply -f k8s/hpa.yaml -n ${NAMESPACE}

# 等待部署完成
echo "Waiting for deployment..."
kubectl rollout status deployment/desktop-pet -n ${NAMESPACE} --timeout=3m || true

# 恢复备份
mv k8s/deployment.yaml.bak k8s/deployment.yaml

echo ""
echo -e "${GREEN}✅ Quick deployment completed!${NC}"
echo ""
echo "Check status:"
echo "  kubectl get pods -l app=desktop-pet -n ${NAMESPACE}"
echo "  kubectl get svc desktop-pet-service -n ${NAMESPACE}"

