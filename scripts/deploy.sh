#!/bin/bash
set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置
NAMESPACE=${K8S_NAMESPACE:-default}
IMAGE_TAG=${IMAGE_TAG:-latest}
DOCKER_REGISTRY=${DOCKER_REGISTRY:-localhost:5000}
IMAGE_NAME=${IMAGE_NAME:-desktop-pet}
FULL_IMAGE="${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"

echo -e "${GREEN}🚀 Starting deployment...${NC}"
echo "Namespace: ${NAMESPACE}"
echo "Image: ${FULL_IMAGE}"

# 检查 kubectl 是否可用
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}❌ kubectl not found. Please install kubectl first.${NC}"
    exit 1
fi

# 检查命名空间是否存在，不存在则创建
if ! kubectl get namespace ${NAMESPACE} &> /dev/null; then
    echo -e "${YELLOW}⚠️  Namespace ${NAMESPACE} not found, creating...${NC}"
    kubectl create namespace ${NAMESPACE}
fi

# 1. 应用配置（并行执行以节省时间）
echo -e "${GREEN}📦 Applying configurations...${NC}"
kubectl apply -f k8s/configmap.yaml -n ${NAMESPACE} &
CONFIGMAP_PID=$!

kubectl apply -f k8s/secret.yaml -n ${NAMESPACE} &
SECRET_PID=$!

kubectl apply -f k8s/pvc.yaml -n ${NAMESPACE} &
PVC_PID=$!

# 等待所有并行任务完成
wait $CONFIGMAP_PID $SECRET_PID $PVC_PID

# 2. 更新镜像（如果提供了镜像标签）
if [ "${IMAGE_TAG}" != "latest" ]; then
    echo -e "${GREEN}🔄 Updating image to ${FULL_IMAGE}...${NC}"
    
    # 备份原始文件
    cp k8s/deployment.yaml k8s/deployment.yaml.bak
    
    # 更新镜像版本（跨平台兼容）
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s|image:.*desktop-pet:.*|image: ${FULL_IMAGE}|g" k8s/deployment.yaml
    else
        # Linux
        sed -i "s|image:.*desktop-pet:.*|image: ${FULL_IMAGE}|g" k8s/deployment.yaml
    fi
fi

# 3. 应用服务配置
echo -e "${GREEN}🌐 Applying service configuration...${NC}"
kubectl apply -f k8s/service.yaml -n ${NAMESPACE}

# 4. 应用 PodDisruptionBudget
if [ -f "k8s/pdb.yaml" ]; then
    echo -e "${GREEN}🛡️  Applying PodDisruptionBudget...${NC}"
    kubectl apply -f k8s/pdb.yaml -n ${NAMESPACE}
fi

# 5. 应用部署配置
echo -e "${GREEN}📦 Applying deployment configuration...${NC}"
kubectl apply -f k8s/deployment.yaml -n ${NAMESPACE}

# 6. 应用 HPA
echo -e "${GREEN}📈 Applying HorizontalPodAutoscaler...${NC}"
kubectl apply -f k8s/hpa.yaml -n ${NAMESPACE}

# 7. 滚动更新（带超时）
echo -e "${GREEN}⏳ Waiting for rollout to complete...${NC}"
if kubectl rollout status deployment/desktop-pet -n ${NAMESPACE} --timeout=5m; then
    echo -e "${GREEN}✅ Rollout completed successfully!${NC}"
else
    echo -e "${RED}❌ Rollout timeout or failed!${NC}"
    echo "Current pod status:"
    kubectl get pods -l app=desktop-pet -n ${NAMESPACE}
    exit 1
fi

# 8. 验证部署
echo -e "${GREEN}✅ Verifying deployment...${NC}"
echo ""
echo "Pod status:"
kubectl get pods -l app=desktop-pet -n ${NAMESPACE}
echo ""
echo "Service status:"
kubectl get svc desktop-pet-service -n ${NAMESPACE}
echo ""
echo "HPA status:"
kubectl get hpa desktop-pet-hpa -n ${NAMESPACE} || echo "HPA not found"
echo ""

# 9. 健康检查
echo -e "${GREEN}🏥 Performing health check...${NC}"
sleep 5
POD_NAME=$(kubectl get pods -l app=desktop-pet -n ${NAMESPACE} -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

if [ -n "$POD_NAME" ]; then
    echo "Checking health of pod: $POD_NAME"
    if kubectl exec $POD_NAME -n ${NAMESPACE} -- python -c "import requests; requests.get('http://localhost:8080/health')" 2>/dev/null; then
        echo -e "${GREEN}✅ Health check passed!${NC}"
    else
        echo -e "${YELLOW}⚠️  Health check failed, but deployment may still be starting...${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  No pods found yet${NC}"
fi

# 清理备份文件
rm -f k8s/deployment.yaml.bak

echo ""
echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo ""
echo "Useful commands:"
echo "  View pods:        kubectl get pods -l app=desktop-pet -n ${NAMESPACE}"
echo "  View logs:        kubectl logs -f deployment/desktop-pet -n ${NAMESPACE}"
echo "  View service:     kubectl get svc desktop-pet-service -n ${NAMESPACE}"
echo "  View HPA:         kubectl get hpa desktop-pet-hpa -n ${NAMESPACE}"
echo "  Rollback:         kubectl rollout undo deployment/desktop-pet -n ${NAMESPACE}"

