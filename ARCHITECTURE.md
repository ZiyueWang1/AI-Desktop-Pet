# AI Desktop Pet - 架构设计文档

## 1. 架构概览

### 1.1 设计原则

本项目采用**事件驱动的模块化架构**，遵循以下核心原则：

- **关注点分离**：UI、业务逻辑、数据存储完全解耦
- **高内聚、低耦合**：模块通过事件总线和接口通信，避免直接依赖
- **微服务就绪**：虽然当前是单体应用，但架构支持未来拆分为微服务
- **云原生**：支持Docker容器化和Kubernetes编排
- **可扩展性**：预留扩展点，支持桌面监控、内容检测等未来功能
- **可测试性**：各模块独立可测，依赖可注入和模拟

### 1.2 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                      Presentation Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐  │
│  │ Floating UI  │  │ System Tray  │  │ Notification       │  │
│  │  (PyQt6)     │  │              │  │ Manager            │  │
│  └──────┬───────┘  └──────┬───────┘  └─────────┬──────────┘  │
└─────────┼──────────────────┼────────────────────┼─────────────┘
          │                  │                    │
          └──────────────────┴────────────────────┘
                             │
┌─────────────────────────────┴───────────────────────────────────┐
│                      Application Layer                          │
│  ┌─────────────────┐  ┌──────────────────┐  ┌───────────────┐ │
│  │ Conversation    │  │ Proactive        │  │ Personality   │ │
│  │ Manager         │  │ Engagement       │  │ Engine        │ │
│  │                 │  │ Scheduler        │  │               │ │
│  └────────┬────────┘  └────────┬─────────┘  └───────┬───────┘ │
└───────────┼──────────────────────┼────────────────────┼─────────┘
            │                      │                    │
            └──────────────────────┴────────────────────┘
                                   │
┌──────────────────────────────────┴──────────────────────────────┐
│                         Domain Layer                            │
│  ┌────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │ AI Engine  │  │ Memory       │  │ User Profile           │ │
│  │ Service    │  │ System       │  │ Service                │ │
│  │            │  │              │  │                        │ │
│  │ • Claude   │  │ • Short-term │  │ • Name extraction      │ │
│  │ • OpenAI   │  │ • Long-term  │  │ • Trait tracking       │ │
│  └─────┬──────┘  │   (ChromaDB) │  │ • Important facts      │ │
│        │         │ • Embedding  │  │ • Auto-update (5 conv) │ │
│        │         └──────┬───────┘  └────────┬───────────────┘ │
│        │                │                   │                  │
│  ┌─────┴────────────────┴───────────────────┴───────────────┐ │
│  │          Future Extension Points (Reserved)              │ │
│  │  ┌──────────────────┐  ┌─────────────────────────────┐  │ │
│  │  │ Desktop Activity │  │ Content Detection Service   │  │ │
│  │  │ Monitor Service  │  │ • Screen content analysis   │  │ │
│  │  │ • App tracking   │  │ • Context extraction        │  │ │
│  │  │ • File tracking  │  │ • Mood detection            │  │ │
│  │  │ • Workflow detect│  │                             │  │ │
│  │  └──────────────────┘  └─────────────────────────────┘  │ │
│  └──────────────────────────────────────────────────────────┘ │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌───────────────────────────────┴─────────────────────────────────┐
│                    Infrastructure Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │ Event Bus    │  │ Data Store   │  │ External APIs        │ │
│  │              │  │              │  │                      │ │
│  │ • Pub/Sub    │  │ • JSON Store │  │ • OpenAI API Client  │ │
│  │ • Async      │  │ • ChromaDB   │  │ • Claude API Client  │ │
│  │ • Event Log  │  │ • Cache      │  │ • Embedding API      │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │ Config Mgmt  │  │ Logger       │  │ Metrics & Monitoring │ │
│  │              │  │              │  │ • Prometheus metrics │ │
│  │ • Env vars   │  │ • Structured │  │ • Health checks      │ │
│  │ • Secrets    │  │ • Log levels │  │                      │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 2. 核心模块设计

### 2.1 表示层（Presentation Layer）

