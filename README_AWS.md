# AWS 部署快速参考

## 🚀 一键部署到 AWS（免费）

### 前提条件
- ✅ AWS 账户（免费计划）
- ✅ GitHub 仓库
- ✅ 5 分钟时间

### 快速步骤

1. **创建 EC2 实例**
   - 类型: t2.micro（免费）
   - AMI: Amazon Linux 2023
   - 安全组: 开放 22 和 8080 端口

2. **在 EC2 上安装软件**
   ```bash
   ssh -i your-key.pem ec2-user@your-ec2-ip
   curl -o setup.sh https://raw.githubusercontent.com/your-repo/scripts/setup-aws-ec2.sh
   chmod +x setup.sh && ./setup.sh
   ```

3. **创建 ECR 仓库**
   ```bash
   aws ecr create-repository --repository-name desktop-pet --region us-east-1
   ```

4. **配置 GitHub Secrets**
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_EC2_HOST` (EC2 IP)
   - `AWS_EC2_USER` (ec2-user)
   - `AWS_EC2_SSH_KEY` (SSH 私钥内容)

5. **推送代码**
   ```bash
   git push origin main
   ```

6. **完成！** 🎉
   - GitHub Actions 自动构建和部署
   - 访问: `http://your-ec2-ip:8080`

### 详细文档
- [快速开始](docs/AWS_QUICK_START.md)
- [完整指南](docs/AWS_DEPLOYMENT.md)

### 成本
**$0/月** - 完全免费（AWS 免费计划）

