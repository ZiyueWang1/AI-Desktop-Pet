#!/bin/bash
# 清理构建缓存并重新构建镜像

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}清理 Python 缓存文件...${NC}"

# 清理所有 __pycache__ 目录
find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
find . -type f -name "*.pyd" -delete 2>/dev/null || true

echo -e "${GREEN}✓ 缓存文件已清理${NC}"
echo ""
echo -e "${YELLOW}现在可以重新构建镜像：${NC}"
echo "  docker build -t desktop-pet:latest ."
echo ""
echo -e "${YELLOW}或者在 Minikube 中直接构建（推荐）：${NC}"
echo "  eval \$(minikube docker-env)"
echo "  docker build -t desktop-pet:latest ."
echo "  eval \$(minikube docker-env -u)"

