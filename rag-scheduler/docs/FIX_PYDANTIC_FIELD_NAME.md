# Pydantic 字段名称不匹配问题修复

## 🐛 问题现象

**错误信息**：
```
搜索失败: Search failed: 1 validation error for VectorSearchResult 
score Field required [type=missing, input_value={'chunk_id': '840fdaf3-09...'}, input_type=dict]
```

**触发场景**：
- 执行向量检索查询时
- 创建 [VectorSearchResult](file://g:\rag\kret-rag\rag-scheduler\app\models\schemas.py#L119-L126) 对象时

---

## 🔍 根本原因

**字段名称不一致**：

| 位置 | 使用的字段名 | 期望的字段名 |
|------|------------|------------|
| **Schema 定义** | `score: float` ✅ | `score` |
| **vector_service.py** | `similarity_score=similarity_score` ❌ | `score` |
| **query.py** | `r.similarity_score` ❌ | `r.score` |
| **rag_service.py** | `result.similarity_score` ❌ | `result.score` |

**Pydantic 验证规则**：
- 字段名称必须完全匹配
- `similarity_score` ≠ `score`
- 缺少必需字段会导致 `ValidationError`

---

## ✅ 已完成的修复

### 1. **修复 [vector_service.py](file://g:\rag\kret-rag\rag-scheduler\app\services\vector_service.py)**

**修改前**：
```python
search_results.append(VectorSearchResult(
    chunk_id=doc_id,
    content=results['documents'][0][i],
    similarity_score=similarity_score,  # ❌ 错误的字段名
    document_id=metadata.get('document_id', ''),
    ...
))
```

**修改后**：
```python
search_results.append(VectorSearchResult(
    chunk_id=doc_id,
    content=results['documents'][0][i],
    score=similarity_score,  # ✅ 正确的字段名
    document_id=metadata.get('document_id', ''),
    ...
))
```

---

### 2. **修复 [query.py](file://g:\rag\kret-rag\rag-scheduler\app\routes\query.py)**

**修改前**：
```python
return {
    "results": [
        {
            "chunk_id": r.chunk_id,
            "document_id": r.document_id,
            "content": r.content,
            "similarity_score": r.similarity_score,  # ❌ 错误的字段名
            "metadata": r.metadata
        }
        for r in search_results
    ],
    ...
}
```

**修改后**：
```python
return {
    "results": [
        {
            "chunk_id": r.chunk_id,
            "document_id": r.document_id,
            "content": r.content,
            "score": r.score,  # ✅ 正确的字段名
            "metadata": r.metadata
        }
        for r in search_results
    ],
    ...
}
```

---

### 3. **修复 [rag_service.py](file://g:\rag\kret-rag\rag-scheduler\app\services\rag_service.py)**

**修改前**：
```python
results.append(QueryResultItem(
    chunk_id=result.chunk_id,
    document_id=result.document_id,
    content=result.content,
    score=result.similarity_score,  # ❌ 错误的字段名
    metadata=result.metadata
))
```

**修改后**：
```python
results.append(QueryResultItem(
    chunk_id=result.chunk_id,
    document_id=result.document_id,
    content=result.content,
    score=result.score,  # ✅ 正确的字段名
    metadata=result.metadata
))
```

---

## 📊 Schema 定义参考

### [VectorSearchResult](file://g:\rag\kret-rag\rag-scheduler\app\models\schemas.py#L119-L126)

```python
class VectorSearchResult(BaseModel):
    """向量搜索结果"""
    chunk_id: str
    document_id: str
    content: str
    score: float              # ✅ 必需字段
    metadata: Dict[str, Any] = {}
```

### [QueryResultItem](file://g:\rag\kret-rag\rag-scheduler\app\models\schemas.py#L75-L80)

```python
class QueryResultItem(BaseModel):
    """查询结果项"""
    chunk_id: str
    document_id: str
    content: str
    score: float              # ✅ 必需字段
    metadata: Optional[Dict[str, Any]] = None
```

---

## 💡 最佳实践

### 1. **统一字段命名规范**

**推荐做法**：
- 在 Schema 中定义清晰的字段名
- 所有代码中使用相同的字段名
- 避免使用别名或不同的命名风格

**示例**：
```python
# ✅ 好：统一的命名
class SearchResult(BaseModel):
    score: float

result = SearchResult(score=0.85)
print(result.score)

# ❌ 坏：混用不同的命名
class SearchResult(BaseModel):
    score: float

result = SearchResult(similarity_score=0.85)  # ValidationError!
```

---

### 2. **使用 IDE 类型检查**

启用 Pydantic 插件或类型检查工具：
- PyCharm: 安装 Pydantic 插件
- VS Code: 安装 Pylance + Pyright
- 命令行: 使用 `mypy` 进行静态类型检查

---

### 3. **编写单元测试**

为 Schema 验证编写测试：

```python
def test_vector_search_result_creation():
    """测试 VectorSearchResult 创建"""
    result = VectorSearchResult(
        chunk_id="test_001",
        document_id="doc_001",
        content="测试内容",
        score=0.85,
        metadata={"source": "test"}
    )
    
    assert result.score == 0.85
    assert result.chunk_id == "test_001"
```

---

### 4. **代码审查清单**

在提交代码前检查：
- [ ] 所有 Pydantic 模型实例化使用正确的字段名
- [ ] 字段类型与 Schema 定义一致
- [ ] 必需字段都已提供
- [ ] 可选字段有合理的默认值

---

## 🔧 调试技巧

### 1. **查看完整的验证错误**

```python
try:
    result = VectorSearchResult(...)
except ValidationError as e:
    print(e.json())  # 详细的 JSON 格式错误信息
```

---

### 2. **检查模型字段**

```python
from app.models.schemas import VectorSearchResult

# 查看所有字段
print(VectorSearchResult.model_fields.keys())
# 输出: dict_keys(['chunk_id', 'document_id', 'content', 'score', 'metadata'])

# 查看特定字段信息
print(VectorSearchResult.model_fields['score'])
# 输出: annotation=float required=True
```

---

### 3. **临时禁用验证（仅调试用）**

```python
# ⚠️ 仅用于调试，不要在生产环境使用
VectorSearchResult.model_config = {'validate_assignment': False}
```

---

## 📚 相关文档

| 文档 | 说明 |
|------|------|
| [`app/models/schemas.py`](file://g:\rag\kret-rag\rag-scheduler\app\models\schemas.py) | Pydantic 模型定义 |
| [[vector_service.py](file://g:\rag\kret-rag\rag-scheduler\app\services\vector_service.py)](file://g:\rag\kret-rag\rag-scheduler\app\services\vector_service.py) | 向量检索服务 |
| [[query.py](file://g:\rag\kret-rag\rag-scheduler\app\routes\query.py)](file://g:\rag\kret-rag\rag-scheduler\app\routes\query.py) | 查询路由 |
| [[rag_service.py](file://g:\rag\kret-rag\rag-scheduler\app\services\rag_service.py)](file://g:\rag\kret-rag\rag-scheduler\app\services\rag_service.py) | RAG 查询服务 |

---

## 🎯 验证步骤

修复完成后，请确认：

- [ ] 重启服务无错误
- [ ] 访问 http://localhost:8000/test-query
- [ ] 发送查询请求不再报 ValidationError
- [ ] 返回结果包含 `score` 字段
- [ ] 相似度分数在合理范围内（-1 到 1）

---

**立即测试**：

```bash
cd g:\rag\kret-rag
.\start-scheduler.bat
```

然后访问 http://localhost:8000/test-query 进行测试！
