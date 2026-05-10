# KRET-RAG 系统

一套基于微服务架构的RAG（检索增强生成）系统，包含两个核心应用：
- **rag-scheduler**: RAG调度器 - 负责文档处理、向量检索、知识库管理
- **llm-session**: LLM会话管理器 - 负责对话管理、上下文维护、模型调用

**English Version**: [README_en.md](./README_en.md)

## 📋 项目状态

- **当前版本**: v1.0.0
- **代码质量评分**: 58/100 ⚠️
- **问题跟踪**: [查看详细问题和修复计划](./docs/ISSUES_TRACKING.md)
- **快速检查**: [日常检查清单](./docs/CHECKLIST.md)
- **已完成修复**: 1/15 (eval() 安全漏洞已修复 ✅)

---

## 📚 文档导航

### 项目级文档
- **[快速开始](./docs/QUICKSTART.md)** - 环境配置和启动指南
- **[系统架构](./docs/ARCHITECTURE.md)** - 架构设计和技术选型
- **[API 示例](./docs/API_EXAMPLES.md)** - API 使用示例和代码片段
- **[检查清单](./docs/CHECKLIST.md)** - 日常运维检查项
- **[问题跟踪](./docs/ISSUES_TRACKING.md)** - 已知问题和修复计划

### rag-scheduler 服务文档
- **[查询测试指南](./rag-scheduler/docs/QUERY_TEST_GUIDE.md)** - 可视化测试页面 ⭐
- **[文件处理流程](./rag-scheduler/docs/FILE_PROCESSING_FLOW.md)** - 文档解析和转换
- **[混合检索](./rag-scheduler/docs/HYBRID_SEARCH_RERANK.md)** - BM25 + 向量检索
- **[数据库指南](./rag-scheduler/docs/DATABASE_GUIDE.md)** - PostgreSQL配置
- **[完整文档索引](./rag-scheduler/docs/README.md)** - 所有技术文档

### 故障排查
- **[故障排查指南](./rag-scheduler/bugfixes/README.md)** - 常见问题解决方案

---

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                      KRET-RAG System                        │
├──────────────────────────┬──────────────────────────────────┤
│   rag-scheduler (8000)   │    llm-session (9000)            │
│                          │                                  │
│  ┌────────────────────┐  │  ┌────────────────────────────┐  │
│  │  Document Service  │  │  │   Session Service          │  │
│  ├────────────────────┤  │  ├────────────────────────────┤  │
│  │  Vector Service    │  │  │   LLM Service              │  │
│  ├────────────────────┤  │  ├────────────────────────────┤  │
│  │  RAG Service       │◄─┼──┼──► Chat Service            │  │
│  └────────────────────┘  │  └────────────────────────────┘  │
│                          │                                  │
│  • 文档上传与解析         │  • 会话创建与管理                 │
│  • 文本分块与向量化       │  • 对话历史维护                   │
│  • 向量相似度搜索         │  • LLM调用与流式响应             │
│  • 知识库管理             │  • 上下文管理                     │
└──────────────────────────┴──────────────────────────────────┘
                           │
                    HTTP API通信
```

## 功能特性

### rag-scheduler (RAG调度器)
- ✅ 多格式文档上传（PDF、DOCX、TXT、MD）
- ✅ 智能文本分块
- ✅ 向量存储与检索
- ✅ 相似度搜索
- ✅ 知识库管理
- ✅ 查询重写优化
- ✅ 混合检索（BM25 + 向量）
- ✅ Rerank重排序
- ✅ 可视化测试页面 ⭐

### llm-session (LLM会话管理器)
- ✅ 多会话管理
- ✅ 对话历史维护
- ✅ 上下文感知
- ✅ LLM集成（OpenAI、Azure等）
- ✅ 流式响应支持

## 🚀 快速开始

### 1. 环境要求
- Python 3.10+
- PostgreSQL 14+
- Redis (可选，用于缓存)

### 2. 安装依赖

#### rag-scheduler
```bash
cd rag-scheduler
pip install -r requirements.txt
```

#### llm-session
```bash
cd llm-session
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env` 并修改配置：

```bash
# rag-scheduler
cp rag-scheduler/.env.example rag-scheduler/.env

# llm-session
cp llm-session/.env.example llm-session/.env
```

**重要**: 如果遇到网络问题（连接 huggingface.co 超时），请在 `.env` 文件中添加：
``env
HF_ENDPOINT=https://hf-mirror.com
```

详见 [故障排查指南](./rag-scheduler/bugfixes/TROUBLESHOOTING.md)

### 4. 启动服务

