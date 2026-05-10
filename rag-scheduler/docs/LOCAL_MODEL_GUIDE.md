# 本地模型使用指南

## 📋 概述

本指南介绍如何下载并使用本地 Embedding 模型，避免每次启动服务时都从网络下载。

---

## 🎯 为什么使用本地模型？

### 优势

1. **启动速度快** - 无需等待模型下载（节省2-5分钟）
2. **离线可用** - 不依赖网络连接
3. **版本可控** - 确保使用固定版本的模型
4. **节省带宽** - 只需下载一次，多次使用
5. **稳定性高** - 避免因网络问题导致启动失败

### 适用场景

- ✅ 生产环境部署
- ✅ 开发测试环境
- ✅ 网络不稳定地区
- ✅ 需要快速重启的场景

---

## 🚀 快速开始

### 步骤1：下载模型到本地

运行预下载脚本：

```bash
cd g:\rag\kret-rag\rag-scheduler
python download_embedding_model.py
```

**预期输出**：
```
================================================================================
KRET-RAG Embedding 模型下载工具
================================================================================

模型名称: sentence-transformers/all-MiniLM-L6-v2
本地路径: G:\rag\kret-rag\rag-scheduler\models\all-MiniLM-L6-v2

正在下载模型（约100MB），请耐心等待...
提示：首次下载可能需要几分钟时间

正在保存模型到: G:\rag\kret-rag\rag-scheduler\models\all-MiniLM-L6-v2

================================================================================
✅ 模型下载成功！
================================================================================

模型路径: G:\rag\kret-rag\rag-scheduler\models\all-MiniLM-L6-v2

下一步操作：
1. 确认 .env 文件中 EMBEDDING_MODEL=./models/all-MiniLM-L6-v2
2. 启动服务: .\start-scheduler.bat
3. 服务将直接使用本地模型，无需联网下载
```

---

### 步骤2：验证配置

检查 `.env` 文件中的配置：

```env
# 使用本地模型路径
EMBEDDING_MODEL=./models/all-MiniLM-L6-v2
```

**注意**：
- ✅ 使用相对路径 `./models/...`
- ❌ 不要使用绝对路径（除非必要）
- ❌ 不要使用模型名称（如 `sentence-transformers/...`）

---

### 步骤3：启动服务

```bash
.\start-scheduler.bat
```

**观察日志**：
- 应该看到 "向量服务初始化成功"
- 不应该有模型下载的进度条
- 启动时间应该在3秒以内

---

## 📁 目录结构

```
rag-scheduler/
│
├── models/                      # ✨ 本地模型存储目录
│   └── all-MiniLM-L6-v2/       # Embedding 模型
│       ├── config.json
│       ├── model.safetensors
│       ├── tokenizer.json
│       ├── tokenizer_config.json
│       ├── special_tokens_map.json
│       ├── vocab.txt
│       └── modules.json
│
├── app/
│   └── core/
│       └── config.py            # 配置 EMBEDDING_MODEL=./models/...
│
├── .env                         # 环境变量配置
├── .env.example                 # 配置模板
└── download_embedding_model.py  # 模型下载脚本
```

---

## 🔧 配置说明

### 方式1：使用本地模型（推荐）

**.env 配置**：
```env
EMBEDDING_MODEL=./models/all-MiniLM-L6-v2
```

**优势**：
- ✅ 启动快
- ✅ 离线可用
- ✅ 版本稳定

**适用**：生产环境、日常开发

---

### 方式2：使用在线模型（备选）

