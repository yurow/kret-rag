# 检索结果为空问题诊断与解决

## 🐛 问题现象

**请求**：
```json
{
  "query": "一套基于微服务架构的RAG",
  "top_k": 5,
  "score_threshold": 0.7,
  "use_hybrid": true,
  "use_rerank": true,
  "use_query_rewrite": true
}
```

**返回**：
```json
{
  "results": [],
  "total": 0,
  "query": "一套基于微服务架构的RAG"
}
```

---

## 🔍 诊断结果

### **不是编码问题！**

经过详细测试，确认：
- ✅ 查询文本编码正常（UTF-8）
- ✅ ChromaDB 中文档内容编码正常
- ✅ Embedding 模型正常工作
- ✅ 向量检索能返回结果

### **真正的原因：相似度阈值过高**

实际测试结果：
```
最佳相似度分数: 0.444
设置的阈值: 0.7
结果: 所有结果都被过滤掉（0.444 < 0.7）
```

**不同阈值下的结果数量**：
| 阈值 | 结果数量 |
|------|---------|
| 0.1  | 10      |
| 0.3  | 10      |
| 0.5  | 0       |
| 0.7  | 0       |
| 0.9  | 0       |

---

## 💡 根本原因分析

### 1. **ChromaDB 数据与配置不匹配**

- **旧数据**：使用 L2 距离存储
- **新配置**：使用余弦相似度（cosine）
- **影响**：相似度分数不准确

虽然 collection 元数据显示 `"hnsw:space": "cosine"`，但**已存储的向量是用 L2 距离计算的**，导致查询时分数偏低。

---

### 2. **默认阈值设置过高**

当前默认 [score_threshold](file://g:\rag\kret-rag\rag-scheduler\app\models\schemas.py#L38-L38) = **0.7**，对于以下情况可能过高：
- 短查询（如"员工管理"）
- 语义相似但用词不同的查询
- 跨语言查询
- 使用 L2 距离存储的旧数据

---

## ✅ 解决方案

### **方案1：降低相似度阈值（推荐 - 快速）**

在查询时设置更低的阈值：

```json
{
  "query": "一套基于微服务架构的RAG",
  "top_k": 5,
  "score_threshold": 0.3,
  "use_hybrid": true,
  "use_rerank": false,
  "use_query_rewrite": true
}
```

**建议阈值范围**：
- **宽松模式**：0.2 - 0.4（获取更多结果，适合探索）
- **标准模式**：0.4 - 0.6（平衡精度和召回）
- **严格模式**：0.6 - 0.8（只返回高相关结果）

---

### **方案2：禁用阈值过滤（调试用）**

设置 `score_threshold` 为负数可完全禁用过滤：

```json
{
  "query": "一套基于微服务架构的RAG",
  "top_k": 5,
  "score_threshold": -1,
  "use_hybrid": true,
  "use_rerank": false,
  "use_query_rewrite": true
}
```

这会返回所有找到的结果，方便调试。

---

### **方案3：修复 ChromaDB（彻底解决 - 推荐）**

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

---

#### 步骤 3：重新上传文档

访问 http://localhost:8000/ 上传文档。

---

#### 步骤 4：测试查询

使用标准阈值 0.5 测试：

```json
{
  "query": "一套基于微服务架构的RAG",
  "top_k": 5,
  "score_threshold": 0.5,
  "use_hybrid": true,
  "use_rerank": false,
  "use_query_rewrite": true
}
```

**预期结果**：
- ✅ 相似度分数在 0.5 - 0.9 之间
- ✅ 能够返回相关结果
- ✅ 分数更准确可靠

---

## 📊 修复前后对比

| 指标 | 修复前（L2距离） | 修复后（余弦相似度） |
|------|-----------------|---------------------|
| **最佳相似度** | 0.444 | 预计 0.7 - 0.9 |
| **阈值 0.7 的结果** | 0个 | 预计 3-5个 |
| **分数准确性** | ❌ 不准确 | ✅ 准确 |
| **直观性** | ❌ 难以理解 | ✅ 直观易懂 |

---

## 🎯 推荐操作流程

### **立即执行（快速验证）**

1. **降低阈值测试**
   ```json
   {
     "score_threshold": 0.3
   }
   ```

2. **观察结果**
   - 应该能看到结果
   - 检查相似度分数

---

### **后续优化（彻底解决）**

1. **运行修复脚本**
   ```bash
   python fix_chromadb_distance.py
   ```

2. **重新上传文档**

3. **使用标准阈值**
   ```json
   {
     "score_threshold": 0.5
   }
   ```

---

## 💡 最佳实践

### 1. **阈值选择指南**

| 场景 | 推荐阈值 | 说明 |
|------|---------|------|
| **开发调试** | 0.2 - 0.3 | 看到更多结果，便于调试 |
| **一般查询** | 0.4 - 0.5 | 平衡精度和召回 |
| **精确搜索** | 0.6 - 0.7 | 只返回高相关结果 |
| **严格匹配** | 0.8+ | 几乎完全相同的內容 |

---

### 2. **动态调整策略**

```python
# 根据查询长度动态调整阈值
if len(query) < 5:
    threshold = 0.3  # 短查询用较低阈值
elif len(query) < 20:
    threshold = 0.5  # 中等长度
else:
    threshold = 0.6  # 长查询可以用较高阈值
```

---

### 3. **监控和优化**

- 记录每次查询的相似度分布
- 分析用户反馈（点击率、满意度）
- 定期调整默认阈值

---

## 🔧 代码修改说明

已在 [`vector_service.py`](file://g:\rag\kret-rag\rag-scheduler\app\services\vector_service.py) 中添加支持：

```python
# 过滤低于阈值的結果（如果 threshold < 0 则不过滤）
if score_threshold < 0 or similarity_score >= score_threshold:
    # 添加结果
```

现在可以设置 `score_threshold = -1` 来禁用过滤，方便调试。

---

## 📚 相关文档

| 文档 | 说明 |
|------|------|
| [[fix_chromadb_distance.py](file://g:\rag\kret-rag\rag-scheduler\fix_chromadb_distance.py)](file://g:\rag\kret-rag\rag-scheduler\fix_chromadb_distance.py) | ChromaDB 修复脚本 |
| [[test_actual_query.py](file://g:\rag\kret-rag\rag-scheduler\test_actual_query.py)](file://g:\rag\kret-rag\rag-scheduler\test_actual_query.py) | 实际查询测试工具 |
| [`docs/FIX_CHROMADB_SIMILARITY.md`](file://g:\rag\kret-rag\rag-scheduler\docs\FIX_CHROMADB_SIMILARITY.md) | ChromaDB 相似度修复指南 |
| [`docs/FINAL_FIX_SUMMARY.md`](file://g:\rag\kret-rag\rag-scheduler\docs\FINAL_FIX_SUMMARY.md) | 完整修复总结 |

---

## 🎯 立即行动

### **选项 A：快速测试（1分钟）**

在 test-query 页面设置：
```
score_threshold: 0.3
```

然后点击查询，应该能看到结果。

---

### **选项 B：彻底修复（5分钟）**

```bash
cd g:\rag\kret-rag\rag-scheduler
python fix_chromadb_distance.py
# 输入 yes 确认

# 重启服务
cd g:\rag\kret-rag
.\start-scheduler.bat

# 重新上传文档并测试
```

---

**总结**：这不是编码问题，而是**相似度阈值设置过高** + **ChromaDB 数据与配置不匹配**。建议先降低阈值快速验证，然后运行修复脚本彻底解决。