#### 2.1.1 Floating UI (PyQt6)
- **职责**：展示聊天界面、接收用户输入、显示AI回复
- **组件**：
  - `FloatingWindow`: 主窗口类（300x400px，always-on-top）
  - `ChatWidget`: 聊天消息展示区域
  - `InputWidget`: 文本输入框（支持Enter发送、Shift+Enter换行）
  - `ThinkingIndicator`: 思考中动画

#### 2.1.2 System Tray
- **职责**：系统托盘图标，提供快速访问菜单
- **功能**：
  - 显示/隐藏主窗口
  - 快速设置
  - 退出应用

#### 2.1.3 Notification Manager
- **职责**：管理系统通知（主动对话提醒）
- **功能**：
  - 桌面通知
  - 声音提醒（可选）

### 2.2 应用层（Application Layer）

#### 2.2.1 Conversation Manager
- **职责**：管理对话流程、协调AI引擎和记忆系统
- **核心功能**：
  ```python
  class ConversationManager:
      async def send_message(self, user_message: str) -> str:
          """
          处理用户消息：
          1. 存储用户消息到短期记忆
          2. 从记忆系统获取上下文（最近20条 + 相关长期记忆）
          3. 从用户档案获取个人信息
          4. 调用AI引擎生成回复
          5. 存储AI回复到记忆系统
          6. 更新用户档案（如需要）
          7. 返回AI回复
          """
          pass

      async def handle_user_input(self, message: str):
          """处理用户输入，触发对话流程"""
          pass

      def get_conversation_context(self) -> ConversationContext:
          """获取当前对话上下文"""
          pass
  ```

#### 2.2.2 Proactive Engagement Scheduler
- **职责**：主动发起对话、定时检查用户状态
- **核心功能**：
  ```python
  class ProactiveScheduler:
      def schedule_check_in(self, interval: timedelta):
          """安排定时检查（例如每2小时）"""
          pass

      async def initiate_conversation(self, trigger: str):
          """
          主动发起对话：
          - startup: 启动问候
          - periodic: 定期检查
          - achievement: 庆祝成就（基于用户档案）
          - reminder: 提醒承诺事项
          """
          pass

      def should_interrupt(self) -> bool:
          """判断是否应该打断用户（未来结合桌面活动监控）"""
          pass
  ```

#### 2.2.3 Personality Engine
- **职责**：管理AI个性、调整回复风格
- **核心功能**：
  ```python
  class PersonalityEngine:
      def load_personality(self) -> PersonalityConfig:
          """加载用户自定义个性"""
          pass

      def build_system_prompt(self) -> str:
          """
          构建系统提示词：
          - 基础个性描述
          - 角色设定
          - 回复风格指南
          """
          pass

      def update_personality(self, description: str):
          """更新个性配置"""
          pass
  ```

### 2.3 领域层（Domain Layer）

#### 2.3.1 AI Engine Service
- **职责**：封装AI API调用，支持多个提供商
- **设计模式**：策略模式（可替换AI提供商）
- **核心接口**：
  ```python
  class AIProvider(ABC):
      @abstractmethod
      async def generate_response(
          self,
          messages: list[Message],
          system_prompt: str,
          **kwargs
      ) -> str:
          """生成AI回复"""
          pass

  class ClaudeProvider(AIProvider):
      """Claude API实现"""
      pass

  class OpenAIProvider(AIProvider):
      """OpenAI API实现"""
      pass

  class AIEngineService:
      def __init__(self, provider: AIProvider):
          self.provider = provider

      async def chat(
          self,
          conversation_context: ConversationContext,
          user_profile: UserProfile,
          personality: PersonalityConfig
      ) -> AIResponse:
          """
          生成AI回复：
          1. 构建消息历史（最近20条 + 相关长期记忆）
          2. 构建系统提示（个性 + 用户档案）
          3. 调用AI提供商
          4. 返回结构化回复
          """
          pass
  ```

