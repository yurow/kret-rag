# KRET-RAG 系统架构详解

## 整体架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Client Applications                          │
│                    (Web / Mobile / API Clients)                     │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                    HTTP/REST API
                         │
        ┌────────────────┴────────────────┐
        │                                 │
        ▼                                 ▼
┌──────────────────────────┐    ┌──────────────────────────┐
│   rag-scheduler          │    │   llm-session            │
│   (Port: 8000)           │    │   (Port: 9000)           │
│                          │    │                          │
│  ┌────────────────────┐  │    │  ┌────────────────────┐  │
│  │   API Routes       │  │    │  │   API Routes       │  │
│  │  /documents        │  │    │  │  /sessions         │  │
│  │  /query            │  │    │  │  /chat             │  │
│  └────────┬───────────┘  │    │  └────────┬───────────┘  │
│           │              │    │           │              │
│  ┌────────▼───────────┐  │    │  ┌────────▼───────────┐  │
│  │   Services         │  │    │  │   Services         │  │
│  │ • DocumentService  │  │    │  │ • SessionService   │  │
│  │ • VectorService    │  │    │  │ • LLMService       │  │
│  │ • RAGService       │  │    │  │ • ChatService      │  │
│  └────────┬───────────┘  │    │  └────────┬───────────┘  │
│           │              │    │           │              │
│  ┌────────▼───────────┐  │    │  ┌────────▼───────────┐  │
│  │   Data Layer       │  │    │  │   Data Layer       │  │
│  │ • PostgreSQL       │  │    │  │ • PostgreSQL       │  │
│  │ • ChromaDB         │  │    │  │ • Redis            │  │
│  │ • (Vector Store)   │  │    │  │ • (Session Store)  │  │
│  └────────────────────┘  │    │  └────────────────────┘  │
└──────────────────────────┘    └──────────────────────────┘
        │                                 │
        │                                 │
        └─────────────┬───────────────────┘
                      │
                 HTTP Communication
                      │
        ┌─────────────▼───────────────────┐
        │     External LLM Providers      │
        │  (OpenAI / Azure / Claude etc.) │
        └─────────────────────────────────┘
```

## rag-scheduler 详细架构

### 组件说明

1. **Document Service (文档服务)**
   - 职责：文档上传、解析、分块
   - 功能：
     - 文件格式验证（PDF、DOCX、TXT、MD）
     - 文件大小限制检查
     - 文本提取
     - 智能分块（支持固定大小、段落、句子分块）

2. **Vector Service (向量服务)**
   - 职责：文本向量化、存储、检索
   - 功能：
     - Embedding生成（Sentence Transformers）
     - 向量存储（ChromaDB/Milvus/Qdrant）
     - 相似度搜索（余弦相似度）
     - 向量过滤和排序

3. **RAG Service (RAG服务)**
   - 职责：检索增强生成流程控制
   - 功能：
     - 查询向量化
     - 文档检索
     - 上下文构建
     - 调用LLM服务
     - 结果整合

### 数据流

```
用户上传文档
    ↓
DocumentService.upload_document()
    ↓
验证 → 提取文本 → 分块
    ↓
VectorService.store_chunks()
    ↓
生成Embedding → 存储到向量数据库
    ↓
返回document_id

---

用户查询
    ↓
RAGService.retrieve_and_generate()
    ↓
VectorService.similarity_search()
    ↓
检索相关文档片段
    ↓
构建上下文
    ↓
调用llm-session服务
    ↓
返回答案 + 引用来源
```

## llm-session 详细架构

### 组件说明

1. **Session Service (会话服务)**
   - 职责：会话生命周期管理
   - 功能：
     - 会话创建/删除/关闭
     - 会话查询和列表
     - 上下文维护
     - 消息历史存储

2. **LLM Service (LLM服务)**
   - 职责：与大语言模型交互
   - 功能：
     - 多提供商支持（OpenAI、Azure等）
     - 消息格式转换
     - 响应生成
     - 流式输出
     - 系统提示构建

3. **Chat Service (聊天服务)**
   - 职责：对话流程编排
   - 功能：
     - 消息发送和接收
     - 上下文整合
     - 对话历史管理
     - 流式聊天

### 数据流

```
创建会话
    ↓
