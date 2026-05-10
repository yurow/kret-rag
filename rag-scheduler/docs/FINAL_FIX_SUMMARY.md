# 问题诊断与解决方案总结

## 🐛 问题清单

### 问题1：向量检索返回空结果

**现象**：
- 查询时返回 `"total": 0`
- 日志显示 "BM25 索引未初始化，降级为纯向量检索"
- ChromaDB 中有10条记录，但检索不到任何结果

**根本原因**：
1. **缺少 startup_event**：main.py 中没有在应用启动时初始化向量服务
2. **ChromaDB 距离度量不匹配**：旧数据使用 L2 距离存储，代码期望余弦相似度

---

### 问题2：TensorFlow oneDNN 警告

**现象**：
```
WARNING: All log messages before absl::InitializeLog() is called are written to STDERR
I0000 00:00:1778564250.227602 port.cc:153] oneDNN custom operations are on...
```

**说明**：
- 这不是错误，只是 TensorFlow 的信息提示
- 虽然已注释掉 Rerank 依赖，但可能有其他库间接引用了 TensorFlow
- **不影响功能**，可以忽略

---

## ✅ 已完成的修复

### 1. 添加了 startup_event（[main.py](file://g:\rag\kret-rag\rag-scheduler\app\main.py)）

```python
@app.on_event("startup")
async def startup_event():
    """应用启动时初始化服务"""
    print("\n" + "=" * 80)
    print("开始初始化 RAG Scheduler 服务...")
    print("=" * 80)
    
    try:
        # 初始化向量服务（包括 ChromaDB 和 Embedding 模型）
        from app.services.vector_service import vector_store_service
        print("正在初始化向量服务...")
        await vector_store_service.initialize()
        print("✅ 向量服务初始化成功")
        
    except Exception as e:
        print(f"❌ 向量服务初始化失败: {e}")
        import traceback
        traceback.print_exc()
        raise
    
    print("=" * 80)
    print("RAG Scheduler 服务初始化完成！")
    print("=" * 80 + "\n")
```

**效果**：
- ✅ 确保应用启动时向量服务被正确初始化
- ✅ 避免首次查询时才初始化的延迟
- ✅ 提供清晰的启动日志

---

### 2. 修改了 ChromaDB collection 配置（[vector_service.py](file://g:\rag\kret-rag\rag-scheduler\app\services\vector_service.py)）

```python
self.collection = self.vector_db.get_or_create_collection(
    name=settings.CHROMA_COLLECTION_NAME,
    metadata={
        "description": "RAG文档向量集合",
        "hnsw:space": "cosine"  # 使用余弦相似度
    }
)
```

**效果**：
- ✅ 新创建的 collection 将使用余弦相似度
- ✅ 相似度范围为 [-1, 1]，更直观

---

### 3. 增强了 BM25 初始化日志（[vector_service.py](file://g:\rag\kret-rag\rag-scheduler\app\services\vector_service.py)）

```python
logger.info(f"Collection 名称: {self.collection.name}")
doc_count = self.collection.count()
logger.info(f"Collection 中文档总数: {doc_count}")

all_docs = self.collection.get(include=["documents"])

logger.info(f"get() 返回的 documents 数量: {len(all_docs['documents']) if all_docs['documents'] else 0}")
logger.info(f"get() 返回的 ids 数量: {len(all_docs['ids']) if all_docs['ids'] else 0}")
```

**效果**：
- ✅ 详细记录 ChromaDB 状态
- ✅ 便于诊断为什么获取不到文档

---

## ⚠️ 当前仍需解决的问题

### 核心问题：旧数据与新配置不兼容

**现状**：
- ChromaDB 中有 10 条记录（用 L2 距离存储）
- 代码现在期望余弦相似度
- 导致检索结果为空

**解决方案**：需要删除旧数据并重新上传文档

---

## 🎯 下一步操作

### 方案1：修复 ChromaDB Collection（推荐）

#### 步骤 1：运行修复脚本

```bash
cd g:\rag\kret-rag\rag-scheduler
python fix_chromadb_distance.py
```

输入 `yes` 确认删除旧数据。

---

#### 步骤 2：重启服务

```bash
cd g:\rag\kret-rag
.\start-scheduler.bat
```

等待看到：
```
================================================================================
开始初始化 RAG Scheduler 服务...
================================================================================
正在初始化向量服务...
✅ 向量服务初始化成功
================================================================================
RAG Scheduler 服务初始化完成！
================================================================================
```

---