#### 方式1：使用启动脚本（推荐）
```bash
# Windows
start-scheduler.bat
start-llm-session.bat

# Linux/Mac
./start-scheduler.sh
./start-llm-session.sh
```

#### 方式2：手动启动
```bash
# 启动 rag-scheduler
cd rag-scheduler
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 启动 llm-session
cd llm-session
uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload
```

### 5. 访问API文档和测试页面

- **rag-scheduler API文档**: http://localhost:8000/docs
- **rag-scheduler 上传测试**: http://localhost:8000/
- **rag-scheduler 查询测试**: http://localhost:8000/test-query ⭐ 新增
- **llm-session API文档**: http://localhost:9000/docs

## API端点

### rag-scheduler (端口 8000)

#### 文档管理
- `POST /documents/upload` - 上传文档
- `GET /documents/{document_id}` - 获取文档信息
- `DELETE /documents/{document_id}` - 删除文档
- `GET /documents/` - 列出所有文档

#### 查询
- `POST /query/` - 查询文档并生成答案
- `POST /query/search` - 仅执行向量搜索
- `POST /query/generate` - 完整RAG生成回答

**测试页面**: http://localhost:8000/test-query - 可视化测试所有查询功能 ⭐

### llm-session (端口 9000)

#### 会话管理
- `POST /sessions/` - 创建会话
- `GET /sessions/{session_id}` - 获取会话信息
- `DELETE /sessions/{session_id}` - 删除会话
- `POST /sessions/{session_id}/close` - 关闭会话
- `GET /sessions/` - 列出所有会话

#### 聊天
- `POST /chat/message` - 发送消息并获取完整响应
- `POST /chat/stream` - 发送消息并获取流式响应

## 技术栈

### rag-scheduler
- **Web框架**: FastAPI
- **数据库**: PostgreSQL + SQLAlchemy
- **向量数据库**: ChromaDB (可扩展 Milvus、Qdrant)
- **Embedding**: Sentence Transformers
- **文档处理**: PyPDF, python-docx

### llm-session
- **Web框架**: FastAPI
- **数据库**: PostgreSQL + SQLAlchemy
- **缓存**: Redis
- **LLM**: OpenAI GPT (可扩展 Azure、Claude等)
- **HTTP客户端**: HTTPX

## 项目结构

```
kret-rag/
├── rag-scheduler/                # RAG调度器
│   ├── app/
│   │   ├── main.py              # 应用入口
│   │   ├── core/                # 核心模块
│   │   │   ├── config.py       # 配置管理
│   │   │   └── __init__.py
│   │   ├── models/              # 数据模型
│   │   │   ├── schemas.py      # Pydantic模型
│   │   │   └── __init__.py
│   │   ├── db/                  # 数据库
│   │   │   ├── database.py     # 数据库连接
│   │   │   └── __init__.py
│   │   ├── services/            # 业务服务
│   │   │   ├── document_service.py
│   │   │   ├── vector_service.py
│   │   │   ├── rag_service.py
│   │   │   └── __init__.py
│   │   └── routes/              # API路由
│   │       ├── documents.py
│   │       ├── query.py
│   │       └── __init__.py
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
├── llm-session/                  # LLM会话管理器
│   ├── app/
│   │   ├── main.py              # 应用入口
│   │   ├── core/                # 核心模块
│   │   │   ├── config.py       # 配置管理
│   │   │   └── __init__.py
│   │   ├── models/              # 数据模型
│   │   │   ├── schemas.py      # Pydantic模型
│   │   │   └── __init__.py
│   │   ├── services/            # 业务服务
│   │   │   ├── session_service.py
│   │   │   ├── llm_service.py
│   │   │   ├── chat_service.py
│   │   │   └── __init__.py
│   │   └── routes/              # API路由
│   │       ├── sessions.py
│   │       ├── chat.py
│   │       └── __init__.py
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
└── README.md                     # 项目总览
```

## 后续开发计划

### 短期优化
- [ ] 完善数据库模型定义
- [ ] 实现真实的LLM调用
- [ ] 添加用户认证与授权
- [ ] 增加日志记录
- [ ] 编写单元测试

### 中期扩展
- [ ] 支持更多向量数据库
- [ ] 支持更多LLM提供商
- [ ] 添加Rerank机制
- [ ] 实现混合检索
- [ ] 添加监控和指标采集

### 长期规划
- [ ] 分布式部署支持
- [ ] 负载均衡
- [ ] 水平扩展能力
- [ ] 多租户支持
- [ ] 可视化界面

## 许可证

MIT License
