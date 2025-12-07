# EC2 设置 - 超简单版（Ubuntu）

## 🎯 你要做什么？

在 AWS EC2 Ubuntu 服务器上安装 Docker，这样 GitHub Actions 就可以自动部署你的应用了。

---

## 📝 步骤（复制粘贴即可）

### 1️⃣ 连接到 EC2

打开 PowerShell 或 CMD，运行：

```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

**替换**：
- `your-key.pem` → 你的密钥文件路径
- `your-ec2-ip` → EC2 的公网 IP

### 2️⃣ 安装所有软件（一条一条复制）

连接成功后，**一条一条**复制粘贴：

```bash
sudo apt-get update
```

```bash
sudo apt-get install docker.io docker-compose awscli git curl -y
```

```bash
sudo systemctl start docker
```

```bash
sudo systemctl enable docker
```

```bash
sudo usermod -aG docker ubuntu
```

### 3️⃣ 退出并重新登录

```bash
exit
```

然后重新连接：

```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### 4️⃣ 测试安装

```bash
docker --version
docker-compose --version
aws --version
```

如果都显示版本号，就成功了！✅

### 5️⃣ 配置 AWS（需要你的 Access Key）

```bash
aws configure
```

输入：
- Access Key ID: [你的 AWS Access Key]
- Secret Access Key: [你的 AWS Secret Key]
- Region: `us-east-1`（或你选择的区域）
- Output format: `json`（直接回车）

---

## ✅ 完成！

现在你的 EC2 已经准备好了。

**下一步**：
1. 创建 ECR 仓库（见下面）
2. 配置 GitHub Secrets
3. 推送代码！

---

## 🔧 创建 ECR 仓库

```bash
aws ecr create-repository --repository-name desktop-pet --region us-east-1
```

---

## ❓ 关于 Minikube

**Minikube 是本地 Kubernetes**，用于：
- ✅ 本地开发测试
- ✅ 学习 Kubernetes

**EC2 部署是云服务器**，用于：
- ✅ 生产环境
- ✅ 公网访问
- ✅ 自动 CI/CD

**你现在不需要 Minikube**，直接用 Docker Compose 在 EC2 上部署更简单！

---

## 🆘 遇到问题？

1. **无法连接 EC2**？
   - 检查安全组是否开放端口 22
   - 检查密钥文件路径是否正确

2. **Docker 需要 sudo**？
   - 退出并重新登录 SSH

3. **AWS 配置失败**？
   - 检查 Access Key 是否正确
   - 检查区域名称是否正确

