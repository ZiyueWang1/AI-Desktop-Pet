# AWS 部署指南

本指南介绍如何在 AWS 免费计划上部署 AI Desktop Pet 应用。

## AWS 免费计划资源

AWS 免费计划（Free Tier）包含：
- **EC2**: 750 小时/月的 t2.micro 或 t3.micro 实例（12个月）
- **ECR**: 500MB 存储空间（12个月）
- **数据传输**: 15GB 出站流量/月（12个月）

## 架构方案

### 方案 1: GitHub Actions + AWS EC2 + ECR（推荐）

**优点**：
- ✅ 完全免费（GitHub Actions 对公开仓库免费）
- ✅ 自动化 CI/CD
- ✅ 使用 AWS ECR 存储镜像
- ✅ 简单易用

**流程**：
```
GitHub Push → GitHub Actions → 构建镜像 → 推送到 ECR → 部署到 EC2
```

### 方案 2: AWS CodePipeline + CodeBuild + EC2

**优点**：
- ✅ AWS 原生服务
- ✅ 集成度高

**缺点**：
- ⚠️ CodePipeline 免费额度有限（每月 1 次）
- ⚠️ CodeBuild 免费额度有限（每月 100 分钟）

## 快速开始

### 步骤 1: 创建 AWS 资源

#### 1.1 创建 EC2 实例

1. 登录 AWS 控制台
2. 进入 EC2 服务
3. 启动实例：
   - **AMI**: Amazon Linux 2023 或 Ubuntu 22.04 LTS
   - **实例类型**: t2.micro 或 t3.micro（免费计划）
   - **存储**: 8GB（免费计划）
   - **安全组**: 开放端口 22（SSH）和 8080（应用）
   - **密钥对**: 创建或选择现有密钥对

4. 连接到实例：
   ```bash
   ssh -i your-key.pem ec2-user@your-ec2-ip
   # 或 Ubuntu
   ssh -i your-key.pem ubuntu@your-ec2-ip
   ```

#### 1.2 在 EC2 上安装 Docker

**Amazon Linux 2023**:
```bash
sudo yum update -y
sudo yum install docker -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user
# 重新登录使权限生效
```

**Ubuntu**:
```bash
sudo apt-get update
sudo apt-get install docker.io docker-compose -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ubuntu
# 重新登录使权限生效
```

#### 1.3 安装 AWS CLI

```bash
# Amazon Linux
sudo yum install aws-cli -y

# Ubuntu
sudo apt-get install awscli -y

# 配置 AWS 凭证
aws configure
# 输入你的 Access Key ID 和 Secret Access Key
# 区域: us-east-1（或你选择的区域）
```

#### 1.4 创建 ECR 仓库

```bash
# 创建 ECR 仓库
aws ecr create-repository --repository-name desktop-pet --region us-east-1

# 获取仓库 URI（格式: 123456789012.dkr.ecr.us-east-1.amazonaws.com/desktop-pet）
aws ecr describe-repositories --repository-names desktop-pet --region us-east-1
```

### 步骤 2: 配置 GitHub Secrets

在 GitHub 仓库设置中添加以下 Secrets：

1. **AWS_ACCESS_KEY_ID**: AWS 访问密钥 ID
2. **AWS_SECRET_ACCESS_KEY**: AWS 秘密访问密钥
3. **AWS_EC2_HOST**: EC2 实例的公网 IP 或域名
4. **AWS_EC2_USER**: EC2 用户名（Amazon Linux: `ec2-user`, Ubuntu: `ubuntu`）
5. **AWS_EC2_SSH_KEY**: EC2 SSH 私钥内容

**如何添加 Secrets**:
1. GitHub 仓库 → Settings → Secrets and variables → Actions
2. 点击 "New repository secret"
3. 添加上述每个 Secret

**如何获取 AWS 访问密钥**:
1. AWS 控制台 → IAM → Users → 你的用户
2. Security credentials → Create access key
3. 保存 Access Key ID 和 Secret Access Key

### 步骤 3: 配置 EC2 安全组

1. EC2 控制台 → Security Groups
2. 选择你的实例的安全组
3. 添加入站规则：
   - **SSH (22)**: 允许你的 IP 访问
   - **Custom TCP (8080)**: 允许所有 IP（或特定 IP）

### 步骤 4: 在 EC2 上准备部署环境

```bash
# 1. 克隆项目（或使用部署脚本）
cd ~
git clone https://github.com/your-username/AI-Desktop-Pet.git
cd AI-Desktop-Pet

# 2. 创建 .env 文件（如果需要）
cat > .env << EOF
ECR_REGISTRY=your-ecr-registry.dkr.ecr.us-east-1.amazonaws.com
IMAGE_TAG=latest
EOF

# 3. 修改 docker-compose.yml（如果需要使用 ECR 镜像）
# 将 build 改为 image，指向 ECR 镜像
```

### 步骤 5: 配置 GitHub Actions

`.github/workflows/deploy-aws.yml` 已经配置好了，只需要：