#### 2.3.2 Memory System
- **职责**：管理对话记忆（短期+长期）和语义检索
- **组件**：

  **A. Short-term Memory（短期记忆）**
  ```python
  class ShortTermMemory:
      def __init__(self, max_messages: int = 20):
          self.messages: deque[Message] = deque(maxlen=max_messages)

      def add_message(self, message: Message):
          """添加消息（自动维护20条窗口）"""
          pass

      def get_recent_messages(self) -> list[Message]:
          """获取最近消息"""
          pass

      def clear(self):
          """清空短期记忆"""
          pass
  ```

  **B. Long-term Memory（长期记忆）**
  ```python
  class LongTermMemory:
      def __init__(self, chromadb_path: str):
          self.collection = chromadb.PersistentClient(path=chromadb_path)
          self.embedding_model = "text-embedding-3-small"

      async def store_conversation(self, message: Message):
          """
          存储对话到ChromaDB：
          1. 生成embedding（使用OpenAI embedding API）
          2. 存储到向量数据库（带元数据：时间戳、角色等）
          """
          pass

      async def retrieve_relevant(
          self,
          query: str,
          top_k: int = 3
      ) -> list[Message]:
          """
          语义检索相关对话：
          1. 生成查询embedding
          2. 在ChromaDB中检索top_k相似对话
          3. 返回相关历史
          """
          pass

      async def search_by_metadata(
          self,
          filters: dict
      ) -> list[Message]:
          """按元数据搜索（例如：特定时间段、特定主题）"""
          pass
  ```

  **C. Memory Manager（记忆管理器）**
  ```python
  class MemoryManager:
      def __init__(
          self,
          short_term: ShortTermMemory,
          long_term: LongTermMemory
      ):
          self.short_term = short_term
          self.long_term = long_term

      async def add_message(self, message: Message):
          """同时添加到短期和长期记忆"""
          self.short_term.add_message(message)
          await self.long_term.store_conversation(message)

      async def get_context_for_ai(
          self,
          current_query: str
      ) -> ConversationContext:
          """
          为AI获取完整上下文：
          1. 获取最近20条消息（短期记忆）
          2. 检索相关历史对话（长期记忆，top 3）
          3. 合并返回
          """
          recent = self.short_term.get_recent_messages()
          relevant = await self.long_term.retrieve_relevant(current_query, top_k=3)
          return ConversationContext(recent=recent, relevant=relevant)
  ```

#### 2.3.3 User Profile Service
- **职责**：管理用户档案（姓名、特征、重要事实）
- **核心功能**：
  ```python
  class UserProfile:
      name: Optional[str]
      personality_traits: list[str]
      important_facts: dict[str, any]  # {fact_type: value}
      goals: list[str]
      commitments: list[str]
      preferences: dict[str, any]
      significant_dates: dict[str, str]
      last_updated: datetime
      conversation_count: int

  class UserProfileService:
      def __init__(self, storage_path: str):
          self.storage_path = storage_path
          self.profile: UserProfile = self.load_profile()
          self.conversation_counter = 0

      async def update_profile_if_needed(self, conversation_history: list[Message]):
          """
          每5次对话更新一次档案：
          1. 检查对话计数
          2. 如果达到5次，调用AI分析对话
          3. 提取新的用户信息（姓名、特征、事实）
          4. 更新档案
          """
          self.conversation_counter += 1
          if self.conversation_counter >= 5:
              await self._extract_and_update(conversation_history)
              self.conversation_counter = 0

      async def _extract_and_update(self, history: list[Message]):
          """使用AI提取用户信息"""
          # 调用AI引擎，使用专门的提示词提取信息
          pass

      def get_profile_summary(self) -> str:
          """获取档案摘要（用于AI系统提示）"""
          pass

      def save_profile(self):
          """保存档案到JSON"""
          pass

      def load_profile(self) -> UserProfile:
          """从JSON加载档案"""
          pass
  ```

#### 2.3.4 未来扩展服务（预留接口）

**A. Desktop Activity Monitor Service**
```python
class DesktopActivityMonitor:
    """
    桌面活动监控（未来功能）：
    - 监控当前活动应用
    - 追踪打开的文件
    - 检测工作流模式
    - 识别适合打断的时机
    """

    def get_current_activity(self) -> Activity:
        """获取当前活动"""
        pass

    def detect_workflow_pattern(self) -> WorkflowPattern:
        """检测工作流模式"""
        pass

    def is_good_time_to_interrupt(self) -> bool:
        """判断是否适合打断"""
        pass
```

