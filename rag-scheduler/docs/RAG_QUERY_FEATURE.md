# RAG 问答功能实现指南

## 📋 概述

rag-scheduler 服务现已实现**完整的 RAG（检索增强生成）问答功能**，包括向量检索、上下文构建和 LLM 回答生成。

## 🎯 核心功能

### 1. 向量相似度搜索
- ✅ 基于 ChromaDB 的语义检索
- ✅ 支持自定义 top_k 和相似度阈值
- ✅ 支持元数据过滤

### 2. 智能上下文构建
- ✅ 自动截取相关文本片段
- ✅ 添加引用标记 [引用1]、[引用2]...
- ✅ 控制上下文长度避免超出限制

### 3. LLM 回答生成
- ✅ 调用 llm-session 服务生成回答
- ✅ 基于检索结果提供准确答案
- ✅ 引用来源标注

---

## 📡 API 端点

### 1. 完整查询（推荐）

**端点**: `POST /query/`

**功能**: 向量检索 + 上下文构建

**请求示例**:
```bash
curl -X POST "http://localhost:8000/query/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "什么是机器学习？",
    "top_k": 5,
    "score_threshold": 0.7
  }'
```

**响应示例**:
```json
{
  "results": [
    {
      "chunk_id": "uuid_chunk_0",
      "document_id": "uuid",
      "content": "机器学习是一种...",
      "score": 0.85,
      "metadata": {...}
    }
  ],
  "total": 5,
  "query_time": 0.234,
  "context": "[引用1] 机器学习是一种...\n\n---\n\n[引用2] ..."
}
```

---

### 2. 仅向量搜索

**端点**: `POST /query/search`

**功能**: 只执行向量检索，不构建上下文

**请求示例**:
```bash
curl -X POST "http://localhost:8000/query/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "深度学习",
    "top_k": 3,
    "score_threshold": 0.6
  }'
```

**响应示例**:
```json
{
  "results": [
    {
      "chunk_id": "uuid_chunk_1",
      "document_id": "uuid",
      "content": "深度学习是机器学习的...",
      "similarity_score": 0.92,
      "metadata": {...}
    }
  ],
  "total": 3
}
```

---

### 3. 生成回答（需要LLM服务）

**端点**: `POST /query/generate`

**功能**: 完整 RAG 流程 - 检索 + 生成回答

**请求示例**:
```bash
curl -X POST "http://localhost:8000/query/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "什么是机器学习？",
    "top_k": 5,
    "score_threshold": 0.7
  }'
```

**响应示例**:
```json
{
  "query": "什么是机器学习？",
  "answer": "机器学习是一种人工智能的分支...",
  "sources": [
    {
      "chunk_id": "uuid_chunk_0",
      "document_id": "uuid",
      "content": "机器学习是一种...",
      "score": 0.85
    }
  ],
  "query_time": 1.234
}
```

---

## 💻 代码实现

### 1. RAG Service

