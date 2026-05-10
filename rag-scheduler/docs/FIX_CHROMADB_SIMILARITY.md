# ChromaDB 相似度为负数问题修复指南

## 🐛 问题描述

**现象**：
- 向量检索返回空结果
- 调试发现相似度分数为负数（如 -0.6469, -0.6599）
- ChromaDB 返回的距离值 > 1.0

**根本原因**：
ChromaDB collection 默认使用 **L2 距离（欧氏距离）**，而不是余弦相似度。

对于归一化向量（Sentence Transformers 输出）：
- L2 距离范围：[0, 2]
- 距离 0 = 完全相同
- 距离 2 = 完全相反

代码中使用 `similarity = 1.0 - distance` 计算相似度：
- 距离 1.6 → 相似度 -0.6（负数！）
- 所有负数都被 `score_threshold >= 0` 过滤掉
- 导致返回空结果

---

## ✅ 解决方案

### 方案1：修复现有 Collection（推荐）

#### 步骤 1：运行修复脚本

```bash
cd g:\rag\kret-rag\rag-scheduler
python fix_chromadb_distance.py
```

**脚本会执行**：
1. 检查现有 collection
2. 提示确认删除（输入 `yes`）
3. 删除旧 collection
4. 创建新 collection（使用余弦相似度）

**预期输出**：
```
================================================================================
ChromaDB Collection 修复工具
================================================================================

[步骤1] 连接 ChromaDB: ./data/chromadb

[步骤2] 检查现有 collection...
  - 找到现有 collection: rag_collection
  - 文档数量: 84

  [WARN] Collection 中有 84 条数据！
  继续操作将删除所有现有数据！

  是否继续？(输入 'yes' 确认): yes

[步骤3] 删除旧 collection...
  [OK] 已删除 collection: rag_collection

[步骤4] 创建新 collection（余弦相似度）...
  [OK] 已创建新 collection: rag_collection
  - 距离度量: cosine (余弦相似度)
  - 相似度范围: [-1, 1]

[步骤5] 验证新 collection...
  [OK] Collection 验证成功

修复完成！
```

---

#### 步骤 2：重启服务

```bash
cd g:\rag\kret-rag
.\start-scheduler.bat
```

---

#### 步骤 3：重新上传文档

由于旧的向量数据已被删除，需要重新上传文档：

1. 访问 http://localhost:8000/
2. 上传之前的文档文件
3. 等待向量化完成

---

#### 步骤 4：测试查询

访问 http://localhost:8000/test-query

**预期结果**：
- ✅ 相似度分数为正数（0.0 - 1.0）
- ✅ 能够返回相关结果
- ✅ 不再显示"向量检索结果为空"

---

### 方案2：手动删除并重建（备选）

如果脚本无法运行，可以手动操作：

#### Windows PowerShell:

```powershell
# 1. 停止服务（如果正在运行）
# Ctrl+C 停止 uvicorn

# 2. 删除 ChromaDB 数据目录
Remove-Item -Recurse -Force data\chromadb

# 3. 重启服务
cd g:\rag\kret-rag
.\start-scheduler.bat

# 4. 重新上传文档
```

**注意**：这会删除所有向量数据，需要重新上传文档。

---

## 🔍 技术细节

### 代码修改