**B. Content Detection Service**
```python
class ContentDetectionService:
    """
    内容检测服务（未来功能）：
    - 屏幕内容分析
    - 上下文提取
    - 心情检测
    """

    async def analyze_screen_content(self) -> ContentAnalysis:
        """分析屏幕内容"""
        pass

    async def detect_user_mood(self) -> MoodState:
        """检测用户心情"""
        pass
```

### 2.4 基础设施层（Infrastructure Layer）

#### 2.4.1 Event Bus
- **职责**：模块间异步通信，解耦组件
- **设计**：
  ```python
  class EventBus:
      def __init__(self):
          self._subscribers: dict[str, list[Callable]] = {}

      def subscribe(self, event_type: str, handler: Callable):
          """订阅事件"""
          pass

      async def publish(self, event: Event):
          """发布事件（异步）"""
          pass

  # 事件类型示例
  class Event:
      event_type: str
      timestamp: datetime
      data: dict

  class UserMessageEvent(Event):
      """用户发送消息事件"""
      pass

  class AIResponseEvent(Event):
      """AI生成回复事件"""
      pass

  class ProfileUpdatedEvent(Event):
      """用户档案更新事件"""
      pass
  ```

#### 2.4.2 Data Store
- **职责**：数据持久化
- **组件**：
  - **JSON Store**：配置、个性、用户档案
  - **ChromaDB**：长期记忆向量存储
  - **Cache**：临时数据缓存（Redis，可选）

#### 2.4.3 External API Clients
- **职责**：封装外部API调用，处理认证、重试、错误
- **组件**：
  ```python
  class OpenAIClient:
      def __init__(self, api_key: str):
          self.api_key = api_key
          self.client = OpenAI(api_key=api_key)

      async def chat_completion(self, messages: list, model: str, **kwargs):
          """聊天完成API"""
          pass

      async def create_embedding(self, text: str, model: str = "text-embedding-3-small"):
          """生成embedding"""
          pass

  class ClaudeClient:
      def __init__(self, api_key: str):
          self.api_key = api_key
          self.client = Anthropic(api_key=api_key)

      async def create_message(self, messages: list, model: str, **kwargs):
          """创建消息"""
          pass
  ```

#### 2.4.4 Configuration Management
- **职责**：管理配置和密钥
- **设计**：
  ```python
  class ConfigManager:
      def __init__(self, config_path: str):
          self.config_path = config_path
          self.config = self.load_config()

      def get(self, key: str, default=None):
          """获取配置"""
          pass

      def set(self, key: str, value):
          """设置配置"""
          pass

      def get_secret(self, key: str) -> str:
          """获取密钥（支持环境变量）"""
          pass
  ```

#### 2.4.5 Logging & Monitoring
- **职责**：结构化日志、性能监控
- **组件**：
  - **Logger**：统一日志接口
  - **Metrics**：Prometheus指标（请求数、延迟、错误率）
  - **Health Check**：健康检查端点（Kubernetes就绪探针）

## 3. 数据流设计

### 3.1 用户发送消息流程

```
User Input
    │
    ↓
FloatingWindow (UI)
    │
    ↓ emit UserMessageEvent
EventBus
    │
    ↓
ConversationManager (subscribe)
    │
    ├─→ MemoryManager.add_message(user_msg)
    │   ├─→ ShortTermMemory.add_message()
    │   └─→ LongTermMemory.store_conversation()
    │
    ├─→ MemoryManager.get_context_for_ai(query)
    │   ├─→ ShortTermMemory.get_recent_messages() → 最近20条
    │   └─→ LongTermMemory.retrieve_relevant() → 相关3条
    │
    ├─→ UserProfileService.get_profile() → 用户档案
    │
    ├─→ PersonalityEngine.build_system_prompt() → 系统提示
    │
    ↓
AIEngineService.chat(context, profile, personality)
    │
    ↓
AIProvider.generate_response() → 调用OpenAI/Claude API
    │
    ↓
AI Response
    │
    ├─→ MemoryManager.add_message(ai_response)
    │   ├─→ ShortTermMemory.add_message()
    │   └─→ LongTermMemory.store_conversation()
    │
    ├─→ UserProfileService.update_if_needed()
    │   └─→ (每5次对话) AIEngine.extract_user_info()
    │
    ↓ emit AIResponseEvent
EventBus
    │
    ↓
FloatingWindow (subscribe)
    │
    ↓
Display AI Response in Chat
```

