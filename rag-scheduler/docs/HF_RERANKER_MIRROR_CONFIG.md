# HuggingFace 镜像配置指南

## 📋 问题描述

在加载 Reranker 模型（BAAI/bge-reranker-base）时，出现连接超时错误：

```
Connection to huggingface.co timed out. (connect timeout=10)
```

这是因为默认连接到 `huggingface.co`，在国内网络环境下可能不稳定。

---

## ✅ 解决方案

系统已经配置了 HuggingFace 国内镜像 `https://hf-mirror.com`，但需要重启服务才能生效。

### 方法一：使用启动脚本（推荐）

```bash
cd g:\rag\kret-rag
.\start-scheduler.bat
```

**优势**：
- ✅ 自动设置 `TF_ENABLE_ONEDNN_OPTS=0` 环境变量
- ✅ 自动加载 `.env` 配置文件
- ✅ 包含所有必要的环境变量

---

### 方法二：手动设置环境变量后启动

#### Windows PowerShell:
```powershell
$env:HF_ENDPOINT = "https://hf-mirror.com"
$env:TF_ENABLE_ONEDNN_OPTS = "0"
cd g:\rag\kret-rag\rag-scheduler
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Windows CMD:
```cmd
set HF_ENDPOINT=https://hf-mirror.com
set TF_ENABLE_ONEDNN_OPTS=0
cd g:\rag\kret-rag\rag-scheduler
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🔍 验证配置是否生效

### 1. 检查环境变量

```python
import os
print(os.environ.get('HF_ENDPOINT'))
# 应该输出: https://hf-mirror.com
```

### 2. 查看服务日志

启动服务后，观察日志中是否有以下信息：

```
INFO: 已设置 HuggingFace 国内镜像: https://hf-mirror.com
INFO: 加载 Reranker 模型: BAAI/bge-reranker-base
```

如果看到下载进度条，说明镜像配置已生效。

---

## 📁 相关配置文件

### 1. `.env` 文件
```env
HF_ENDPOINT=https://hf-mirror.com
```

### 2. `app/core/config.py`
```python
# 第10行：模块级别设置环境变量
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

# 第43行：Settings 类中的字段
HF_ENDPOINT: str = "https://hf-mirror.com"
```

### 3. `app/services/hybrid_search_service.py`
```python
# 在 initialize() 方法中再次确认设置
if not os.environ.get('HF_ENDPOINT'):
    os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
```

---

## 🚀 首次加载 Reranker 模型

### 预计时间
- **网络良好**：2-5 分钟
- **使用镜像**：1-3 分钟
- **网络较差**：可能超时

### 模型大小
- **BAAI/bge-reranker-base**: 约 400MB

### 存储位置
模型会缓存到：
```
C:\Users\<用户名>\.cache\huggingface\hub\models--BAAI--bge-reranker-base
```

---

## ⚠️ 常见问题

### Q1: 仍然连接超时怎么办？

**解决方案**：
1. 确认 `.env` 文件中 `HF_ENDPOINT=https://hf-mirror.com`
2. 重启服务（必须重启才能生效）
3. 检查网络连接是否正常

---

### Q2: 如何知道模型是否下载成功？

**检查方法**：
```bash
# 查看缓存目录
ls C:\Users\$env:USERNAME\.cache\huggingface\hub\

# 应该能看到类似这样的目录：
# models--BAAI--bge-reranker-base
```

---

### Q3: 想切换回官方源？

**修改配置**：
1. 编辑 `.env` 文件：
   ```env
   HF_ENDPOINT=https://huggingface.co
   ```

2. 编辑 `app/core/config.py` 第10行：
   ```python
   os.environ["HF_ENDPOINT"] = "https://huggingface.co"
   ```

3. 重启服务

---

### Q4: 不想使用 Rerank 功能？

**禁用方法**：
已在之前的修改中将 [use_rerank](file://g:\rag\kret-rag\rag-scheduler\app\models\schemas.py#L41-L41) 默认值改为 `False`，系统不会自动加载 Reranker 模型。

如需临时启用，可以在 API 请求中设置：
```json
{
  "query": "你的问题",
  "use_rerank": true
}
```

---

## 📊 性能对比

| 配置 | 首次加载时间 | 后续加载 | 稳定性 |
|------|------------|---------|--------|
| huggingface.co（官方） | 5-10分钟 | 快速 | 受网络影响 |
| hf-mirror.com（镜像） | 2-5分钟 | 快速 | 稳定 |
| 本地模型 | 无需下载 | 快速 | 最稳定 |

---

## 💡 最佳实践

1. **始终使用镜像**：在国内环境下推荐使用 `hf-mirror.com`
2. **耐心等待**：首次下载可能需要几分钟，不要中断
3. **检查日志**：观察是否有下载进度提示
4. **避免重复下载**：模型会缓存在本地，后续启动很快
5. **定期清理**：如果磁盘空间不足，可以清理未使用的模型缓存

---

## 🎯 下一步操作

1. **重启服务**（应用新配置）
   ```bash
   cd g:\rag\kret-rag
   .\start-scheduler.bat
   ```

2. **测试查询**
   - 访问 http://localhost:8000/test-query
   - 输入问题测试检索效果

3. **观察日志**
   - 确认没有连接超时错误
   - 查看是否有模型加载成功的提示

---

**提示**：如果重启后仍有问题，请提供完整的错误日志以便进一步诊断。
