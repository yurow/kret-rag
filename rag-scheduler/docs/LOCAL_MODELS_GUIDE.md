# 本地模型配置快速指南

## 📋 概述

本指南帮助你将所有 AI 模型下载到本地，避免每次启动服务都联网下载。

---

## 🎯 使用的模型

| 模型名称 | 用途 | 大小 | 状态 |
|---------|------|------|------|
| **all-MiniLM-L6-v2** | 文本向量化（Embedding） | ~100MB | ✅ 已支持本地化 |
| **bge-reranker-base** | 检索结果重排序（Rerank） | ~400MB | ✅ 已支持本地化 |

**总计**：约 500MB

---

## 🚀 快速开始（3步完成）

### 步骤 1：运行下载脚本

```bash
cd g:\rag\kret-rag\rag-scheduler
python download_all_models.py
```

**预期输出**：
```
================================================================================
KRET-RAG 模型下载工具
================================================================================

此脚本将下载所有必需的模型到本地，避免每次启动都联网
预计总大小：约 500MB

提示：首次下载可能需要较长时间，请耐心等待

================================================================================
1. 下载 Embedding 模型
================================================================================
✓ Embedding 模型已存在于: ./models/all-MiniLM-L6-v2
  大小: 90.86 MB

================================================================================
2. 下载 Reranker 模型
================================================================================
正在下载 Reranker 模型: BAAI/bge-reranker-base
保存到: ./models/bge-reranker-base
这可能需要几分钟时间，请耐心等待...
  - 下载模型权重...
  - 下载分词器...
  - 保存到本地...
✓ Reranker 模型下载成功！
  位置: G:\rag\kret-rag\rag-scheduler\models\bge-reranker-base
  大小: 387.45 MB
```

---

### 步骤 2：验证配置文件

确认 `.env` 文件中包含以下配置：

```env
# Embedding 模型（本地路径）
EMBEDDING_MODEL=./models/all-MiniLM-L6-v2

# Reranker 模型（本地路径）
RERANKER_MODEL=./models/bge-reranker-base

# HuggingFace 镜像（用于首次下载）
HF_ENDPOINT=https://hf-mirror.com
```

✅ 这些配置已经在之前的修改中自动添加，通常无需手动修改。

---

### 步骤 3：重启服务

```bash
cd g:\rag\kret-rag
.\start-scheduler.bat
```

**预期日志**：
```
INFO: 加载 Embedding 模型: ./models/all-MiniLM-L6-v2
INFO: Embedding 模型加载成功
INFO: 使用本地模型: G:\rag\kret-rag\rag-scheduler\models\bge-reranker-base
INFO: Reranker 模型加载成功
```

---

## ✅ 验证是否成功

### 方法 1：检查模型目录

```bash
# Windows PowerShell
Get-ChildItem models -Recurse | Select-Object FullName, Length | Format-Table -AutoSize
```

**应该看到**：
```
models/all-MiniLM-L6-v2/
  ├── config.json
  ├── model.safetensors    (~90MB)
  ├── tokenizer.json
  └── ...

models/bge-reranker-base/
  ├── config.json
  ├── pytorch_model.bin    (~380MB)
  ├── tokenizer.json
  └── ...
```

---

### 方法 2：测试服务启动时间

```bash
Measure-Command { .\start-scheduler.bat }
```

**预期结果**：
- **使用本地模型**：3-5 秒内完成启动
- **使用在线模型**：2-5 分钟（需要下载）

---

### 方法 3：查看服务日志

启动后观察日志，**不应该看到**：
```
❌ Downloading from huggingface.co
❌ Connection to huggingface.co timed out
❌ Max retries exceeded
```

**应该看到**：
```
✅ 使用本地模型: G:\...\models\all-MiniLM-L6-v2
✅ 使用本地模型: G:\...\models\bge-reranker-base
✅ 模型加载成功
```

---

## 📁 目录结构

```
rag-scheduler/
│
├── models/                          # ✨ 本地模型存储
│   ├── all-MiniLM-L6-v2/           # Embedding 模型 (~100MB)
│   │   ├── config.json
│   │   ├── model.safetensors       # 模型权重
│   │   ├── tokenizer.json          # 分词器
│   │   ├── vocab.txt
│   │   └── ...
│   │
│   └── bge-reranker-base/          # Reranker 模型 (~400MB)
│       ├── config.json
│       ├── pytorch_model.bin       # 模型权重
│       ├── tokenizer.json          # 分词器
│       ├── special_tokens_map.json
│       └── ...
│
├── data/                            # 数据目录
│   ├── chromadb/                    # ChromaDB 向量数据库
│   └── documents.db                 # SQLite 元数据
│
├── app/                             # 应用代码
│   ├── core/
│   │   └── config.py                # 配置 EMBEDDING_MODEL, RERANKER_MODEL
│   └── services/
│       ├── vector_service.py        # 向量服务
│       └── hybrid_search_service.py # 混合检索（含 Rerank）
│
├── .env                             # 环境配置
├── .env.example                     # 配置模板
└── download_all_models.py           # ✨ 模型下载脚本
```

