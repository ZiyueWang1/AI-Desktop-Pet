# AWS 快速开始指南

5 分钟快速部署到 AWS EC2！

## 前置要求

- ✅ AWS 账户（免费计划）
- ✅ GitHub 账户
- ✅ 项目已推送到 GitHub

## 步骤 1: 创建 EC2 实例（5分钟）

### 1.1 启动 EC2 实例

1. 登录 [AWS 控制台](https://console.aws.amazon.com/)
2. 进入 **EC2** 服务
3. 点击 **Launch Instance**
4. 配置：
   - **Name**: `desktop-pet-server`
   - **AMI**: Amazon Linux 2023 或 Ubuntu 22.04 LTS
   - **Instance type**: `t2.micro`（免费计划）
   - **Key pair**: 创建新密钥对或选择现有
   - **Network settings**: 
     - 创建安全组
     - 允许 SSH (22) 和 Custom TCP (8080)
   - **Storage**: 8GB（免费计划）

5. 点击 **Launch Instance**

### 1.2 记录重要信息

- **EC2 公网 IP**: 例如 `54.123.45.67`
- **EC2 用户名**: 
  - Amazon Linux: `ec2-user`
  - Ubuntu: `ubuntu`
- **密钥文件**: 下载的 `.pem` 文件

## 步骤 2: 在 EC2 上安装软件（5分钟）

### 2.1 连接到 EC2

**Ubuntu 用户**（你选择的）：
```bash
# Windows (PowerShell)
ssh -i your-key.pem ubuntu@your-ec2-ip

# Linux/Mac
chmod 400 your-key.pem
ssh -i your-key.pem ubuntu@your-ec2-ip
```

**Amazon Linux 用户**：
```bash
ssh -i your-key.pem ec2-user@your-ec2-ip
```

### 2.2 安装软件（Ubuntu）

**一条一条复制粘贴**：

```bash
# 更新系统
sudo apt-get update
sudo apt-get upgrade -y

# 安装所有需要的软件
sudo apt-get install docker.io docker-compose awscli git curl -y

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker

# 添加用户到 docker 组
sudo usermod -aG docker ubuntu
```

**重要**: 安装完成后，**退出 SSH 并重新登录**，使 Docker 权限生效。

```bash
exit
# 然后重新连接
ssh -i your-key.pem ubuntu@your-ec2-ip
```

**验证安装**：
```bash
docker --version
docker-compose --version
aws --version
```

如果都显示版本号，说明安装成功！✅

**详细步骤**：参见 [Ubuntu EC2 设置指南](UBUNTU_EC2_SETUP.md)

## 步骤 3: 创建 ECR 仓库（2分钟）

### 3.1 创建仓库

```bash
# 在本地或 EC2 上运行
aws ecr create-repository --repository-name desktop-pet --region us-east-1
```

### 3.2 获取仓库 URI

```bash
aws ecr describe-repositories --repository-names desktop-pet --region us-east-1
```

记录返回的 `repositoryUri`，格式类似：
```
123456789012.dkr.ecr.us-east-1.amazonaws.com/desktop-pet
```

## 步骤 4: 配置 GitHub Secrets（3分钟）

1. 打开 GitHub 仓库
2. **Settings** → **Secrets and variables** → **Actions**
3. 添加以下 Secrets：

| Secret 名称 | 说明 | 如何获取 |
|------------|------|----------|
| `AWS_ACCESS_KEY_ID` | AWS 访问密钥 ID | IAM → Users → Security credentials → Create access key |
| `AWS_SECRET_ACCESS_KEY` | AWS 秘密访问密钥 | 同上 |
| `AWS_EC2_HOST` | EC2 公网 IP | EC2 控制台 → Instances |
| `AWS_EC2_USER` | EC2 用户名 | `ubuntu` (你选择的 Ubuntu) |
| `AWS_EC2_SSH_KEY` | SSH 私钥内容 | 打开 `.pem` 文件，复制全部内容 |

### 4.1 创建 AWS 访问密钥

1. AWS 控制台 → **IAM** → **Users**
2. 选择你的用户 → **Security credentials**
3. **Create access key**
4. 选择 **Command Line Interface (CLI)**
5. 复制 **Access Key ID** 和 **Secret Access Key**

## 步骤 5: 配置 EC2 安全组（1分钟）

1. EC2 控制台 → **Security Groups**
2. 选择你的实例的安全组
3. **Edit inbound rules**
4. 添加规则：
   - **Type**: Custom TCP
   - **Port**: 8080
   - **Source**: 0.0.0.0/0（或你的 IP）

## 步骤 6: 在 EC2 上准备项目（可选）

**注意**：如果你使用 GitHub Actions 自动部署，这一步可以跳过。GitHub Actions 会自动处理。

如果你想手动部署，可以：

```bash
# SSH 连接到 EC2
ssh -i your-key.pem ubuntu@your-ec2-ip

# 克隆项目
cd ~
git clone https://github.com/your-username/AI-Desktop-Pet.git
cd AI-Desktop-Pet

# 配置 AWS 凭证（如果还没有）
aws configure
# 输入 Access Key ID 和 Secret Access Key
# 区域: us-east-1

# 创建环境变量文件
cat > .env << EOF
ECR_REGISTRY=your-ecr-registry.dkr.ecr.us-east-1.amazonaws.com
IMAGE_TAG=latest
EOF

# 使用 AWS 版本的 docker-compose
cp docker-compose.aws.yml docker-compose.yml
```

## 步骤 7: 测试部署（自动）

### 7.1 推送代码到 GitHub

```bash
git add .
git commit -m "Setup AWS deployment"
git push origin main
```

### 7.2 查看 GitHub Actions

1. GitHub 仓库 → **Actions** 标签页
2. 查看部署进度
3. 等待部署完成（约 5-10 分钟）

### 7.3 验证部署

```bash
# 在浏览器或命令行访问
curl http://your-ec2-ip:8080/health

# 应该返回健康状态
```

## 完成！🎉

现在每次你推送代码到 GitHub，应用会自动部署到 AWS EC2！

## 常见问题

### Q: GitHub Actions 失败？

**A**: 检查：
1. 所有 Secrets 是否正确配置
2. EC2 安全组是否允许 SSH (22)
3. SSH 密钥格式是否正确（包含 `-----BEGIN` 和 `-----END`）

### Q: 无法访问应用？

**A**: 检查：
1. EC2 安全组是否允许端口 8080
2. 容器是否运行：`docker-compose ps`
3. 查看日志：`docker-compose logs`

### Q: ECR 登录失败？

**A**: 确保：
1. AWS 凭证正确配置
2. EC2 实例有 ECR 权限（IAM 角色或 AWS CLI 凭证）

### Q: 如何手动部署？

**A**: 在 EC2 上运行：
```bash
cd ~/AI-Desktop-Pet
export ECR_REGISTRY=your-ecr-registry.dkr.ecr.us-east-1.amazonaws.com
export IMAGE_TAG=latest
./scripts/deploy-aws.sh
```

## 下一步

- 📊 设置 CloudWatch 监控
- 🔒 配置域名和 SSL 证书
- 💾 设置自动备份
- 📈 配置负载均衡（如果需要）

## 成本

使用 AWS 免费计划：
- **EC2 t2.micro**: 750 小时/月（12个月免费）
- **ECR**: 500MB 存储（12个月免费）
- **数据传输**: 15GB/月（12个月免费）

**总成本**: $0/月（在免费计划内）

## 需要帮助？

查看详细文档：[AWS_DEPLOYMENT.md](./AWS_DEPLOYMENT.md)

