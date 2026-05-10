# 快速开始指南

本指南将帮助你在5分钟内启动并运行KRET-RAG系统。

## 前置要求

- Python 3.9+ 
- pip 包管理器
- （可选）PostgreSQL - 用于持久化存储
- （可选）Redis - 用于缓存和会话存储

## 第一步：克隆或下载项目

```bash
# 如果从Git仓库克隆
git clone <repository-url>
cd kret-rag

# 或者直接解压下载的项目文件
cd kret-rag
```

## 第二步：配置环境

### rag-scheduler 配置

```bash
cd rag-scheduler

# 复制环境变量示例文件
cp .env.example .env

# 编辑 .env 文件，至少修改以下配置：
# DATABASE_URL=postgresql://user:password@localhost:5432/rag_db
# 或使用SQLite进行开发测试：
# DATABASE_URL=sqlite:///./rag_scheduler.db
```

### llm-session 配置

```bash
cd ../llm-session

# 复制环境变量示例文件
cp .env.example .env

# 编辑 .env 文件，至少修改以下配置：
# OPENAI_API_KEY=your-actual-api-key-here
# DATABASE_URL=postgresql://user:password@localhost:5432/session_db
# 或使用SQLite进行开发测试：
# DATABASE_URL=sqlite:///./llm_session.db
```

**重要**：你需要一个有效的OpenAI API密钥才能使用LLM功能。如果没有，可以：
1. 在 https://platform.openai.com 注册获取
2. 或者使用模拟模式（当前代码已包含mock响应）

## 第三步：安装依赖

### 安装 rag-scheduler 依赖

```bash
cd ../rag-scheduler
pip install -r requirements.txt
```

### 安装 llm-session 依赖

```bash
cd ../llm-session
pip install -r requirements.txt
```

## 第四步：启动服务

### 方法1：使用启动脚本（推荐）

#### Windows用户：
```bash
# 在一个终端窗口运行
start-scheduler.bat

# 在另一个终端窗口运行
start-session.bat
```

#### Linux/Mac用户：
```bash
# 给脚本添加执行权限
chmod +x start-scheduler.sh start-session.sh

# 在一个终端窗口运行
./start-scheduler.sh

# 在另一个终端窗口运行
./start-session.sh
```

### 方法2：手动启动

#### 启动 rag-scheduler

```bash
cd rag-scheduler
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 启动 llm-session

```bash
cd llm-session
uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload
```

## 第五步：验证安装

### 访问API文档

打开浏览器访问：
- rag-scheduler: http://localhost:8000/docs
- llm-session: http://localhost:9000/docs

你应该能看到FastAPI的交互式API文档界面。

### 测试健康检查

```bash
# 测试 rag-scheduler
curl http://localhost:8000/health

# 应该返回: {"status":"healthy"}

# 测试 llm-session
curl http://localhost:9000/health

# 应该返回: {"status":"healthy"}
```

## 第六步：第一次使用

### 1. 上传一个文档到 rag-scheduler

创建一个测试文本文件 `test.txt`：
```
机器学习是人工智能的一个分支，它使计算机能够从数据中学习，
而无需进行明确的编程。机器学习算法构建数学模型样本数据，
称为训练数据，以便进行预测或决策。
```

上传文件：
```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@test.txt" \
  -F 'metadata={"category": "test"}'
```

### 2. 查询文档

```bash
curl -X POST "http://localhost:8000/query/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "什么是机器学习？",
    "top_k": 3,
    "score_threshold": 0.5
  }'
```

### 3. 创建会话并在 llm-session 中聊天

创建会话：
```bash
curl -X POST "http://localhost:9000/sessions/" \
  -H "Content-Type: application/json" \
  -d '{
    "session_name": "我的第一个会话"
  }'
```

发送消息：
```bash
curl -X POST "http://localhost:9000/chat/message" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你好！请介绍一下你自己",
    "session_id": "<从上一步获得的session_id>"
  }'
```

## 常见问题

### Q: 遇到数据库连接错误

A: 确保你正确配置了DATABASE_URL。对于开发环境，建议使用SQLite：
```
DATABASE_URL=sqlite:///./rag_scheduler.db  # rag-scheduler
DATABASE_URL=sqlite:///./llm_session.db    # llm-session
```

### Q: OpenAI API调用失败

A: 检查以下几点：
1. 确认OPENAI_API_KEY已正确设置在.env文件中
2. 确认网络连接正常
3. 查看llm-service.py中的错误处理，当前会fallback到mock响应

### Q: 端口被占用

A: 修改.env文件中的PORT配置，或在启动时指定不同端口：
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### Q: 导入错误

A: 确保已安装所有依赖：
```bash
pip install -r requirements.txt
```

## 下一步

现在你已经成功运行了KRET-RAG系统，可以：

1. 📖 阅读 [README.md](README.md) 了解完整功能
2. 🔧 查看 [ARCHITECTURE.md](ARCHITECTURE.md) 深入理解架构
3. 📝 参考 [API_EXAMPLES.md](API_EXAMPLES.md) 学习API使用
4. 💻 探索代码结构，根据需求定制功能

## 项目结构回顾

```
kret-rag/
├── rag-scheduler/          # RAG调度器（端口8000）
│   ├── app/
│   │   ├── main.py        # 入口文件
│   │   ├── core/          # 配置
│   │   ├── models/        # 数据模型
│   │   ├── services/      # 业务逻辑
│   │   └── routes/        # API路由
│   └── requirements.txt
│
├── llm-session/           # LLM会话管理器（端口9000）
│   ├── app/
│   │   ├── main.py        # 入口文件
│   │   ├── core/          # 配置
│   │   ├── models/        # 数据模型
│   │   ├── services/      # 业务逻辑
│   │   └── routes/        # API路由
│   └── requirements.txt
│
└── README.md              # 项目总览
```

## 获取帮助

如果遇到问题：
1. 检查控制台输出的错误信息
2. 查看日志文件（如果有）
3. 参考API文档 http://localhost:8000/docs 和 http://localhost:9000/docs
4. 查阅本文档的常见问题部分

祝你使用愉快！🚀