1. 更新 `AWS_REGION`（如果需要）
2. 更新 `ECR_REPOSITORY` 名称（如果需要）
3. 确保所有 Secrets 都已配置

### 步骤 6: 测试部署

```bash
# 1. 提交代码到 GitHub
git add .
git commit -m "Setup AWS deployment"
git push origin main

# 2. 查看 GitHub Actions 执行情况
# GitHub 仓库 → Actions 标签页

# 3. 部署成功后，访问应用
curl http://your-ec2-ip:8080/health
```

## 手动部署（不使用 GitHub Actions）

如果你想手动部署到 EC2：

```bash
# 1. 在本地构建并推送到 ECR
export AWS_REGION=us-east-1
export ECR_REGISTRY=your-ecr-registry.dkr.ecr.us-east-1.amazonaws.com
export ECR_REPOSITORY=desktop-pet
export IMAGE_TAG=latest

# 登录 ECR
aws ecr get-login-password --region $AWS_REGION | \
    docker login --username AWS --password-stdin $ECR_REGISTRY

# 构建镜像
docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .

# 推送镜像
docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest

# 2. 在 EC2 上部署
ssh -i your-key.pem ec2-user@your-ec2-ip
cd ~/AI-Desktop-Pet
export ECR_REGISTRY=your-ecr-registry.dkr.ecr.us-east-1.amazonaws.com
export IMAGE_TAG=latest
./scripts/deploy-aws.sh
```

## 更新 docker-compose.yml 使用 ECR 镜像

修改 `docker-compose.yml` 使用 ECR 镜像而不是本地构建：

```yaml
version: '3.8'

services:
  desktop-pet:
    image: ${ECR_REGISTRY}/desktop-pet:${IMAGE_TAG:-latest}  # 使用 ECR 镜像
    container_name: ai-desktop-pet
    volumes:
      - ./data:/app/data
      - ./data/chromadb:/app/data/chromadb
      - ./data/logs:/app/data/logs
    environment:
      - AI_PROVIDER=${AI_PROVIDER:-openai}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - CLAUDE_API_KEY=${CLAUDE_API_KEY}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
    restart: unless-stopped
    ports:
      - "8080:8080"
```

## 成本优化

### 1. 使用 Spot 实例（可选）

Spot 实例可以节省最多 90% 的成本，但可能被中断：
- 适合开发和测试环境
- 不适合生产环境

### 2. 使用 ECR 生命周期策略

清理旧镜像以节省存储空间：

```bash
aws ecr put-lifecycle-policy \
    --repository-name desktop-pet \
    --lifecycle-policy-text '{
        "rules": [{
            "rulePriority": 1,
            "description": "Keep last 10 images",
            "selection": {
                "tagStatus": "any",
                "countType": "imageCountMoreThan",
                "countNumber": 10
            },
            "action": {
                "type": "expire"
            }
        }]
    }'
```

### 3. 监控使用量

定期检查 AWS 免费计划使用情况：
- AWS 控制台 → Billing and Cost Management
- 查看 Free Tier 使用情况

## 故障排查

### 1. ECR 登录失败

```bash
# 检查 AWS 凭证
aws sts get-caller-identity

# 检查 ECR 权限
aws ecr describe-repositories --region us-east-1
```

### 2. EC2 无法拉取镜像

```bash
# 检查 EC2 实例的 IAM 角色是否有 ECR 权限
# 或使用 AWS CLI 凭证
aws ecr get-login-password --region us-east-1 | \
    docker login --username AWS --password-stdin your-ecr-registry
```

### 3. 应用无法访问

```bash
# 检查容器状态
docker-compose ps

# 查看日志
docker-compose logs

# 检查端口
netstat -tuln | grep 8080

# 检查安全组规则
# EC2 控制台 → Security Groups → 检查入站规则
```

### 4. GitHub Actions 部署失败

1. 检查 Secrets 是否正确配置
2. 检查 EC2 安全组是否允许 SSH
3. 查看 GitHub Actions 日志获取详细错误信息

## 安全建议

1. **使用 IAM 角色**（推荐）：
   - 为 EC2 实例创建 IAM 角色
   - 授予 ECR 读取权限
   - 避免在代码中存储 AWS 凭证

2. **限制安全组**：
   - SSH (22) 端口只允许你的 IP
   - 应用端口 (8080) 根据需要限制

3. **定期更新**：
   - 更新 EC2 实例系统包
   - 更新 Docker 镜像
   - 更新应用依赖

4. **监控和日志**：
   - 启用 CloudWatch 日志
   - 设置 CloudWatch 告警

## 下一步

- [ ] 设置 CloudWatch 监控
- [ ] 配置自动备份
- [ ] 设置域名和 SSL 证书（使用 AWS Certificate Manager）
- [ ] 配置负载均衡（如果需要）

## 参考资源

- [AWS Free Tier](https://aws.amazon.com/free/)
- [ECR 文档](https://docs.aws.amazon.com/ecr/)
- [EC2 文档](https://docs.aws.amazon.com/ec2/)
- [GitHub Actions 文档](https://docs.github.com/en/actions)