### 3.2 主动对话流程

```
ProactiveScheduler (定时器触发)
    │
    ↓
ProactiveScheduler.should_interrupt()
    │ (未来: 检查DesktopActivityMonitor)
    ↓
ProactiveScheduler.initiate_conversation(trigger)
    │
    ├─→ UserProfileService.get_profile() → 获取用户信息
    │
    ├─→ MemoryManager.get_context_for_ai() → 获取记忆
    │
    ↓
AIEngineService.generate_proactive_message(context, profile)
    │
    ↓
AI Generated Message
    │
    ↓ emit AIProactiveMessageEvent
EventBus
    │
    ↓
FloatingWindow (subscribe)
    │
    ↓ Display + Notification
User sees proactive message
```

## 4. 部署架构

### 4.1 Docker容器化

#### 4.1.1 容器设计
```dockerfile
# 多阶段构建
FROM python:3.10-slim as builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.10-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY src/ /app/src/
COPY run.py /app/

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

# 持久化数据挂载点
VOLUME ["/app/data"]

CMD ["python", "run.py"]
```

#### 4.1.2 卷挂载
- `/app/data/config.json`：应用配置
- `/app/data/personality.json`：个性配置
- `/app/data/user_profile.json`：用户档案
- `/app/data/chromadb/`：ChromaDB数据目录
- `/app/data/logs/`：日志目录

### 4.2 Kubernetes部署架构

#### 4.2.1 核心资源

**A. Deployment**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: desktop-pet
spec:
  replicas: 1  # 可通过HPA自动扩展1-5
  selector:
    matchLabels:
      app: desktop-pet
  template:
    metadata:
      labels:
        app: desktop-pet
    spec:
      containers:
      - name: desktop-pet
        image: desktop-pet:latest
        resources:
          requests:
            cpu: 200m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
        env:
        - name: AI_PROVIDER
          valueFrom:
            configMapKeyRef:
              name: desktop-pet-config
              key: ai_provider
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: desktop-pet-secrets
              key: openai_api_key
        volumeMounts:
        - name: data
          mountPath: /app/data
        - name: chromadb
          mountPath: /app/data/chromadb
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: desktop-pet-data-pvc
      - name: chromadb
        persistentVolumeClaim:
          claimName: desktop-pet-chromadb-pvc
```

**B. Service**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: desktop-pet-service
spec:
  selector:
    app: desktop-pet
  ports:
  - protocol: TCP
    port: 8080  # 健康检查端口
    targetPort: 8080
  type: ClusterIP
```

**C. HorizontalPodAutoscaler**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: desktop-pet-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: desktop-pet
  minReplicas: 1
  maxReplicas: 5
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

**D. ConfigMap**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: desktop-pet-config
data:
  ai_provider: "openai"
  log_level: "INFO"
  proactive_interval: "7200"  # 2小时（秒）
```

**E. Secret**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: desktop-pet-secrets
type: Opaque
data:
  openai_api_key: <base64-encoded-key>
  claude_api_key: <base64-encoded-key>
```

**F. PersistentVolumeClaim**
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: desktop-pet-data-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: desktop-pet-chromadb-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
```

#### 4.2.2 数据持久化策略

为了在多Pod环境下共享数据，采用以下策略：

1. **配置数据**：通过ConfigMap和Secret共享
2. **用户档案**：存储在PVC中，通过ReadWriteMany模式共享（或使用Redis/数据库）
3. **ChromaDB**：
   - **方案1（MVP）**：单独的ChromaDB服务Pod + PVC
   - **方案2（生产）**：使用托管向量数据库（Pinecone, Weaviate）

#### 4.2.3 部署到GitHub Codespaces/Minikube

```bash
# 1. 启动Minikube
minikube start --cpus=2 --memory=8192 --driver=docker

