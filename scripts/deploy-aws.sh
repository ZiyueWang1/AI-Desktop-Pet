#!/bin/bash
# AWS EC2 部署脚本
# 用于在 EC2 实例上部署应用

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置（从环境变量读取）
AWS_REGION=${AWS_REGION:-us-east-1}
ECR_REPOSITORY=${ECR_REPOSITORY:-desktop-pet}
IMAGE_TAG=${IMAGE_TAG:-latest}
ECR_REGISTRY=${ECR_REGISTRY:-}  # 需要设置，格式: 123456789012.dkr.ecr.us-east-1.amazonaws.com

echo -e "${BLUE}🚀 AWS EC2 Deployment Script${NC}"
echo ""

# 检查必要的环境变量
if [ -z "$ECR_REGISTRY" ]; then
    echo -e "${RED}❌ Error: ECR_REGISTRY environment variable is required${NC}"
    echo "Example: export ECR_REGISTRY=123456789012.dkr.ecr.us-east-1.amazonaws.com"
    exit 1
fi

FULL_IMAGE="${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}"

echo -e "${GREEN}Configuration:${NC}"
echo "  AWS Region: ${AWS_REGION}"
echo "  ECR Registry: ${ECR_REGISTRY}"
echo "  Repository: ${ECR_REPOSITORY}"
echo "  Image Tag: ${IMAGE_TAG}"
echo "  Full Image: ${FULL_IMAGE}"
echo ""

# 1. 登录到 ECR
echo -e "${GREEN}📦 Logging in to Amazon ECR...${NC}"
aws ecr get-login-password --region ${AWS_REGION} | \
    docker login --username AWS --password-stdin ${ECR_REGISTRY} || {
    echo -e "${RED}❌ Failed to login to ECR${NC}"
    exit 1
}

# 2. 拉取最新镜像
echo -e "${GREEN}⬇️  Pulling latest image...${NC}"
docker pull ${FULL_IMAGE} || {
    echo -e "${YELLOW}⚠️  Failed to pull image, trying latest tag...${NC}"
    docker pull ${ECR_REGISTRY}/${ECR_REPOSITORY}:latest || {
        echo -e "${RED}❌ Failed to pull image${NC}"
        exit 1
    }
}

# 3. 停止旧容器
echo -e "${GREEN}🛑 Stopping old containers...${NC}"
docker-compose down || echo "No existing containers to stop"

# 4. 更新 docker-compose.yml（如果需要）
if [ -f "docker-compose.yml" ]; then
    echo -e "${GREEN}📝 Updating docker-compose.yml...${NC}"
    # 备份原文件
    cp docker-compose.yml docker-compose.yml.bak
    
    # 更新镜像（如果使用环境变量，这步可能不需要）
    # sed -i "s|image:.*desktop-pet:.*|image: ${FULL_IMAGE}|g" docker-compose.yml || true
fi

# 5. 设置环境变量并启动
echo -e "${GREEN}🚀 Starting containers...${NC}"
export ECR_REGISTRY=${ECR_REGISTRY}
export IMAGE_TAG=${IMAGE_TAG}
export FULL_IMAGE=${FULL_IMAGE}

# 如果 docker-compose.yml 使用环境变量，可以这样设置
# 或者直接修改 docker-compose.yml 中的镜像名称

docker-compose up -d || {
    echo -e "${RED}❌ Failed to start containers${NC}"
    # 恢复备份
    [ -f "docker-compose.yml.bak" ] && mv docker-compose.yml.bak docker-compose.yml
    exit 1
}

# 6. 等待服务启动
echo -e "${GREEN}⏳ Waiting for service to start...${NC}"
sleep 10

# 7. 健康检查
echo -e "${GREEN}🏥 Performing health check...${NC}"
for i in {1..30}; do
    if curl -f http://localhost:8080/health 2>/dev/null; then
        echo -e "${GREEN}✅ Health check passed!${NC}"
        break
    fi
    echo "Waiting for service... ($i/30)"
    sleep 2
done

# 8. 显示状态
echo ""
echo -e "${GREEN}📊 Container Status:${NC}"
docker-compose ps

echo ""
echo -e "${GREEN}📋 Recent Logs:${NC}"
docker-compose logs --tail=20

echo ""
echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo ""
echo "Useful commands:"
echo "  View logs:        docker-compose logs -f"
echo "  Stop service:     docker-compose down"
echo "  Restart service:  docker-compose restart"
echo "  View status:      docker-compose ps"

# 清理备份文件
rm -f docker-compose.yml.bak