**.env 配置**：
```env
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

**行为**：
- 首次启动时自动下载模型
- 下载到 HuggingFace 缓存目录
- 后续启动使用缓存

**劣势**：
- ❌ 首次启动慢（2-5分钟）
- ❌ 依赖网络
- ❌ 可能因网络问题失败

**适用**：临时测试、不想管理本地文件

---

## 🔄 切换模型来源

### 从在线切换到本地

1. 运行下载脚本：
   ```bash
   python download_embedding_model.py
   ```

2. 修改 `.env`：
   ```diff
   - EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
   + EMBEDDING_MODEL=./models/all-MiniLM-L6-v2
   ```

3. 重启服务

---

### 从本地切换到在线

1. 修改 `.env`：
   ```diff
   - EMBEDDING_MODEL=./models/all-MiniLM-L6-v2
   + EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
   ```

2. （可选）删除本地模型释放空间：
   ```bash
   Remove-Item -Recurse -Force models\all-MiniLM-L6-v2
   ```

3. 重启服务

---

## 🧪 验证本地模型

### 方法1：检查目录

```bash
cd g:\rag\kret-rag\rag-scheduler
Get-ChildItem models\all-MiniLM-L6-v2 | Select-Object Name, Length
```

**预期输出**：
```
Name                    Length
----                    ------
config.json             190
model.safetensors       90868776
tokenizer.json          466081
tokenizer_config.json   350
special_tokens_map.json 112
vocab.txt               231508
modules.json            349
```

**关键文件**：
- `model.safetensors` - 模型权重（约90MB）
- `tokenizer.json` - 分词器
- `config.json` - 配置文件

---

### 方法2：测试加载

创建测试脚本 `test_local_model.py`：

```python
"""测试本地模型加载"""
from sentence_transformers import SentenceTransformer
import time

print("测试本地模型加载...")
start_time = time.time()

# 加载本地模型
model_path = "./models/all-MiniLM-L6-v2"
model = SentenceTransformer(model_path)

elapsed = time.time() - start_time
print(f"✅ 模型加载成功！耗时: {elapsed:.2f}秒")

# 测试编码
test_texts = ["Hello World", "你好世界"]
embeddings = model.encode(test_texts)
print(f"✅ 编码测试成功！生成 {len(embeddings)} 个向量")
print(f"   向量维度: {embeddings[0].shape}")
```

运行测试：
```bash
python test_local_model.py
```

**预期输出**：
```
测试本地模型加载...
✅ 模型加载成功！耗时: 0.50秒
✅ 编码测试成功！生成 2 个向量
   向量维度: (384,)
```

---

## 💡 最佳实践

### 1. 首次部署流程

```bash
# 1. 克隆项目
git clone <repository-url>
cd rag-scheduler

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env

# 4. 下载模型
python download_embedding_model.py

# 5. 启动服务
.\start-scheduler.bat
```

---

### 2. CI/CD 集成

在 Dockerfile 中预下载模型：

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 预下载模型
COPY download_embedding_model.py .
RUN python download_embedding_model.py

# 复制应用代码
COPY . .

# 启动服务
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

### 3. 定期更新模型

如果需要更新到最新版本的模型：

```bash
# 1. 备份旧模型
mv models/all-MiniLM-L6-v2 models/all-MiniLM-L6-v2.backup

# 2. 重新下载
python download_embedding_model.py

# 3. 测试新功能
python test_local_model.py

# 4. 如果没问题，删除备份
Remove-Item -Recurse -Force models\all-MiniLM-L6-v2.backup
```

---

### 4. 多模型管理

如果需要支持多个模型：

```
models/
├── all-MiniLM-L6-v2/          # 默认模型（384维）
├── all-mpnet-base-v2/         # 高性能模型（768维）
└── paraphrase-multilingual/   # 多语言模型
```

在 `.env` 中切换：
```env
# 默认模型
EMBEDDING_MODEL=./models/all-MiniLM-L6-v2

# 高性能模型（更准确但更慢）
# EMBEDDING_MODEL=./models/all-mpnet-base-v2

# 多语言模型（支持中文更好）
# EMBEDDING_MODEL=./models/paraphrase-multilingual
```

---

## 🔍 故障排查

### Q1: 模型加载失败，提示找不到文件

**错误信息**：
```
OSError: Model path './models/all-MiniLM-L6-v2' does not exist
```

**解决方案**：
```bash
# 1. 检查目录是否存在
Test-Path models\all-MiniLM-L6-v2