# 2. 启用指标服务器
minikube addons enable metrics-server

# 3. 构建Docker镜像
docker build -t desktop-pet:latest .

# 4. 加载镜像到Minikube
minikube image load desktop-pet:latest

# 5. 应用Kubernetes清单
kubectl apply -f k8s/

# 6. 检查部署
kubectl get pods
kubectl get hpa
```

### 4.3 负载测试架构

#### 4.3.1 测试场景
- **基线测试**：10并发用户
- **中等负载**：50并发用户
- **高负载**：100并发用户

#### 4.3.2 测试脚本（Locust）
```python
from locust import HttpUser, task, between

class DesktopPetUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def send_message(self):
        self.client.post("/api/chat", json={
            "message": "Hello, how are you?",
            "user_id": "test_user"
        })

    @task(2)
    def get_conversation(self):
        self.client.get("/api/conversation/test_user")
```

#### 4.3.3 监控指标
- **CPU使用率**：`kubectl top pods`
- **内存使用率**：`kubectl top pods`
- **HPA扩展行为**：`kubectl get hpa -w`
- **响应时间**：Locust统计
- **错误率**：Locust统计

## 5. 项目目录结构

```
AI-Desktop-Pet/
├── src/
│   ├── __init__.py
│   │
│   ├── presentation/              # 表示层
│   │   ├── __init__.py
│   │   ├── floating_window.py     # 浮动窗口
│   │   ├── chat_widget.py         # 聊天组件
│   │   ├── input_widget.py        # 输入组件
│   │   ├── system_tray.py         # 系统托盘
│   │   └── notification_manager.py # 通知管理器
│   │
│   ├── application/               # 应用层
│   │   ├── __init__.py
│   │   ├── conversation_manager.py # 对话管理器
│   │   ├── proactive_scheduler.py  # 主动对话调度
│   │   └── personality_engine.py   # 个性引擎
│   │
│   ├── domain/                    # 领域层
│   │   ├── __init__.py
│   │   ├── ai/                    # AI引擎
│   │   │   ├── __init__.py
│   │   │   ├── ai_engine.py       # AI引擎服务
│   │   │   ├── providers/         # AI提供商
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py        # 基础接口
│   │   │   │   ├── openai_provider.py
│   │   │   │   └── claude_provider.py
│   │   │   └── models.py          # 数据模型
│   │   │
│   │   ├── memory/                # 记忆系统
│   │   │   ├── __init__.py
│   │   │   ├── memory_manager.py  # 记忆管理器
│   │   │   ├── short_term.py      # 短期记忆
│   │   │   ├── long_term.py       # 长期记忆（ChromaDB）
│   │   │   └── models.py          # 数据模型
│   │   │
│   │   ├── profile/               # 用户档案
│   │   │   ├── __init__.py
│   │   │   ├── profile_service.py # 档案服务
│   │   │   └── models.py          # 数据模型
│   │   │
│   │   └── extensions/            # 未来扩展（预留）
│   │       ├── __init__.py
│   │       ├── activity_monitor.py # 桌面活动监控
│   │       └── content_detection.py # 内容检测
│   │
│   ├── infrastructure/            # 基础设施层
│   │   ├── __init__.py
│   │   ├── event_bus.py           # 事件总线
│   │   ├── config_manager.py      # 配置管理
│   │   ├── logger.py              # 日志
│   │   ├── metrics.py             # 监控指标
│   │   ├── storage/               # 数据存储
│   │   │   ├── __init__.py
│   │   │   ├── json_store.py      # JSON存储
│   │   │   ├── chromadb_client.py # ChromaDB客户端
│   │   │   └── cache.py           # 缓存
│   │   └── api_clients/           # 外部API客户端
│   │       ├── __init__.py
│   │       ├── openai_client.py
│   │       └── claude_client.py
│   │
│   └── main.py                    # 应用入口
│
├── data/                          # 数据目录（Git忽略）
│   ├── config.json
│   ├── personality.json
│   ├── user_profile.json
│   ├── chromadb/                  # ChromaDB数据
│   └── logs/                      # 日志文件
│
├── k8s/                           # Kubernetes清单
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── hpa.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   └── pvc.yaml
│
├── tests/                         # 测试
│   ├── unit/
│   ├── integration/
│   └── load/
│       └── locustfile.py
│
├── docs/                          # 文档
│   ├── API.md
│   └── DEPLOYMENT.md
│
├── Dockerfile                     # Docker镜像
├── docker-compose.yml             # 本地开发
├── requirements.txt               # 依赖
├── .env.example                   # 环境变量示例
├── run.py                         # 启动脚本
├── README.md
└── ARCHITECTURE.md                # 本文档
```

## 6. 关键技术选型

| 组件 | 技术 | 原因 |
|------|------|------|
| UI框架 | PyQt6 | 跨平台、成熟、性能好 |
| AI提供商 | OpenAI / Claude | 高质量对话能力 |
| 向量数据库 | ChromaDB | 轻量、易部署、支持本地化 |
| Embedding模型 | text-embedding-3-small | 性价比高、速度快 |
| 事件总线 | 自研（asyncio） | 轻量、满足需求 |
| 配置管理 | JSON + 环境变量 | 简单、易维护 |
| 容器化 | Docker | 标准化部署 |
| 编排 | Kubernetes | 云原生、自动扩展 |
| 日志 | Python logging | 内置、结构化 |
| 监控 | Prometheus（可选） | 云原生标准 |
| 负载测试 | Locust | Python生态、易扩展 |

## 7. 数据模型

### 7.1 Message（消息）
```python
@dataclass
class Message:
    id: str                      # 唯一标识
    role: str                    # "user" | "assistant"
    content: str                 # 消息内容
    timestamp: datetime          # 时间戳
    metadata: dict               # 元数据（例如：情绪、主题）
