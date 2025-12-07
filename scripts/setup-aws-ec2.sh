#!/bin/bash
# AWS EC2 初始化脚本
# 在 EC2 实例上运行此脚本来准备部署环境

set -e

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 AWS EC2 Setup Script${NC}"
echo ""

# 检测操作系统
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "Cannot detect OS"
    exit 1
fi

echo -e "${GREEN}Detected OS: $OS${NC}"
echo ""

# 1. 更新系统
echo -e "${GREEN}📦 Updating system packages...${NC}"
if [ "$OS" = "amzn" ] || [ "$OS" = "rhel" ] || [ "$OS" = "centos" ]; then
    sudo yum update -y
elif [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    sudo apt-get update -y
    sudo apt-get upgrade -y
fi

# 2. 安装 Docker
echo -e "${GREEN}🐳 Installing Docker...${NC}"
if [ "$OS" = "amzn" ] || [ "$OS" = "rhel" ] || [ "$OS" = "centos" ]; then
    sudo yum install docker -y
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker $USER
elif [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    sudo apt-get install docker.io -y
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker $USER
fi

# 3. 安装 Docker Compose
echo -e "${GREEN}📦 Installing Docker Compose...${NC}"
if [ "$OS" = "amzn" ] || [ "$OS" = "rhel" ] || [ "$OS" = "centos" ]; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
elif [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    sudo apt-get install docker-compose -y
fi

# 4. 安装 AWS CLI
echo -e "${GREEN}☁️  Installing AWS CLI...${NC}"
if [ "$OS" = "amzn" ] || [ "$OS" = "rhel" ] || [ "$OS" = "centos" ]; then
    if ! command -v aws &> /dev/null; then
        curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
        unzip awscliv2.zip
        sudo ./aws/install
        rm -rf aws awscliv2.zip
    fi
elif [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    sudo apt-get install awscli -y
fi

# 5. 安装 Git
echo -e "${GREEN}📥 Installing Git...${NC}"
if [ "$OS" = "amzn" ] || [ "$OS" = "rhel" ] || [ "$OS" = "centos" ]; then
    sudo yum install git -y
elif [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    sudo apt-get install git -y
fi

# 6. 安装 curl
echo -e "${GREEN}📡 Installing curl...${NC}"
if [ "$OS" = "amzn" ] || [ "$OS" = "rhel" ] || [ "$OS" = "centos" ]; then
    sudo yum install curl -y || true
elif [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    sudo apt-get install curl -y
fi

# 7. 验证安装
echo -e "${GREEN}✅ Verifying installations...${NC}"
echo ""
echo "Docker version:"
docker --version || echo "Docker not found"
echo ""
echo "Docker Compose version:"
docker-compose --version || echo "Docker Compose not found"
echo ""
echo "AWS CLI version:"
aws --version || echo "AWS CLI not found"
echo ""
echo "Git version:"
git --version || echo "Git not found"
echo ""

# 8. 创建项目目录
echo -e "${GREEN}📁 Creating project directory...${NC}"
mkdir -p ~/projects
cd ~/projects

# 9. 提示下一步
echo -e "${YELLOW}📝 Next steps:${NC}"
echo ""
echo "1. Configure AWS credentials:"
echo "   aws configure"
echo ""
echo "2. Clone your repository:"
echo "   git clone https://github.com/your-username/AI-Desktop-Pet.git"
echo "   cd AI-Desktop-Pet"
echo ""
echo "3. Set up environment variables:"
echo "   export ECR_REGISTRY=your-ecr-registry.dkr.ecr.us-east-1.amazonaws.com"
echo "   export IMAGE_TAG=latest"
echo ""
echo "4. Deploy:"
echo "   ./scripts/deploy-aws.sh"
echo ""
echo -e "${GREEN}✅ Setup completed!${NC}"
echo ""
echo -e "${YELLOW}⚠️  Note: You may need to log out and log back in for Docker group changes to take effect.${NC}"

