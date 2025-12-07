# Ubuntu EC2 安装指南

## 📋 关于 Minikube 和 EC2 部署

### Minikube vs EC2 部署

| 特性 | Minikube（本地） | EC2 部署（云） |
|------|-----------------|---------------|
| **位置** | 你的电脑上 | AWS 云服务器 |
| **用途** | 本地开发测试 | 生产环境/公网访问 |
| **成本** | 免费 | AWS 免费计划（12个月） |
| **访问** | 只能本地访问 | 可以从任何地方访问 |
| **CI/CD** | 手动部署 | GitHub Actions 自动部署 |

**结论**：
- **Minikube**：适合本地开发和测试 Kubernetes
- **EC2 + Docker Compose**：适合生产部署，更简单，免费

你现在要做的是 **EC2 部署**，不需要 Minikube。

---

## 🚀 Ubuntu EC2 安装步骤（超简单版）

### 步骤 1: 连接到你的 EC2 实例

```bash
# Windows PowerShell 或 CMD
ssh -i your-key.pem ubuntu@your-ec2-ip

# 如果提示权限错误，先设置权限（Linux/Mac）
chmod 400 your-key.pem
ssh -i your-key.pem ubuntu@your-ec2-ip
```

**替换**：
- `your-key.pem` → 你的密钥文件名（如 `my-key.pem`）
- `your-ec2-ip` → 你的 EC2 公网 IP（如 `54.123.45.67`）

### 步骤 2: 在 EC2 上安装软件（复制粘贴即可）

连接成功后，**一条一条**复制粘贴以下命令：

```bash
# 1. 更新系统
sudo apt-get update
sudo apt-get upgrade -y

# 2. 安装 Docker
sudo apt-get install docker.io -y

# 3. 启动 Docker 服务
sudo systemctl start docker
sudo systemctl enable docker

# 4. 将当前用户添加到 docker 组（这样不需要每次都 sudo）
sudo usermod -aG docker ubuntu

# 5. 安装 Docker Compose
sudo apt-get install docker-compose -y

# 6. 安装 AWS CLI
sudo apt-get install awscli -y

# 7. 安装 Git（如果还没有）
sudo apt-get install git -y

# 8. 安装 curl（如果还没有）
sudo apt-get install curl -y
```

### 步骤 3: 退出并重新登录（重要！）

```bash
# 退出 SSH
exit

# 重新连接（使 Docker 权限生效）
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### 步骤 4: 验证安装

重新登录后，运行：

```bash
# 检查 Docker（不需要 sudo）
docker --version

# 检查 Docker Compose
docker-compose --version

# 检查 AWS CLI
aws --version

# 检查 Git
git --version
```

如果都显示版本号，说明安装成功！✅

### 步骤 5: 配置 AWS 凭证

```bash
# 配置 AWS（需要你的 Access Key）
aws configure

# 会提示输入：
# AWS Access Key ID: [输入你的 Access Key ID]
# AWS Secret Access Key: [输入你的 Secret Key]
# Default region name: us-east-1（或你选择的区域）
# Default output format: json（直接回车）
```

**如何获取 AWS Access Key**：
1. AWS 控制台 → IAM → Users → 你的用户
2. Security credentials → Create access key
3. 复制 Access Key ID 和 Secret Access Key

### 步骤 6: 克隆项目到 EC2

```bash
# 创建项目目录
mkdir -p ~/projects
cd ~/projects

# 克隆你的项目（替换为你的 GitHub 仓库地址）
git clone https://github.com/your-username/AI-Desktop-Pet.git
cd AI-Desktop-Pet
```

### 步骤 7: 准备部署环境

```bash
# 创建 .env 文件（稍后 GitHub Actions 会自动部署，这里先准备）
cat > .env << 'EOF'
ECR_REGISTRY=your-ecr-registry.dkr.ecr.us-east-1.amazonaws.com
IMAGE_TAG=latest
EOF

# 复制 AWS 版本的 docker-compose
cp docker-compose.aws.yml docker-compose.yml
```

---

## ✅ 完成！

现在你的 EC2 已经准备好了！

**下一步**：
1. 创建 ECR 仓库（见下面的命令）
2. 配置 GitHub Secrets
3. 推送代码，自动部署！

---

## 🔧 创建 ECR 仓库

在 EC2 上或本地运行：

```bash
# 创建 ECR 仓库
aws ecr create-repository --repository-name desktop-pet --region us-east-1

# 获取仓库 URI（记录下来，后面要用）
aws ecr describe-repositories --repository-names desktop-pet --region us-east-1
```

会返回类似这样的 URI：
```
123456789012.dkr.ecr.us-east-1.amazonaws.com/desktop-pet
```

---

## 🐛 常见问题

### Q: 提示 "Permission denied"？

**A**: 确保：
1. 密钥文件权限正确：`chmod 400 your-key.pem`
2. 用户名正确：Ubuntu 用 `ubuntu`，不是 `ec2-user`

### Q: Docker 命令需要 sudo？

**A**: 退出 SSH 并重新登录，使 Docker 组权限生效。

### Q: AWS CLI 配置失败？

**A**: 确保：
1. Access Key 和 Secret Key 正确
2. 区域名称正确（如 `us-east-1`）

### Q: Git clone 失败？

**A**: 如果是私有仓库，需要配置 SSH 密钥或使用 HTTPS 带用户名密码。

---

## 📝 快速检查清单

- [ ] 成功 SSH 连接到 EC2
- [ ] Docker 安装成功（`docker --version`）
- [ ] Docker Compose 安装成功（`docker-compose --version`）
- [ ] AWS CLI 安装成功（`aws --version`）
- [ ] AWS 凭证配置成功（`aws configure`）
- [ ] 项目克隆成功
- [ ] ECR 仓库创建成功

全部完成？继续下一步：配置 GitHub Secrets！

