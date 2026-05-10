# KRET-RAG 微服务架构设计规范

## 📋 概述

本文档定义了 KRET-RAG 系统中两个核心微服务的职责边界和协作方式。

---

## 🎯 架构原则

### 单一职责原则
每个服务只负责一个明确的业务领域，避免功能重叠和耦合。

### 关注点分离
- **rag-scheduler**: 专注于信息检索和知识提取
- **llm-session**: 专注于对话管理和语言生成

### 松耦合设计
通过 HTTP API 进行通信，服务间不共享数据库或内部状态。

---

## 🏗️ 服务职责划分

### rag-scheduler（检索服务）

#### ✅ 核心职责

**1. 文档处理**
- 多格式文档上传（PDF/DOCX/TXT/MD等）
- 文本提取与清洗
- 智能分块（500字符/块，重叠50字符）
- 清洗后文本持久化

**2. 向量存储**
- Embedding 向量化（Sentence Transformers）
- ChromaDB 向量数据库管理
- 批量存储优化

**3. 检索增强**
- **向量相似度搜索**（语义检索）
- **BM25 关键词检索**（精确匹配）
- **混合检索**（BM25 + 向量融合）
- **Rerank 重排序**（BGE Reranker 精排）
- **查询重写**（优化检索效果）

**4. 上下文构建**
- 根据检索结果构建带引用标记的上下文
- 控制上下文长度（默认2000字符）
- 添加 [引用1]、[引用2] 等标记

**5. 知识库管理**
- 文档元数据存储（SQLite/PostgreSQL）
- 文件去重检测
- 文档生命周期管理

#### ❌ 不负责的功能

- ❌ Prompt 模板管理
- ❌ 多轮对话历史管理
- ❌ LLM 调用与响应生成
- ❌ 流式输出
- ❌ 会话状态管理
- ❌ 用户认证与授权

#### 📡 对外接口

```python
POST /query/              # 检索 + 上下文构建
POST /query/search        # 纯向量搜索
POST /query/context       # 仅构建上下文
POST /query/generate      # 转发给 llm-session 生成回答
POST /documents/upload    # 文档上传
GET  /documents/          # 文档列表
DELETE /documents/{id}    # 删除文档
```

#### 🔧 技术栈

- **Web框架**: FastAPI
- **向量库**: ChromaDB (PersistentClient)
- **Embedding**: sentence-transformers/all-MiniLM-L6-v2
- **BM25**: rank-bm25 + jieba 分词
- **Rerank**: FlagEmbedding/BGE Reranker
- **数据库**: SQLite (可扩展 PostgreSQL)
- **文档解析**: pypdf, python-docx, pandas

---

### llm-session（对话管理服务）

#### ✅ 核心职责

**1. Prompt 模板管理**
- 系统提示词构建
- RAG 专用提示模板
- 多轮对话上下文整合
- 动态模板渲染

**2. 多轮对话管理**
- 会话创建与维护
- 对话历史存储
- 上下文窗口管理（最近N轮）
- 会话状态跟踪（active/paused/closed）

**3. LLM 调用**
- OpenAI/Azure/Claude 等多模型支持
- 模型参数配置（temperature, max_tokens等）
- 错误处理与重试机制
- Token 使用统计

**4. 流式输出**
- Server-Sent Events (SSE) 支持
- 实时响应推送
- 增量内容处理

**5. RAG 上下文整合**
- 接收 rag-scheduler 提供的上下文
- 将上下文融入系统提示
- 保持原始问题与上下文的关联

#### ❌ 不负责的功能

- ❌ 文档上传与解析
- ❌ 向量检索
- ❌ 相似度计算
- ❌ 文档分块
- ❌ 知识库管理

#### 📡 对外接口

```python
POST /chat/message        # 发送消息（支持RAG上下文）
POST /chat/stream         # 流式响应（支持RAG上下文）
POST /sessions/           # 创建会话
GET  /sessions/           # 列出会话
GET  /sessions/{id}       # 获取会话详情
DELETE /sessions/{id}     # 删除会话
```

#### 🔧 技术栈

- **Web框架**: FastAPI
- **LLM**: OpenAI GPT / Azure OpenAI / Claude
- **缓存**: Redis (可选，用于会话缓存)
- **HTTP客户端**: HTTPX
- **流式传输**: FastAPI StreamingResponse

---

## 🔄 服务协作流程

### 完整的 RAG 问答流程

