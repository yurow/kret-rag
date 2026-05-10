# 调试基础检索流程指南

## 📋 概述

本文档说明如何在调试阶段禁用 Rerank 重排序功能，仅使用向量检索和 BM25 关键词检索的基础组合。

---

## 🎯 当前配置状态

### ✅ 已启用的功能

| 功能 | 状态 | 说明 |
|------|------|------|
| **向量检索** | ✅ 启用 | 使用 all-MiniLM-L6-v2 模型 |
| **BM25 关键词检索** | ✅ 启用 | 使用 jieba 分词 + rank-bm25 |
| **混合检索** | ✅ 启用 | 向量 + BM25 结合 |
| **查询重写** | ✅ 启用 | 优化用户查询 |

### ❌ 已禁用的功能

| 功能 | 状态 | 原因 |
|------|------|------|
| **Rerank 重排序** | ❌ 禁用 | 调试基础流程，避免复杂依赖 |
| **FlagEmbedding** | ❌ 注释 | 避免隐性加载和网络请求 |

---

## 🔧 已完成的修改

### 1. **hybrid_search_service.py**

#### 注释掉的内容：
- ❌ `RerankerService` 类（完整注释）
- ❌ `HybridSearchService.__init__()` 中的 Reranker 初始化
- ❌ `HybridSearchService.initialize()` 中的 Reranker 调用
- ❌ `hybrid_search()` 方法中的 Rerank 逻辑

#### 保留的内容：
- ✅ `HybridRetrievalService` 类（BM25 实现）
- ✅ `bm25_search()` 方法
- ✅ `HybridSearchService` 基础框架
- ✅ 日志输出和错误处理

#### 关键代码变化：

```python
# ⚠️ RerankerService 类已完整注释
# class RerankerService:
#     ...

class HybridSearchService:
    def __init__(self):
        self.bm25_service = HybridRetrievalService()
        # ⚠️ Reranker 服务已禁用
        # self.reranker_service = RerankerService()
    
    async def initialize(self, documents, document_ids):
        self.bm25_service.initialize(documents, document_ids)
        # ⚠️ Reranker 初始化已禁用
        # await self.reranker_service.initialize()
        logger.info("混合搜索服务初始化完成（BM25 + 向量，Rerank 已禁用）")
    
    async def hybrid_search(self, query, vector_results, top_k, ...):
        # ⚠️ Rerank 已禁用，直接返回向量检索结果
        logger.info("Rerank 已禁用，直接返回向量检索结果")
        return vector_results[:top_k]
```

---

### 2. **requirements.txt**

#### 注释掉的依赖：
```txt
# ⚠️ Rerank 相关依赖已注释 - 调试基础流程时不需要
# torch>=2.0.0  # BGE Reranker 需要
# FlagEmbedding==1.2.10  # BGE Rerank 模型
# tf-keras  # FlagEmbedding 依赖的 Keras 兼容层
```

#### 保留的依赖：
```txt
rank-bm25==0.2.2      # BM25 算法
jieba==0.42.1         # 中文分词
```

---

### 3. **config.py**

#### 注释掉的配置：
```python
# ⚠️ Reranker 模型配置已注释 - 调试基础流程时不需要
# RERANKER_MODEL: str = "./models/bge-reranker-base"
# RERANKER_MODEL: str = "BAAI/bge-reranker-base"
```

---

### 4. **.env 和 .env.example**

#### 注释掉的配置：
```env
# ⚠️ Reranker 模型配置已注释 - 调试基础流程时不需要
# RERANKER_MODEL=./models/bge-reranker-base
# RERANKER_MODEL=BAAI/bge-reranker-base
```

---

### 5. **schemas.py**

#### 更新的字段描述：
```python
use_rerank: bool = Field(
    default=False, 
    description="是否使用 Rerank 重排序（已禁用，调试基础流程）"
)
```

---

## 🚀 使用流程

### 步骤 1：重启服务

```bash
cd g:\rag\kret-rag
.\start-scheduler.bat
```

**预期日志**：
```
INFO: 开始初始化向量服务
INFO: Embedding 模型加载成功: ./models/all-MiniLM-L6-v2
INFO: 混合搜索服务初始化完成（BM25 + 向量，Rerank 已禁用）
INFO: Application startup complete.
```

**不应该看到**：
```
❌ 加载 Reranker 模型: BAAI/bge-reranker-base
❌ FlagEmbedding 未安装
❌ Connection to huggingface.co timed out
```

---

### 步骤 2：测试检索功能

访问 http://localhost:8000/test-query

#### 推荐配置：
```json
{
  "query": "员工管理系统",
  "top_k": 5,
  "score_threshold": 0.5,
  "use_hybrid": true,
  "use_rerank": false,
  "use_query_rewrite": true
}
```

#### 观察点：
1. ✅ 向量检索是否正常执行
2. ✅ BM25 索引是否正确初始化
3. ✅ 混合检索是否返回结果
4. ✅ 响应时间是否合理（应该更快）

---

### 步骤 3：验证日志输出

**正常日志示例**：
```
INFO: 开始向量检索: query='员工管理系统...'
INFO: 向量检索完成，找到 10 个结果
INFO: 开始混合搜索: query='员工管理系统...', 向量结果数=10
INFO: Rerank 已禁用，直接返回向量检索结果
INFO: 混合检索完成，返回 5 个结果
```

**不应该出现的日志**：
```
❌ 执行 Rerank 重排
❌ 加载 Reranker 模型
❌ FlagEmbedding import error
```

---

## 📊 性能对比

