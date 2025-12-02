# 前后端分离 - 快速开始指南

## ✅ 文件已复制完成

现在可以开始测试前后端分离是否成功！

## 🧪 第一步：测试代码

运行测试脚本检查代码是否正确：

```bash
python test_separation.py
```

这个脚本会检查：
- ✅ 后端代码是否可以正常导入
- ✅ 客户端代码是否可以正常导入  
- ✅ API客户端功能是否正常

## 🚀 第二步：启动后端

在**第一个终端**启动后端API服务器：

```bash
# 使用Mock模式（不消耗API token，用于测试）
export USE_MOCK_AI=true
export API_MODE=true

# 启动后端
python run.py --api

# 或者直接
python run.py --api
```

你应该看到：
```
🚀 Starting API server mode on 0.0.0.0:8080
📝 API docs available at http://0.0.0.0:8080/docs
✓ Using Mock AI Provider (no API tokens consumed)
```

后端启动后，可以访问：
- API文档: http://localhost:8080/docs
- 健康检查: http://localhost:8080/health

## 🖥️ 第三步：启动客户端

在**第二个终端**启动客户端GUI：

```bash
# 设置后端API地址（如果后端不在localhost:8080）
export API_BASE_URL=http://localhost:8080

# 启动客户端
python run.py
```

你应该看到GUI窗口弹出！

## 🧪 测试完整流程

1. **后端健康检查**
   ```bash
   curl http://localhost:8080/health
   ```
   应该返回: `{"status":"healthy","version":"2.0.0"}`

2. **发送测试消息**
   在GUI中输入消息，应该能收到回复（Mock模式下是模拟回复）

3. **检查多用户隔离**
   - 每个用户有独立的user_id
   - 数据存储在 `./data/users/{user_id}/`

## 🔧 常见问题

### 问题1: 客户端无法连接后端

**错误**: `Cannot connect to backend API`

**解决**:
1. 确认后端正在运行（`python run.py --api`）
2. 检查 `API_BASE_URL` 环境变量是否正确
3. 检查防火墙是否阻止了连接

### 问题2: 导入错误

**错误**: `ModuleNotFoundError`

**解决**:
1. 确保所有文件都已复制到 `client/src/presentation/`
2. 确保 `client/src/infrastructure/config_manager.py` 存在
3. 检查Python路径是否正确

### 问题3: 后端启动失败

**错误**: 后端无法启动

**解决**:
1. 检查依赖是否安装: `pip install -r backend/requirements.txt`
2. 检查端口8080是否被占用
3. 查看错误日志

## 📊 验证分离成功

前后端分离成功的标志：

✅ **客户端**:
- 不直接导入 `domain.ai.providers`
- 不直接导入 `infrastructure.memory.vector_store`
- 所有AI调用都通过 `APIClient.chat()`

✅ **后端**:
- 独立的FastAPI服务器
- 支持多用户（每个user_id独立数据）
- 可以独立部署到Docker/K8s

## 🎯 下一步

1. ✅ 前后端代码分离完成
2. ⏳ 测试前后端通信
3. ⏳ Docker化后端
4. ⏳ K8s部署

## 📝 环境变量参考

### 后端环境变量
```bash
API_MODE=true                    # 启用API模式
PORT=8080                        # 端口
HOST=0.0.0.0                     # 监听地址
USE_MOCK_AI=true                 # 使用Mock AI（测试用）
AI_PROVIDER=openai               # AI Provider
OPENAI_API_KEY=sk-...            # OpenAI API Key
```

### 客户端环境变量
```bash
API_BASE_URL=http://localhost:8080  # 后端API地址
USER_ID=your-user-id                # 用户ID（可选，自动生成）
```