```
用户提问
    ↓
┌─────────────────────────────────────────┐
│  前端/客户端                              │
│  - 收集用户问题                           │
│  - 可选：提供 session_id                 │
└────────────┬────────────────────────────┘
             │
             │ POST /query/generate
             │ {
             │   "query": "问题",
             │   "session_id": "xxx"
             │ }
             ↓
┌─────────────────────────────────────────┐
│  rag-scheduler (8000端口)                │
│                                          │
│  1. 查询重写（可选）                      │
│  2. 向量检索（Top-K）                    │
│  3. BM25 检索（可选）                    │
│  4. Rerank 重排序（可选）                │
│  5. 构建上下文（带引用标记）              │
│     "[引用1] 内容...\n\n[引用2] 内容..." │
│                                          │
│  6. 调用 llm-session:                   │
│     POST /chat/message                  │
│     {                                   │
│       "message": context,               │
│       "query": original_query,          │
│       "rag_context": context,           │
│       "session_id": "xxx"               │
│     }                                   │
└────────────┬────────────────────────────┘
             │
             │ 转发请求
             ↓
┌─────────────────────────────────────────┐
│  llm-session (9000端口)                  │
│                                          │
│  1. 获取或创建会话                        │
│  2. 保存用户消息到历史                    │
│  3. 构建系统提示（包含RAG上下文）         │
│     "你是一个智能问答助手...             │
│      参考信息：{rag_context}"            │
│  4. 整合对话历史                          │
│  5. 调用 LLM 生成回答                     │
│  6. 保存助手响应到历史                    │
│  7. 返回完整响应                          │
└────────────┬────────────────────────────┘
             │
             │ 返回回答
             ↓
┌─────────────────────────────────────────┐
│  rag-scheduler                           │
│  - 组装最终响应                          │
│  - 包含：                                │
│    * answer: LLM生成的回答               │
│    * sources: 引用来源列表               │
│    * context_used: 使用的上下文          │
│    * session_id: 会话ID                  │
└────────────┬────────────────────────────┘
             │
             │ 返回最终结果
             ↓
┌─────────────────────────────────────────┐
│  前端/客户端                              │
│  - 展示AI回答                            │
│  - 显示引用来源                          │
│  - 支持多轮对话                          │
└─────────────────────────────────────────┘
```

### 简化流程（仅检索）

```
用户查询
    ↓
┌─────────────────────────────────────────┐
│  前端/客户端                              │
└────────────┬────────────────────────────┘
             │
             │ POST /query/
             │ {
             │   "query": "问题",
             │   "top_k": 5
             │ }
             ↓
┌─────────────────────────────────────────┐
│  rag-scheduler                           │
│  1. 执行检索                             │
│  2. 构建上下文                           │
│  3. 返回检索结果                         │
└────────────┬────────────────────────────┘
             │
             │ 返回结果
             ↓
┌─────────────────────────────────────────┐
│  前端/客户端                              │
│  - 展示相关文档片段                       │
│  - 自行决定后续操作                       │
└─────────────────────────────────────────┘
```

---

## 📊 数据流转示例

### rag-scheduler → llm-session

**请求示例**：
```json
POST http://localhost:9000/chat/message
{
  "message": "[引用1] RAG是一种检索增强生成技术...\n\n[引用2] 它结合了向量检索和语言模型...",
  "query": "什么是RAG？",
  "rag_context": "[引用1] RAG是一种检索增强生成技术...\n\n[引用2] 它结合了向量检索和语言模型...",
  "session_id": "sess_123456"
}
```

**响应示例**：
```json
{
  "session_id": "sess_123456",
  "message_id": "5",
  "response": "RAG（Retrieval-Augmented Generation）是一种检索增强生成技术 [引用1]。它结合了向量检索和大型语言模型，通过先从知识库中检索相关信息，再基于这些信息生成回答 [引用2]。这种方法可以显著提高回答的准确性和可靠性。",
  "conversation_history": [...]
}
```

---

## 🔑 关键设计决策

### 1. 为什么 rag-scheduler 不直接调用 LLM？

**原因**：
- **职责清晰**: rag-scheduler 专注检索，llm-session 专注对话
- **可复用性**: 其他服务也可以使用 llm-session 的对话能力
- **灵活性**: 可以独立升级 LLM 模型而不影响检索逻辑
- **性能优化**: llm-session 可以专门优化流式输出、缓存等

### 2. 为什么需要传递 session_id？

**原因**：
- **多轮对话**: 保持对话上下文的连续性
- **个性化**: 不同用户可以有不同的对话历史
- **状态管理**: llm-session 需要知道这是新对话还是继续之前的对话

### 3. 为什么要传递 query 和 rag_context 两个字段？

**原因**：
- **query**: 保留原始问题，用于日志、分析和调试
- **rag_context**: 提供检索到的相关知识，用于生成回答
- **分离关注点**: 问题和知识是两个不同的概念

### 4. 为什么不直接在 rag-scheduler 中构建 Prompt？

**原因**：
- **Prompt 是对话的一部分**: 应该由对话管理服务统一管理
- **灵活性**: llm-session 可以根据不同场景使用不同的 Prompt 模板
- **维护性**: Prompt 调整不需要修改检索代码

---

## 🚀 部署建议

### 开发环境

```bash
# 启动 rag-scheduler
cd rag-scheduler
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 启动 llm-session
cd llm-session
uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload
```

### 生产环境