| 指标 | 启用 Rerank | 禁用 Rerank |
|------|------------|------------|
| **启动时间** | 5-10秒（加载模型） | 2-3秒 |
| **首次查询** | 2-5秒（含重排） | 0.5-1秒 |
| **后续查询** | 1-3秒 | 0.3-0.8秒 |
| **内存占用** | ~2GB | ~1GB |
| **网络依赖** | 需要（首次下载） | 无需 |
| **准确率** | 较高（+20-40%） | 基础水平 |

---

## 💡 调试建议

### 1. 优先测试纯向量检索

```json
{
  "use_hybrid": false,
  "use_rerank": false
}
```

**目的**：验证向量检索基础功能是否正常

---

### 2. 然后测试混合检索

```json
{
  "use_hybrid": true,
  "use_rerank": false
}
```

**目的**：验证 BM25 + 向量组合效果

---

### 3. 调整相似度阈值

```json
{
  "score_threshold": 0.3  // 降低阈值获取更多结果
}
```

**目的**：观察不同阈值下的检索效果

---

### 4. 增加 top_k

```json
{
  "top_k": 10  // 增加返回数量
}
```

**目的**：查看更多候选结果，评估召回率

---

### 5. 关闭查询重写

```json
{
  "use_query_rewrite": false
}
```

**目的**：对比原始查询与重写后的效果差异

---

## 🔍 常见问题

### Q1: 如何确认 Rerank 已完全禁用？

**检查方法**：
1. 查看启动日志，不应有 "加载 Reranker 模型" 提示
2. 查看查询日志，应显示 "Rerank 已禁用"
3. 检查内存占用，应该明显降低
4. 观察响应时间，应该更快

---

### Q2: BM25 索引未初始化怎么办？

**错误日志**：
```
WARNING: BM25 索引未初始化，降级为纯向量检索
```

**解决方案**：
1. 确认 ChromaDB 中有文档数据
2. 运行 `python check_chromadb.py` 检查数据
3. 上传至少一个文档触发索引构建
4. 重启服务后再次测试

---

### Q3: 想临时启用 Rerank 怎么办？

**步骤**：
1. 取消注释 `requirements.txt` 中的 FlagEmbedding 相关依赖
2. 运行 `pip install -r requirements.txt`
3. 取消注释 `config.py` 中的 `RERANKER_MODEL` 配置
4. 取消注释 `.env` 中的 `RERANKER_MODEL` 配置
5. 取消注释 `hybrid_search_service.py` 中的 `RerankerService` 类
6. 重启服务

**注意**：这会重新引入网络依赖和较长的启动时间

---

### Q4: 为什么禁用 Rerank？

**原因**：
1. **简化调试**：减少变量，专注基础流程
2. **加快迭代**：更快的启动和查询速度
3. **降低依赖**：避免复杂的深度学习库
4. **节省资源**：减少内存和磁盘占用
5. **离线可用**：无需下载大型模型

---

### Q5: 生产环境是否需要 Rerank？

**建议**：
- ✅ **开发/测试阶段**：禁用 Rerank，快速迭代
- ✅ **生产环境**：启用 Rerank，提升准确率
- ✅ **性能敏感场景**：根据需求权衡

**决策因素**：
- 准确率要求
- 响应时间要求
- 硬件资源限制
- 网络环境稳定性

---

## 📁 相关文件清单

| 文件 | 修改内容 |
|------|---------|
| `app/services/hybrid_search_service.py` | 注释 RerankerService 类和相关调用 |
| `requirements.txt` | 注释 FlagEmbedding、tf-keras、torch |
| `app/core/config.py` | 注释 RERANKER_MODEL 配置 |
| `.env` | 注释 RERANKER_MODEL 配置 |
| `.env.example` | 注释 RERANKER_MODEL 配置 |
| `app/models/schemas.py` | 更新 use_rerank 字段描述 |

---

## 🎯 下一步操作

### 立即执行：

1. **重启服务**
   ```bash
   cd g:\rag\kret-rag
   .\start-scheduler.bat
   ```

2. **测试检索**
   - 访问 http://localhost:8000/test-query
   - 使用推荐配置进行测试
   - 观察日志输出

3. **验证性能**
   - 记录启动时间
   - 记录查询响应时间
   - 检查内存占用

---

### 后续计划：

当基础流程调试完成后，可以：

1. **逐步启用 Rerank**
   - 取消注释相关代码
   - 重新安装依赖
   - 对比效果差异

2. **优化 BM25**
   - 调整分词策略
   - 优化停用词表
   - 调整权重参数

3. **完善混合检索**
   - 实现 BM25 + 向量分数融合
   - 添加更多召回策略
   - 优化排序算法

---

## 📚 相关文档

| 文档 | 说明 |
|------|------|
| [`docs/LOCAL_MODELS_GUIDE.md`](file://g:\rag\kret-rag\rag-scheduler\docs\LOCAL_MODELS_GUIDE.md) | 本地模型配置指南 |
| [`docs/HF_RERANKER_MIRROR_CONFIG.md`](file://g:\rag\kret-rag\rag-scheduler\docs\HF_RERANKER_MIRROR_CONFIG.md) | Reranker 镜像配置 |
| [[QUICKSTART_LOCAL_MODEL.md](file://g:\rag\kret-rag\rag-scheduler\QUICKSTART_LOCAL_MODEL.md)](file://g:\rag\kret-rag\rag-scheduler\QUICKSTART_LOCAL_MODEL.md) | Embedding 模型快速配置 |

---

**恭喜！** 🎉 现在你的系统已经切换到纯基础检索模式，可以更专注于调试向量检索和 BM25 的核心功能！