SessionService.create_session()
    ↓
生成session_id → 初始化上下文 → 存储会话信息
    ↓
返回session_id

---

发送消息
    ↓
ChatService.send_message()
    ↓
获取会话上下文
    ↓
添加用户消息到历史
    ↓
LLMService.generate_response()
    ↓
调用外部LLM API
    ↓
获取LLM响应
    ↓
保存助手消息到历史
    ↓
返回完整对话历史
```

## 两个服务的协作

### 场景：基于知识库的智能问答

```
1. 用户上传文档到 rag-scheduler
   POST http://localhost:8000/documents/upload
   
2. rag-scheduler处理文档
   - 提取文本
   - 分块
   - 生成向量
   - 存储到ChromaDB
   
3. 用户在 llm-session 创建会话
   POST http://localhost:9000/sessions/
   
4. 用户提问
   POST http://localhost:9000/chat/message
   {
     "message": "什么是机器学习？",
     "session_id": "xxx"
   }
   
5. llm-session 调用 rag-scheduler 检索相关文档
   POST http://localhost:8000/query/
   {
     "query": "什么是机器学习？"
   }
   
6. rag-scheduler 返回相关文档片段
   
7. llm-session 整合上下文，调用LLM生成回答
   
8. 返回答案给用户
```

## 技术栈详情

### rag-scheduler

| 层级 | 技术 | 用途 |
|------|------|------|
| Web框架 | FastAPI | RESTful API开发 |
| ORM | SQLAlchemy | 数据库操作 |
| 数据库 | PostgreSQL | 元数据存储 |
| 向量数据库 | ChromaDB | 向量存储和检索 |
| Embedding | Sentence Transformers | 文本向量化 |
| 文档处理 | PyPDF, python-docx | 文档解析 |
| 缓存 | Redis | 查询结果缓存 |

### llm-session

| 层级 | 技术 | 用途 |
|------|------|------|
| Web框架 | FastAPI | RESTful API开发 |
| ORM | SQLAlchemy | 数据库操作 |
| 数据库 | PostgreSQL | 会话数据存储 |
| 缓存 | Redis | 会话存储 |
| LLM | OpenAI SDK | GPT模型调用 |
| HTTP客户端 | HTTPX | 异步HTTP请求 |

## 扩展性设计

### rag-scheduler 扩展点

1. **向量数据库插件化**
   - 当前支持：ChromaDB
   - 可扩展：Milvus、Qdrant、Weaviate等

2. **Embedding模型可配置**
   - 当前支持：Sentence Transformers
   - 可扩展：OpenAI Embeddings、Cohere等

3. **文档解析器插件化**
   - 当前支持：PDF、DOCX、TXT、MD
   - 可扩展：PPT、Excel、HTML等

### llm-session 扩展点

1. **LLM提供商插件化**
   - 当前支持：OpenAI
   - 可扩展：Azure OpenAI、Claude、本地模型

2. **会话存储后端**
   - 当前支持：内存/PostgreSQL
   - 可扩展：MongoDB、Redis纯存储

3. **流式响应优化**
   - 支持SSE（Server-Sent Events）
   - 可扩展：WebSocket实时通信

## 部署建议

### 开发环境
```bash
# 启动rag-scheduler
cd rag-scheduler
uvicorn app.main:app --reload --port 8000

# 启动llm-session
cd llm-session
uvicorn app.main:app --reload --port 9000
```

### 生产环境

使用Docker Compose或Kubernetes：

```yaml
# docker-compose.yml 示例
version: '3.8'

services:
  postgres-rag:
    image: postgres:15
    environment:
      POSTGRES_DB: rag_db
  
  chromadb:
    image: chromadb/chroma:latest
  
  redis:
    image: redis:7-alpine
  
  rag-scheduler:
    build: ./rag-scheduler
    ports:
      - "8000:8000"
    depends_on:
      - postgres-rag
      - chromadb
      - redis
  
  llm-session:
    build: ./llm-session
    ports:
      - "9000:9000"
    depends_on:
      - postgres-rag
      - redis
```

## 监控和日志

建议集成：
- **Prometheus**: 指标采集
- **Grafana**: 可视化监控
- **ELK Stack**: 日志收集和分析
- **Jaeger**: 分布式追踪