```yaml
# docker-compose.yml
version: '3.8'
services:
  rag-scheduler:
    build: ./rag-scheduler
    ports:
      - "8000:8000"
    environment:
      - LLM_SESSION_URL=http://llm-session:9000
    depends_on:
      - chromadb
      - postgresql
  
  llm-session:
    build: ./llm-session
    ports:
      - "9000:9000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - redis
  
  chromadb:
    image: chromadb/chroma:latest
    volumes:
      - ./data/chromadb:/chroma/chroma
  
  postgresql:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - ./data/postgres:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
```

---

## 📈 性能优化建议

### rag-scheduler

1. **向量检索优化**
   - 使用 HNSW 索引加速相似度搜索
   - 批量 embedding 生成（比逐个快10x）
   - 缓存热门查询的检索结果

2. **混合检索策略**
   - 开发阶段：use_hybrid=False 测试基础功能
   - 生产环境：use_hybrid=True, use_rerank=True 获得最佳效果
   - 性能敏感：use_hybrid=True, use_rerank=False 平衡速度和质量

3. **数据库优化**
   - 为常用查询字段创建索引
   - 定期清理过期文档
   - 使用连接池（PostgreSQL）

### llm-session

1. **LLM 调用优化**
   - 使用流式输出提升用户体验
   - 缓存常见问题的回答
   - 设置合理的 max_tokens 限制

2. **会话管理优化**
   - 使用 Redis 缓存活跃会话
   - 定期清理过期会话
   - 限制单个会话的最大消息数

3. **并发处理**
   - 使用异步 HTTP 客户端
   - 实现请求队列和限流
   - 水平扩展多个实例

---

## 🔍 故障排查

### rag-scheduler 常见问题

**问题1**: 检索结果为空
- 检查 ChromaDB 是否有数据
- 验证 embedding 模型是否正确加载
- 调整 score_threshold 参数

**问题2**: 查询速度慢
- 检查是否启用了 Rerank（会增加耗时）
- 减少 top_k 值
- 优化 ChromaDB 索引

**问题3**: 上下文过长被截断
- 调整 build_context 的 max_tokens 参数
- 减少 top_k 值
- 优化分块大小

### llm-session 常见问题

**问题1**: LLM 调用失败
- 检查 API Key 是否正确
- 验证网络连接
- 查看 LLM 服务商状态

**问题2**: 响应超时
- 增加 timeout 配置
- 使用流式输出
- 减少 max_tokens

**问题3**: 会话丢失
- 检查 Redis 连接
- 验证会话存储逻辑
- 查看磁盘空间

---

## 📝 最佳实践

### 1. 日志记录

**rag-scheduler**:
```python
logger.info(f"开始检索: query='{query[:50]}...', top_k={top_k}")
logger.info(f"检索完成，找到 {len(results)} 个相关结果")
logger.info(f"上下文构建完成，长度: {len(context)} 字符")
```

**llm-session**:
```python
logger.info(f"处理消息: session_id={session_id}, has_rag_context={has_rag}")
logger.info(f"LLM响应生成完成，长度: {len(response)} 字符")
logger.info(f"流式响应完成: total_chunks={chunk_count}")
```

### 2. 错误处理

- 始终捕获异常并记录详细日志
- 返回友好的错误消息
- 实现重试机制（特别是 LLM 调用）

### 3. 监控指标

**rag-scheduler**:
- 平均查询耗时
- 检索结果数量分布
- 缓存命中率

**llm-session**:
- LLM 调用成功率
- 平均响应时间
- 活跃会话数

### 4. 安全考虑

- 对用户输入进行验证和转义
- 限制单次请求的最大长度
- 实现速率限制
- 记录审计日志

---

## 🔄 版本演进

### v1.0（当前版本）
- ✅ rag-scheduler: 完整的检索和上下文构建
- ✅ llm-session: 基础的对话管理和 LLM 调用
- ✅ 服务间通过 HTTP API 通信

### v2.0（规划中）
- 🔜 rag-scheduler: 支持多向量库（Milvus/Qdrant）
- 🔜 llm-session: 支持更多 LLM 模型
- 🔜 实现服务发现和健康检查
- 🔜 添加分布式追踪

### v3.0（长期目标）
- 🔮 rag-scheduler: 支持实时文档更新
- 🔮 llm-session: 支持多模态对话
- 🔮 实现自动扩缩容
- 🔮 添加 A/B 测试框架

---

## 📚 相关文档

- [rag-scheduler README](../rag-scheduler/README.md)
- [llm-session README](../llm-session/README.md)
- [RAG 完整四步处理流程](./RAG_PIPELINE_IMPLEMENTATION.md)
- [BM25 混合检索与 Rerank](./HYBRID_SEARCH_RERANK.md)
- [查询测试页面指南](./QUERY_TEST_GUIDE.md)

---

**最后更新**: 2026-05-11  
**维护者**: KRET-RAG Team