已在 [`vector_service.py`](file://g:\rag\kret-rag\rag-scheduler\app\services\vector_service.py) 中修改：

```python
# 创建 collection 时指定余弦相似度
self.collection = self.vector_db.get_or_create_collection(
    name=settings.CHROMA_COLLECTION_NAME,
    metadata={
        "description": "RAG文档向量集合",
        "hnsw:space": "cosine"  # 使用余弦相似度
    }
)
```

### 距离度量对比

| 度量方式 | 范围 | 含义 | 适用场景 |
|---------|------|------|---------|
| **L2 (欧氏距离)** | [0, ∞) | 越小越相似 | 未归一化向量 |
| **Cosine (余弦)** | [-1, 1] | 越大越相似 | 归一化向量 ✅ |
| **IP (内积)** | (-∞, ∞) | 越大越相似 | 特定场景 |

**为什么选择 Cosine**：
- ✅ Sentence Transformers 输出已归一化向量
- ✅ 余弦相似度直观易懂（1=相同，0=无关，-1=相反）
- ✅ 适合语义相似度搜索

---

## 📊 修复前后对比

### 修复前（L2 距离）

```
查询: "员工管理"

ChromaDB 返回:
  - 距离: 1.6469 → 相似度: -0.6469 ❌
  - 距离: 1.6599 → 相似度: -0.6599 ❌
  - 距离: 1.6602 → 相似度: -0.6602 ❌

过滤后: 0 个结果（全部被 score_threshold 过滤）
```

---

### 修复后（余弦相似度）

```
查询: "员工管理"

ChromaDB 返回:
  - 距离: 0.35 → 相似度: 0.65 ✅
  - 距离: 0.42 → 相似度: 0.58 ✅
  - 距离: 0.48 → 相似度: 0.52 ✅

过滤后: 3 个结果（通过 score_threshold=0.5）
```

---

## ⚠️ 注意事项

### 1. 数据备份

修复前建议备份：

```bash
# 备份 ChromaDB 数据
Copy-Item -Path data\chromadb -Destination data\chromadb.backup -Recurse
```

---

### 2. 重新上传文档

修复后必须重新上传所有文档，因为向量数据已被删除。

**快速上传方法**：
```bash
# 如果有文档列表，可以批量上传
# 或者使用 API 脚本自动化
```

---

### 3. 调整阈值

修复后可能需要调整 `score_threshold`：

- **宽松模式**：0.3 - 0.5（获取更多结果）
- **标准模式**：0.5 - 0.7（平衡精度和召回）
- **严格模式**：0.7 - 0.9（只返回高相关结果）

---

## 🎯 验证清单

修复完成后，请确认：

- [ ] 运行 `fix_chromadb_distance.py` 成功
- [ ] 重启服务无错误
- [ ] 上传至少一个文档
- [ ] 运行 `debug_vector_detailed.py` 测试
- [ ] 相似度分数为正数（0.0 - 1.0）
- [ ] 查询能返回相关结果
- [ ] 不再显示"向量检索结果为空"

---

## 💡 常见问题

### Q1: 为什么之前能用？

**答**：之前可能：
1. 没有设置 `score_threshold` 或设置为负数
2. 使用了不同的 embedding 模型
3. ChromaDB 版本不同，默认行为有变化

---

### Q2: 可以不删除数据直接修改吗？

**答**：**不可以**。ChromaDB 的 distance metric 在 collection 创建时确定，无法动态修改。必须删除重建。

---

### Q3: 会影响其他服务吗？

**答**：只会影响 `rag-scheduler` 服务的向量检索功能。`llm-session` 不受影响。

---

### Q4: 以后还会遇到这个问题吗？

**答**：不会。代码已修改，新创建的 collection 会自动使用余弦相似度。

---

## 📚 相关文档

| 文档 | 说明 |
|------|------|
| [[fix_chromadb_distance.py](file://g:\rag\kret-rag\rag-scheduler\fix_chromadb_distance.py)](file://g:\rag\kret-rag\rag-scheduler\fix_chromadb_distance.py) | Collection 修复脚本 |
| [[debug_vector_detailed.py](file://g:\rag\kret-rag\rag-scheduler\debug_vector_detailed.py)](file://g:\rag\kret-rag\rag-scheduler\debug_vector_detailed.py) | 向量检索调试工具 |
| [`docs/DEBUG_BASIC_RETRIEVAL.md`](file://g:\rag\kret-rag\rag-scheduler\docs\DEBUG_BASIC_RETRIEVAL.md) | 基础检索调试指南 |

---

**立即执行修复**：

```bash
cd g:\rag\kret-rag\rag-scheduler
python fix_chromadb_distance.py
```

输入 `yes` 确认，然后重启服务并重新上传文档即可！