---

## 🔧 常见问题

### Q1: 如何知道模型是否已下载？

```bash
# 检查目录是否存在
Test-Path models\all-MiniLM-L6-v2
Test-Path models\bge-reranker-base

# 查看文件大小
Get-ChildItem models -Recurse -File | Measure-Object -Property Length -Sum
```

---

### Q2: 想重新下载怎么办？

```bash
# 删除现有模型
Remove-Item -Recurse -Force models\all-MiniLM-L6-v2
Remove-Item -Recurse -Force models\bge-reranker-base

# 重新运行下载脚本
python download_all_models.py
```

---

### Q3: 磁盘空间不足？

**检查空间**：
```bash
Get-PSDrive C | Select-Object Used, Free
```

**清理方案**：
- 删除未使用的模型
- 清理 HuggingFace 缓存：`Remove-Item -Recurse -Force "$env:USERPROFILE\.cache\huggingface"`
- 建议预留至少 1GB 空间

---

### Q4: 想切换回在线模型？

**修改 `.env`**：
```env
# 注释掉本地路径，启用在线模型
# EMBEDDING_MODEL=./models/all-MiniLM-L6-v2
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# RERANKER_MODEL=./models/bge-reranker-base
RERANKER_MODEL=BAAI/bge-reranker-base
```

然后重启服务

---

### Q5: 不想使用 Rerank 功能？

**当前状态**：[use_rerank](file://g:\rag\kret-rag\rag-scheduler\app\models\schemas.py#L41-L41) 默认值为 `False`，系统不会自动加载 Reranker 模型。

**如需临时启用**：
在 API 请求中设置：
```json
{
  "query": "你的问题",
  "use_rerank": true
}
```

---

## 📊 性能对比

| 指标 | 在线模型 | 本地模型 |
|------|---------|---------|
| 首次启动 | 2-5分钟 | 3-5秒 |
| 后续启动 | 10-30秒 | 2-3秒 |
| 网络依赖 | 需要 | 不需要 |
| 稳定性 | 受网络影响 | 稳定 |
| 离线可用 | ❌ | ✅ |

---

## 💡 最佳实践

### 1. 开发环境
- ✅ 使用本地模型，加快迭代速度
- ✅ 避免网络波动影响开发效率

### 2. 生产环境
- ✅ 部署时包含 `models/` 目录
- ✅ 确保服务器有足够磁盘空间
- ✅ 定期备份模型文件

### 3. 团队协作
- ✅ 将 `download_all_models.py` 加入项目
- ✅ 在 README 中说明模型下载步骤
- ⚠️ 不要将模型文件提交到 Git（太大）

---

## 🎯 下一步操作

1. **运行下载脚本**
   ```bash
   python download_all_models.py
   ```

2. **重启服务**
   ```bash
   cd g:\rag\kret-rag
   .\start-scheduler.bat
   ```

3. **测试功能**
   - 访问 http://localhost:8000/test-query
   - 上传文档并测试检索

4. **监控日志**
   - 确认没有网络连接错误
   - 观察模型加载时间

---

## 📚 相关文档

| 文档 | 说明 |
|------|------|
| [`QUICKSTART_LOCAL_MODEL.md`](file://g:\rag\kret-rag\rag-scheduler\QUICKSTART_LOCAL_MODEL.md) | Embedding 模型快速配置 |
| [`docs/LOCAL_MODEL_GUIDE.md`](file://g:\rag\kret-rag\rag-scheduler\docs\LOCAL_MODEL_GUIDE.md) | 本地模型完整指南 |
| [`docs/HF_MIRROR_CONFIG.md`](file://g:\rag\kret-rag\rag-scheduler\docs\HF_MIRROR_CONFIG.md) | HuggingFace镜像配置 |
| [[download_all_models.py](file://g:\rag\kret-rag\rag-scheduler\download_all_models.py)](file://g:\rag\kret-rag\rag-scheduler\download_all_models.py) | 统一模型下载脚本 |

---

**恭喜！** 🎉 现在你的系统已经完全本地化，无需联网即可运行！
