# RAG 完整处理流程实现指南

## 📋 概述

rag-scheduler 服务现已实现**完整的 RAG 处理流程**，包括文本清洗、分块、向量化和存储。

## 🎯 四步处理流程

### ✅ 第 1 步：清洗后的文本持久化保存（已完成）

**功能**：将提取并清洗后的文本保存为独立的 `.txt` 文件

**实现位置**：[`app/services/document_service.py`](file://g:\rag\kret-rag\rag-scheduler\app\services\document_service.py) - [save_cleaned_text()](file://g:\rag\kret-rag\rag-scheduler\app\services\document_service.py#L847-L869)

**存储位置**：`./uploads_text/{document_id}.txt`

**好处**：
- ✅ 避免重复解析 Word/PDF
- ✅ 直接读取文本文件，提升性能
- ✅ 便于调试和查看清洗结果

**代码示例**：
```python
# 保存清洗后的文本
text_file_path = self.save_cleaned_text(document_id, cleaned_text)
# 输出: uploads_text/550e8400-e29b-41d4-a716-446655440000.txt
```

---

### ✅ 第 2 步：文本分块（已完成）

**功能**：将长文档切分成适合 RAG 的小块

**实现位置**：[`app/services/document_service.py`](file://g:\rag\kret-rag\rag-scheduler\app\services\document_service.py) - [chunk_document()](file://g:\rag\kret-rag\rag-scheduler\app\services\document_service.py#L862-L903)

**分块策略**：
- **块大小**：500 字符（可配置 `CHUNK_SIZE`）
- **重叠**：50 字符（可配置 `CHUNK_OVERLAP`）
- **智能分割**：优先在句子边界（`.` 或 `\n`）处分割

**代码示例**：
```python
# 对清洗后的文本进行分块
chunks = self.chunk_document(cleaned_text)
# 输出: ["第一段内容...", "第二段内容...", ...]
logger.info(f"文本分块完成，共 {len(chunks)} 个块")
```

**配置参数**（在 [.env](file://g:\rag\kret-rag\.env) 中）：
```env
CHUNK_SIZE=500        # 每块的字符数
CHUNK_OVERLAP=50      # 块之间的重叠字符数
```

---

### ✅ 第 3 步：Embedding 向量化（已完成）

**功能**：为每个文本块生成向量表示

**实现位置**：[`app/services/vector_service.py`](file://g:\rag\kret-rag\rag-scheduler\app\services\vector_service.py) - [generate_embedding()](file://g:\rag\kret-rag\rag-scheduler\app\services\vector_service.py#L63-L78)

**使用的模型**：`sentence-transformers/all-MiniLM-L6-v2`
- **维度**：384 维
- **语言**：支持中英文
- **性能**：快速且准确

**代码示例**：
```python
# 生成单个文本的向量
embedding = vector_store_service.generate_embedding("这是一段测试文本")
# 输出: [0.123, -0.456, 0.789, ...] (384 维向量)

# 批量生成向量（更高效）
embeddings = embedding_model.encode(chunks).tolist()
```

**配置参数**：
```env
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
```

---

### ✅ 第 4 步：存入向量库（已完成）

**功能**：将「文本块 + 向量」存储到 ChromaDB

**实现位置**：[`app/services/vector_service.py`](file://g:\rag\kret-rag\rag-scheduler\app\services\vector_service.py) - [store_chunks()](file://g:\rag\kret-rag\rag-scheduler\app\services\vector_service.py#L80-L138)

**存储结构**：
```
ChromaDB Collection: rag_collection
├─ ID: {document_id}_chunk_0
│  ├─ Document: "第一段文本内容..."
│  ├─ Embedding: [0.123, -0.456, ...]
│  └─ Metadata: {
│       "document_id": "550e8400-...",
│       "file_name": "test.pdf",
│       "chunk_index": 0,
│       "chunk_length": 485,
│       "timestamp": "2026-05-11T00:00:00"
│     }
├─ ID: {document_id}_chunk_1
│  └─ ...
└─ ...
```

**存储路径**：`./data/chromadb/`（持久化存储）

**代码示例**：
```python
# 存储所有 chunk 到向量数据库
await vector_store_service.store_chunks(
    document_id=document_id,
    chunks=chunks,
    file_name=file.filename
)
logger.info(f"成功存储 {len(chunks)} 个文本块到向量数据库")
```

---

## 🔄 完整处理流程

```
用户上传文档
    ↓
1️⃣ 验证文件格式和大小
    ↓
2️⃣ 检查是否重复（文件名+大小）
    ↓
3️⃣ 保存原始文件到 uploads/
    ↓
4️⃣ 提取文本内容（PDF/DOCX/Excel等）
    ↓
5️⃣ 清理文本（去页眉页脚、水印、乱码）
    ↓
⭐ 6️⃣ 保存清洗后文本到 uploads_text/{uuid}.txt
    ↓
⭐ 7️⃣ 文本分块（500字符/块，重叠50字符）
    ↓
⭐ 8️⃣ 生成向量（Sentence Transformers）
    ↓
⭐ 9️⃣ 存储到 ChromaDB（./data/chromadb/）
    ↓
🔟 保存元数据到 SQLite
    ↓
返回响应
```

---

## 💻 代码实现细节

### 1. DocumentService 初始化

**文件**: [`app/services/document_service.py`](file://g:\rag\kret-rag\rag-scheduler\app\services\document_service.py#L31-L73)

```python
def __init__(self):
    """初始化文档服务"""
    # ... 创建目录、执行迁移 ...
    
    # ⭐ 初始化向量服务
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(self._init_vector_service())
        else:
            loop.run_until_complete(self._init_vector_service())
    except Exception as e:
        logger.warning(f"向量服务初始化延迟: {str(e)}")

async def _init_vector_service(self):
    """异步初始化向量服务"""
    await vector_store_service.initialize()
    logger.info("向量服务初始化成功")
```

### 2. 上传文档时的处理流程

**文件**: [`app/services/document_service.py`](file://g:\rag\kret-rag\rag-scheduler\app\services\document_service.py#L130-L160)

```python
# 清理文本
cleaned_text = self.clean_text(extracted_text)

# ⭐ 第 1 步：保存清洗后文本
text_file_path = self.save_cleaned_text(document_id, cleaned_text)

# ⭐ 第 2 步：文本分块
chunks = self.chunk_document(cleaned_text)
logger.info(f"文本分块完成，共 {len(chunks)} 个块")

# ⭐ 第 3 & 4 步：向量化和存储
await self._process_and_store_chunks(document_id, chunks, file.filename)
logger.info("向量化和存储完成")

# 保存元数据到数据库
doc_metadata = repo.create(
    document_id=document_id,
    file_name=file.filename,
    # ...
    metadata={
        "text_length": len(cleaned_text),
        "chunk_count": len(chunks)  # ⭐ 记录 chunk 数量
    }
)
```

### 3. VectorStoreService 核心方法

#### 初始化

**文件**: [`app/services/vector_service.py`](file://g:\rag\kret-rag\rag-scheduler\app\services\vector_service.py#L28-L50)

```python
async def initialize(self):
    """初始化向量数据库和embedding模型"""
    # 初始化 ChromaDB（持久化存储）
    self.vector_db = chromadb.PersistentClient(path=settings.CHROMA_HOST)
    
    # 获取或创建集合
    self.collection = self.vector_db.get_or_create_collection(
        name=settings.CHROMA_COLLECTION_NAME
    )
    
    # 加载 Embedding 模型
    self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
```

#### 存储 Chunks

**文件**: [`app/services/vector_service.py`](file://g:\rag\kret-rag\rag-scheduler\app\services\vector_service.py#L80-L138)

```python
async def store_chunks(self, document_id: str, chunks: List[str], file_name: str) -> bool:
    """存储文档块向量到 ChromaDB"""
    # 为每个 chunk 生成 ID
    ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]
    
    # 批量生成向量（更高效）
    embeddings = self.embedding_model.encode(chunks).tolist()
    
    # 准备元数据
    metadatas = [
        {
            "document_id": document_id,
            "file_name": file_name,
            "chunk_index": i,
            "chunk_length": len(chunk),
            "timestamp": datetime.now().isoformat()
        }
        for i, chunk in enumerate(chunks)
    ]
    
    # 存储到 ChromaDB
    self.collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas
    )
```

---

## 🧪 测试方法

### 1. 启动服务

```bash
cd rag-scheduler
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**首次启动日志**：
```
INFO:app.services.document_service:检查并执行数据库迁移...
✅ [Migration 001] text_file_path 字段已存在，跳过
INFO:app.services.document_service:数据库初始化完成
INFO:app.services.vector_service:初始化 ChromaDB，路径: ./data/chromadb
INFO:app.services.vector_service:ChromaDB 集合 'rag_collection' 初始化成功
INFO:app.services.vector_service:加载 Embedding 模型: sentence-transformers/all-MiniLM-L6-v2
INFO:app.services.vector_service:Embedding 模型加载成功
INFO:app.services.document_service:向量服务初始化成功
```

### 2. 上传文档

```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@test.pdf" \
  -v
```

**处理日志**：
```
INFO:app.services.document_service:开始处理文件上传: test.pdf, 大小: 1024000 bytes
INFO:app.services.document_service:文件格式验证通过: pdf
INFO:app.services.document_service:开始提取文本内容，文件格式: pdf
INFO:app.services.document_service:文本提取完成，原始文本长度: 15000 字符
INFO:app.services.document_service:开始清理文本内容...
INFO:app.services.document_service:文本清理完成，清理后文本长度: 14500 字符
INFO:app.services.document_service:开始保存清洗后的文本文件...
INFO:app.services.document_service:清洗后的文本已保存: uploads_text/550e8400-....txt
INFO:app.services.document_service:清洗后文本保存成功: uploads_text/550e8400-....txt
INFO:app.services.document_service:开始对文本进行分块...
INFO:app.services.document_service:文本分块完成，共 29 个块
INFO:app.services.document_service:开始向量化和存储...
INFO:app.services.vector_service:开始存储 29 个文本块...
INFO:app.services.vector_service:正在生成向量...
INFO:app.services.vector_service:正在写入 ChromaDB...
INFO:app.services.vector_service:成功存储 29 个文本块到向量数据库
INFO:app.services.document_service:向量化和存储完成
INFO:app.services.document_service:开始保存文档元数据到数据库...
INFO:app.services.document_service:文档元数据保存成功: 550e8400-...
INFO:app.services.document_service:文件处理完成: 550e8400-...
```

### 3. 验证结果

#### 检查清洗后的文本文件
```bash
ls -la uploads_text/
cat uploads_text/550e8400-*.txt
```

#### 检查 ChromaDB 数据
```python
import chromadb

# 连接 ChromaDB
client = chromadb.PersistentClient(path="./data/chromadb")
collection = client.get_collection("rag_collection")

# 查询某个文档的所有 chunk
results = collection.get(
    where={"document_id": {"$eq": "550e8400-..."}}
)

print(f"Chunk 数量: {len(results['ids'])}")
print(f"第一个 Chunk: {results['documents'][0][:100]}...")
print(f"向量维度: {len(results['embeddings'][0])}")
```

#### 测试相似度搜索
```python
from app.services.vector_service import vector_store_service
import asyncio

async def test_search():
    # 初始化
    await vector_store_service.initialize()
    
    # 搜索
    results = await vector_store_service.similarity_search(
        query="什么是机器学习？",
        top_k=5,
        score_threshold=0.7
    )
    
    for result in results:
        print(f"相似度: {result.similarity_score:.4f}")
        print(f"内容: {result.content[:100]}...")
        print("---")

asyncio.run(test_search())
```

---

## 📊 性能优化建议

### 1. 批量向量化
当前实现已经使用批量处理：
```python
# ✅ 高效：一次性生成所有向量
embeddings = self.embedding_model.encode(chunks).tolist()

# ❌ 低效：逐个生成
for chunk in chunks:
    embedding = self.generate_embedding(chunk)
```

### 2. ChromaDB 持久化存储
使用本地文件系统存储，避免每次重启丢失数据：
```python
# ✅ 持久化存储
self.vector_db = chromadb.PersistentClient(path="./data/chromadb")

# ❌ 内存存储（重启后丢失）
self.vector_db = chromadb.Client()
```

### 3. 懒加载 Embedding 模型
首次使用时才加载模型，加快启动速度：
```python
# 在 __init__ 中不加载模型
# 在首次调用时加载
if not self.embedding_model:
    self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
```

---

## 🔍 故障排查

### 问题 1: Embedding 模型下载失败

**症状**：
```
OSError: Can't load model from sentence-transformers/all-MiniLM-L6-v2
```

**解决**：
```bash
# 手动下载模型
pip install -U sentence-transformers

# 或在代码中指定缓存目录
import os
os.environ['SENTENCE_TRANSFORMERS_HOME'] = './models'
```

### 问题 2: ChromaDB 初始化失败

**症状**：
```
Exception: ChromaDB initialization failed
```

**解决**：
```bash
# 删除旧的 ChromaDB 数据
rm -rf data/chromadb

# 重启服务，自动重新创建
uvicorn app.main:app --reload
```

### 问题 3: 向量化速度慢

**原因**：CPU 模式下较慢

**解决**：
```python
# 使用 GPU（如果有）
self.embedding_model = SentenceTransformer(
    settings.EMBEDDING_MODEL,
    device='cuda'  # 或 'cpu'
)
```

---

## 📚 相关文档

- [CLEANED_TEXT_AUTO_SAVE.md](CLEANED_TEXT_AUTO_SAVE.md) - 清洗后文本保存
- [TABLE_TO_MARKDOWN.md](TABLE_TO_MARKDOWN.md) - 表格转 Markdown
- [FILE_PROCESSING_FLOW.md](FILE_PROCESSING_FLOW.md) - 文件处理流程
- [DATABASE_MIGRATION_GUIDE.md](DATABASE_MIGRATION_GUIDE.md) - 数据库迁移

---

## 🚀 后续优化方向

1. **异步队列处理**
   - 将向量化改为后台任务
   - 避免阻塞上传响应

2. **增量更新**
   - 检测文档变更
   - 只重新处理变化的部分

3. **多模型支持**
   - 支持切换不同的 Embedding 模型
   - 根据语言自动选择模型

4. **向量索引优化**
   - 使用 HNSW 索引加速搜索
   - 调整索引参数平衡速度和精度

5. **分布式存储**
   - 支持 Milvus/Qdrant 集群
   - 水平扩展向量检索能力

---

## 💡 总结

现在 rag-scheduler 已经实现了**完整的 RAG 处理流程**：

✅ **第 1 步**：清洗后的文本保存到 `uploads_text/{uuid}.txt`  
✅ **第 2 步**：文本分块（500字符/块）  
✅ **第 3 步**：Embedding 向量化（Sentence Transformers）  
✅ **第 4 步**：存入 ChromaDB（`./data/chromadb/`）  

**优势**：
- 🚀 避免重复解析，提升性能
- 📊 结构化存储，便于检索
- 🔍 支持语义相似度搜索
- 💾 持久化存储，重启不丢失

**下一步**：可以实现基于向量检索的 RAG 问答功能！