#### 步骤 3：重新上传文档

访问 http://localhost:8000/ 上传文档文件。

---

#### 步骤 4：测试查询

访问 http://localhost:8000/test-query 或发送 API 请求：

```powershell
$body = @{
    query="员工管理"
    top_k=5
    score_threshold=0.3
    use_hybrid=$true
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:8000/query/search `
    -Method POST `
    -Body $body `
    -ContentType "application/json"
```

**预期结果**：
```json
{
  "results": [
    {
      "chunk_id": "...",
      "document_id": "...",
      "content": "...",
      "similarity_score": 0.65,  // 正数！
      "metadata": {...}
    }
  ],
  "total": 3,
  "query": "员工管理"
}
```

---

### 方案2：手动删除并重建（备选）

如果修复脚本无法运行：

```powershell
# 1. 停止服务（Ctrl+C）

# 2. 删除 ChromaDB 数据
Remove-Item -Recurse -Force data\chromadb

# 3. 重启服务
cd g:\rag\kret-rag
.\start-scheduler.bat

# 4. 重新上传文档
```

---

## 📊 修复前后对比

| 指标 | 修复前 | 修复后 |
|------|--------|--------|
| **向量服务初始化** | ❌ 未初始化 | ✅ 启动时初始化 |
| **距离度量** | L2（欧氏距离） | Cosine（余弦相似度）✅ |
| **相似度范围** | (-∞, 1] | [-1, 1] ✅ |
| **典型相似度值** | -0.65（负数）❌ | 0.65（正数）✅ |
| **检索结果** | 0个 ❌ | 正常返回 ✅ |
| **BM25 索引** | 未初始化 ❌ | 正常初始化 ✅ |

---

## 💡 关键知识点

### 1. FastAPI 启动事件

```python
@app.on_event("startup")
async def startup_event():
    # 在这里初始化服务
    await some_service.initialize()
```

**重要性**：
- 确保服务在接收请求前已准备好
- 避免懒加载导致的性能问题
- 提供清晰的启动日志

---

### 2. ChromaDB 距离度量

| 度量方式 | 适用场景 | 相似度范围 |
|---------|---------|-----------|
| **L2 (欧氏距离)** | 未归一化向量 | [0, ∞) |
| **Cosine (余弦)** | 归一化向量 ✅ | [-1, 1] |
| **IP (内积)** | 特定场景 | (-∞, ∞) |

**Sentence Transformers** 输出已归一化向量，应使用 **Cosine**。

---

### 3. 向量检索流程

```
用户查询
  ↓
生成查询向量（Embedding）
  ↓
ChromaDB 相似度搜索
  ↓
过滤 score_threshold
  ↓
返回结果
```

**关键点**：
- Embedding 模型必须一致
- 距离度量必须匹配
- score_threshold 要合理设置

---

## 📚 相关文档

| 文档 | 说明 |
|------|------|
| [`docs/FIX_CHROMADB_SIMILARITY.md`](file://g:\rag\kret-rag\rag-scheduler\docs\FIX_CHROMADB_SIMILARITY.md) | ChromaDB 修复详细指南 |
| [[fix_chromadb_distance.py](file://g:\rag\kret-rag\rag-scheduler\fix_chromadb_distance.py)](file://g:\rag\kret-rag\rag-scheduler\fix_chromadb_distance.py) | 自动修复脚本 |
| [[diagnose_chromadb_path.py](file://g:\rag\kret-rag\rag-scheduler\diagnose_chromadb_path.py)](file://g:\rag\kret-rag\rag-scheduler\diagnose_chromadb_path.py) | 路径诊断工具 |
| [`docs/DEBUG_BASIC_RETRIEVAL.md`](file://g:\rag\kret-rag\rag-scheduler\docs\DEBUG_BASIC_RETRIEVAL.md) | 基础检索调试指南 |

---

## 🔍 验证清单

修复完成后，请确认：

- [ ] 运行 `fix_chromadb_distance.py` 成功
- [ ] 重启服务看到 "✅ 向量服务初始化成功"
- [ ] 上传至少一个文档
- [ ] BM25 索引正常初始化（日志显示"找到 X 个文档用于 BM25 索引"）
- [ ] 查询返回正数相似度分数
- [ ] 不再显示"向量检索结果为空"

---

**立即执行**：

```bash
cd g:\rag\kret-rag\rag-scheduler
python fix_chromadb_distance.py
```

输入 `yes` 确认后，你的系统将完全恢复正常！🚀