**文件**: [`app/services/rag_service.py`](file://g:\rag\kret-rag\rag-scheduler\app\services\rag_service.py)

#### 核心方法

##### retrieve_and_generate()
```python
async def retrieve_and_generate(self, query_request: DocumentQueryRequest):
    """检索相关文档并生成答案"""
    # 1. 向量检索
    search_results = await vector_store_service.similarity_search(...)
    
    # 2. 构建上下文
    context = self.build_context(search_results, max_tokens=2000)
    
    # 3. 返回结果
    return DocumentQueryResponse(
        results=results,
        total=len(results),
        query_time=query_time,
        context=context
    )
```

##### build_context()
```python
def build_context(self, search_results, max_tokens=2000):
    """根据检索结果构建上下文"""
    context_parts = []
    current_length = 0
    
    for i, result in enumerate(search_results, 1):
        # 添加引用标记
        marked_content = f"[引用{i}] {result.content}"
        
        # 检查长度限制
        if current_length + len(marked_content) > max_tokens:
            break
        
        context_parts.append(marked_content)
        current_length += len(marked_content)
    
    # 用分隔符连接
    return "\n\n---\n\n".join(context_parts)
```

##### generate_answer_with_llm()
```python
async def generate_answer_with_llm(self, query, context, session_id=None):
    """调用LLM服务生成回答"""
    # 构建提示词
    prompt = self._build_rag_prompt(query, context)
    
    # 调用 llm-session 服务
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.LLM_SESSION_URL}/chat/message",
            json={"message": prompt, "session_id": session_id}
        )
        
        return response.json().get("response", "")
```

##### _build_rag_prompt()
```python
def _build_rag_prompt(self, query, context):
    """构建 RAG 提示词"""
    prompt = f"""你是一个智能问答助手。请基于以下参考信息回答问题。

**要求**：
1. 如果参考信息足以回答问题，请给出准确、详细的回答
2. 如果参考信息不足，请说明无法回答
3. 回答时要引用相关的信息来源（如：[引用1]、[引用2]）
4. 保持回答的专业性和准确性
5. 使用中文回答

**参考信息**：
{context}

**问题**：
{query}

**回答**：
"""
    return prompt
```

---

### 2. Query Routes

**文件**: [`app/routes/query.py`](file://g:\rag\kret-rag\rag-scheduler\app\routes\query.py)

#### 三个端点

1. **`POST /query/`** - 完整查询（检索 + 上下文）
2. **`POST /query/search`** - 仅向量搜索
3. **`POST /query/generate`** - 完整 RAG（检索 + 生成回答）

---

### 3. Schema 定义

**文件**: [`app/models/schemas.py`](file://g:\rag\kret-rag\rag-scheduler\app\models\schemas.py)

```python
class DocumentQueryRequest(BaseModel):
    """查询请求"""
    query: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(default=5, ge=1, le=20)
    score_threshold: Optional[float] = Field(default=0.7, ge=0.0, le=1.0)
    filters: Optional[Dict[str, Any]] = None


class DocumentQueryResponse(BaseModel):
    """查询响应"""
    results: List[QueryResultItem]
    total: int
    query_time: float
    context: Optional[str] = None  # ⭐ 新增字段
```

---

## 🧪 测试方法

### 1. 启动服务

```bash
cd rag-scheduler
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. 上传测试文档

确保已经上传了包含相关内容的文档：

```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@machine_learning_intro.pdf"
```

### 3. 运行测试脚本

```bash
cd rag-scheduler
python test_rag_query.py
```

**测试内容**：
- ✅ 测试 1: 向量搜索
- ✅ 测试 2: 完整查询
- ⚠️ 测试 3: 生成回答（需要 LLM 服务运行）

### 4. 手动测试

#### 测试向量搜索
```bash
curl -X POST "http://localhost:8000/query/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "机器学习", "top_k": 3}'
```

#### 测试完整查询
```bash
curl -X POST "http://localhost:8000/query/" \
  -H "Content-Type: application/json" \
  -d '{"query": "什么是深度学习？", "top_k": 5}'
```

#### 测试生成回答
```bash
curl -X POST "http://localhost:8000/query/generate" \
  -H "Content-Type: application/json" \
  -d '{"query": "神经网络的工作原理是什么？"}'
```

---

## 📊 工作流程

```
用户提问
    ↓
1️⃣ 向量化查询文本
    ↓
2️⃣ ChromaDB 相似度搜索
    ↓
3️⃣ 获取 Top-K 相关 chunk
    ↓
4️⃣ 过滤低相似度结果
    ↓
5️⃣ 构建上下文（添加引用标记）
    ↓
6️⃣ 构建 RAG 提示词
    ↓
7️⃣ 调用 LLM 服务生成回答
    ↓
8️⃣ 返回答案 + 引用来源
```

---

## 🔧 配置参数

### 环境变量 (.env)

```env
# LLM 服务地址
LLM_SESSION_URL=http://localhost:9000

# 向量数据库配置
CHROMA_HOST=./data/chromadb
CHROMA_COLLECTION_NAME=rag_collection

# Embedding 模型
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# 分块配置
CHUNK_SIZE=500
CHUNK_OVERLAP=50
```

### 查询参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| query | string | 必填 | 用户问题 |
| top_k | int | 5 | 返回结果数量（1-20） |
| score_threshold | float | 0.7 | 相似度阈值（0.0-1.0） |
| filters | object | null | 元数据过滤条件 |

---

## 💡 高级用法

### 1. 元数据过滤

按文档 ID 过滤：
```json
{
  "query": "机器学习",
  "filters": {
    "document_id": "specific-uuid"
  }
}
```

按文件名过滤：
```json
{
  "query": "深度学习",
  "filters": {
    "file_name": "AI_Intro.pdf"
  }
}
```

### 2. 调整相似度阈值

高精度（减少噪声）：
```json
{
  "query": "神经网络",
  "score_threshold": 0.9
}
```

高召回（更多结果）：
```json
{
  "query": "人工智能",
  "score_threshold": 0.5
}
```

### 3. 控制上下文长度

在代码中修改：
```python
context = self.build_context(
    search_results=search_results,
    max_tokens=3000  # 增加上下文长度
)
```

---

## 🔍 故障排查

### 问题 1: 搜索结果为空

**症状**:
```json
{"results": [], "total": 0}
```

**原因**:
- 没有上传文档
- 文档未正确向量化
- 相似度阈值设置过高

**解决**:
1. 检查是否已上传文档
2. 查看 ChromaDB 中的数据：
   ```python
   import chromadb
   client = chromadb.PersistentClient(path="./data/chromadb")
   collection = client.get_collection("rag_collection")
   print(collection.count())  # 应该 > 0
   ```
3. 降低 `score_threshold` 到 0.5

---

### 问题 2: LLM 服务调用失败

**症状**:
```
Connection refused: localhost:9000
```

**原因**: llm-session 服务未启动

**解决**:
```bash
# 启动 llm-session 服务
cd llm-session
uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload
```

或者暂时不使用 `/query/generate` 端点，改用 `/query/` 获取检索结果。

---

### 问题 3: 回答质量不高

**原因**:
- 检索到的相关内容不够准确
- 上下文构建不合理

**优化建议**:
1. 调整 `top_k` 获取更多相关片段
2. 降低 `score_threshold` 扩大检索范围
3. 优化文档分块策略（增大 CHUNK_SIZE）
4. 改进提示词模板

---

## 🚀 性能优化

### 1. 批量检索
当前已经是批量处理，无需额外优化。

### 2. 缓存热门搜索
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_search(query: str, top_k: int):
    """缓存热门查询结果"""
    # ...
```

### 3. 异步并发
```python
# 同时检索多个知识库
results = await asyncio.gather(
    search_kb1(query),
    search_kb2(query),
    search_kb3(query)
)
```

---

## 📚 相关文档

- [RAG_PIPELINE_IMPLEMENTATION.md](RAG_PIPELINE_IMPLEMENTATION.md) - RAG 四步处理流程
- [CLEANED_TEXT_AUTO_SAVE.md](CLEANED_TEXT_AUTO_SAVE.md) - 清洗后文本保存
- [TABLE_TO_MARKDOWN.md](TABLE_TO_MARKDOWN.md) - 表格转 Markdown
- [FILE_PROCESSING_FLOW.md](FILE_PROCESSING_FLOW.md) - 文件处理流程

---

## 🎯 下一步优化方向

1. **混合检索**
   - 关键词检索 + 向量检索
   - BM25 + Dense Vector

2. **重排序（Rerank）**
   - 使用 Cross-Encoder 对检索结果重新排序
   - 提升相关性最高的结果排名

3. **多轮对话**
   - 维护对话历史
   - 上下文感知问答

4. **引用溯源**
   - 精确标注答案来源段落
   - 高亮显示关键信息

5. **流式输出**
   - SSE 实时推送回答
   - 提升用户体验

---

## 💡 总结

现在 rag-scheduler 已经实现了**完整的 RAG 问答功能**：

✅ **向量检索** - 基于 ChromaDB 的语义搜索  
✅ **上下文构建** - 智能截取和引用标记  
✅ **LLM 集成** - 调用 llm-session 生成回答  
✅ **三个 API 端点** - 灵活适配不同场景  

**使用建议**：
- 开发阶段：使用 `/query/search` 测试检索效果
- 生产环境：使用 `/query/` 获取检索结果
- 完整体验：使用 `/query/generate` 获得 AI 回答

准备好开始使用 RAG 问答功能了吗？🚀