```

### 7.2 ConversationContext（对话上下文）
```python
@dataclass
class ConversationContext:
    recent_messages: list[Message]   # 最近20条消息
    relevant_history: list[Message]  # 相关历史（3条）
    user_profile: UserProfile        # 用户档案
    personality: PersonalityConfig   # 个性配置
```

### 7.3 UserProfile（用户档案）
```python
@dataclass
class UserProfile:
    name: Optional[str] = None
    personality_traits: list[str] = field(default_factory=list)
    important_facts: dict[str, any] = field(default_factory=dict)
    goals: list[str] = field(default_factory=list)
    commitments: list[str] = field(default_factory=list)
    preferences: dict[str, any] = field(default_factory=dict)
    significant_dates: dict[str, str] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.now)
    conversation_count: int = 0
```

### 7.4 PersonalityConfig（个性配置）
```python
@dataclass
class PersonalityConfig:
    description: str             # 个性描述
    tone: str                    # 语气（friendly, professional, etc.）
    response_style: str          # 回复风格
    custom_instructions: str     # 自定义指令
```

### 7.5 AIResponse（AI回复）
```python
@dataclass
class AIResponse:
    content: str                 # 回复内容
    model: str                   # 使用的模型
    tokens_used: int             # 使用的token数
    latency: float               # 延迟（秒）
    metadata: dict               # 其他元数据
```

## 8. 接口设计（API）

虽然MVP是桌面应用，但为了支持Kubernetes部署和未来扩展，预留HTTP API接口：

### 8.1 对话接口
```
POST /api/chat
Request:
{
    "user_id": "string",
    "message": "string"
}

Response:
{
    "response": "string",
    "conversation_id": "string",
    "timestamp": "datetime"
}
```

### 8.2 用户档案接口
```
GET /api/profile/{user_id}
Response:
{
    "name": "string",
    "personality_traits": ["trait1", "trait2"],
    "important_facts": {...},
    ...
}