# 2. 如果不存在，重新下载
python download_embedding_model.py

# 3. 检查 .env 配置是否正确
cat .env | findstr EMBEDDING_MODEL
```

---

### Q2: 模型加载很慢

**可能原因**：
1. 磁盘速度慢（HDD vs SSD）
2. 内存不足
3. 首次加载需要编译

**解决方案**：
```python
# 在代码中添加缓存
from sentence_transformers import SentenceTransformer

# 全局变量
_model_cache = {}

def get_model():
    if 'embedding' not in _model_cache:
        _model_cache['embedding'] = SentenceTransformer('./models/all-MiniLM-L6-v2')
    return _model_cache['embedding']
```

---

### Q3: 磁盘空间不足

**检查空间**：
```bash
# Windows PowerShell
Get-PSDrive C | Select-Object Used, Free

# Linux
df -h
```

**清理方案**：
```bash
# 1. 删除未使用的模型
Remove-Item -Recurse -Force models\unused-model

# 2. 清理 HuggingFace 缓存
Remove-Item -Recurse -Force "$env:USERPROFILE\.cache\huggingface"

# 3. 压缩模型（不推荐，会影响性能）
```

**空间需求**：
- all-MiniLM-L6-v2: ~100MB
- all-mpnet-base-v2: ~400MB
- 建议预留至少 1GB 空间

---

### Q4: 权限问题

**错误信息**：
```
PermissionError: [WinError 5] Access is denied
```

**解决方案**：
```bash
# Windows: 以管理员身份运行
# 右键 PowerShell -> 以管理员身份运行

# 或者修改文件夹权限
icacls models /grant Everyone:F
```

---

## 📊 性能对比

### 启动时间对比

| 模型来源 | 首次启动 | 后续启动 | 说明 |
|---------|---------|---------|------|
| 在线下载 | 2-5分钟 | 10-30秒 | 依赖网络和缓存 |
| 本地模型 | 3-5秒 | 2-3秒 | 直接加载 |

### 内存占用

| 模型 | 磁盘大小 | 内存占用 | 向量维度 |
|------|---------|---------|---------|
| all-MiniLM-L6-v2 | ~100MB | ~300MB | 384 |
| all-mpnet-base-v2 | ~400MB | ~1.2GB | 768 |
| paraphrase-multilingual | ~500MB | ~1.5GB | 768 |

---

## 📚 相关资源

### 官方文档
- [Sentence Transformers](https://www.sbert.net/)
- [HuggingFace Models](https://huggingface.co/models)
- [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)

### 其他模型推荐
- **all-mpnet-base-v2**: 更高精度，适合英文
- **paraphrase-multilingual-MiniLM-L12-v2**: 多语言支持
- **bge-large-zh**: 中文优化（阿里出品）

### 工具脚本
- [`download_embedding_model.py`](file://g:\rag\kret-rag\rag-scheduler\download_embedding_model.py) - 模型下载脚本
- [`docs/HF_MIRROR_CONFIG.md`](file://g:\rag\kret-rag\rag-scheduler\docs\HF_MIRROR_CONFIG.md) - 镜像配置指南

---

## 🎯 总结

### 配置要点

1. ✅ 运行 `download_embedding_model.py` 下载模型到 `./models/`
2. ✅ 在 `.env` 中设置 `EMBEDDING_MODEL=./models/all-MiniLM-L6-v2`
3. ✅ 确保 models 目录有读取权限
4. ✅ 定期检查模型文件完整性

### 预期效果

- 🚀 启动时间从 2-5分钟 降低到 3-5秒
- ✅ 完全离线可用
- 📦 版本固定，避免兼容性问题
- 💾 节省网络带宽

### 维护建议

- 定期备份 models 目录
- 监控磁盘空间使用情况
- 根据需求选择合适的模型
- 记录模型版本和更新日期

---

**最后更新**: 2026-05-11  
**维护者**: KRET-RAG Team