PUT /api/profile/{user_id}
Request:
{
    "name": "string",
    ...
}
```

### 8.3 健康检查接口
```
GET /health
Response:
{
    "status": "healthy",
    "timestamp": "datetime",
    "services": {
        "ai_engine": "healthy",
        "memory_system": "healthy",
        "chromadb": "healthy"
    }
}
```

## 9. 扩展性设计

### 9.1 插件架构（未来）
为了支持第三方扩展，预留插件接口：

```python
class Plugin(ABC):
    @abstractmethod
    def on_message_received(self, message: Message):
        """消息接收钩子"""
        pass

    @abstractmethod
    def on_response_generated(self, response: AIResponse):
        """回复生成钩子"""
        pass

class PluginManager:
    def register_plugin(self, plugin: Plugin):
        """注册插件"""
        pass

    def load_plugins(self, plugin_dir: str):
        """加载插件目录"""
        pass
```

### 9.2 多用户支持（未来）
当前为单用户设计，未来可扩展为多用户：
- 每个用户独立的档案
- 每个用户独立的记忆空间
- 通过`user_id`隔离数据

### 9.3 多模态支持（未来）
- **语音输入**：集成语音识别（Whisper API）
- **图像理解**：支持用户上传图片（GPT-4 Vision）
- **语音输出**：TTS语音合成

## 10. 安全性设计

### 10.1 API密钥管理
- 密钥存储在Kubernetes Secret中
- 支持环境变量注入
- 不在日志中打印密钥

### 10.2 数据隐私
- 所有对话数据本地存储（ChromaDB）
- 可选：端到端加密存储
- 用户可随时删除所有数据

### 10.3 网络安全
- API接口使用HTTPS（生产环境）
- 限流保护（防止API滥用）
- 输入验证和清理

## 11. 性能优化

### 11.1 缓存策略
- **Embedding缓存**：相同文本的embedding结果缓存
- **AI回复缓存**：相似问题的回复缓存（可选）
- **用户档案缓存**：内存缓存，减少磁盘读取

### 11.2 异步处理
- 所有I/O操作异步化（API调用、数据库操作）
- 使用`asyncio`提升并发性能
- 非阻塞UI更新

### 11.3 批处理
- ChromaDB批量插入
- Embedding批量生成

## 12. 测试策略

### 12.1 单元测试
- 每个模块独立测试
- 使用Mock对象模拟依赖
- 覆盖率目标：80%+

### 12.2 集成测试
- 测试模块间交互
- 测试事件总线通信
- 测试完整对话流程

### 12.3 端到端测试
- 模拟真实用户交互
- 测试UI响应
- 测试数据持久化

### 12.4 负载测试
- 使用Locust模拟并发用户
- 测试HPA自动扩展
- 性能基准：
  - 响应时间 < 2秒（P95）
  - 错误率 < 1%
  - 支持100并发用户

## 13. 开发路线图

### Phase 1: MVP核心功能（Week 1-2）
- [x] Day 1: UI框架（已完成）
- [ ] Day 2-3: AI集成 + 记忆系统
- [ ] Day 4-5: Docker + Kubernetes部署
- [ ] Day 6-7: 负载测试

### Phase 2: 功能增强（Week 3-4）
- [ ] 主动对话优化（智能时机选择）
- [ ] 用户档案自动更新优化
- [ ] 多AI提供商支持（Claude + OpenAI切换）
- [ ] 性能优化（缓存、批处理）

### Phase 3: 扩展功能（Week 5-8）
- [ ] 桌面活动监控
- [ ] 内容检测服务
- [ ] 工作流模式识别
- [ ] 多模态支持（语音、图像）

### Phase 4: 生产就绪（Week 9-12）
- [ ] 完整测试覆盖
- [ ] 监控和告警
- [ ] 文档完善
- [ ] 生产部署

## 14. 总结

本架构设计采用**事件驱动的模块化架构**，具有以下优势：

1. **清晰的分层**：表示层、应用层、领域层、基础设施层职责明确
2. **高度解耦**：模块通过事件总线通信，避免直接依赖
3. **可扩展性强**：预留扩展点，支持桌面监控、内容检测等未来功能
4. **云原生就绪**：支持Docker容器化和Kubernetes编排
5. **易于测试**：依赖注入、接口抽象，单元测试友好
6. **性能优化**：异步I/O、缓存策略、批处理

该架构既满足当前MVP需求，又为未来扩展奠定了坚实基础。
