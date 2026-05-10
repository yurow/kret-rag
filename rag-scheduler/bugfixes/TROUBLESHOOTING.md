# RAG Scheduler 启动问题排查指南

## 📋 常见问题及解决方案

### 1. ModuleNotFoundError: No module named 'app'

**问题描述：**
```
ModuleNotFoundError: No module named 'app'
```

**原因：**
- 工作目录不正确（不在 `rag-scheduler` 目录下）
- 缺少 `__init__.py` 文件

**解决方案：**

#### 方法1：使用启动脚本（推荐）
```bash
# Windows
start-scheduler.bat

# Linux/Mac
./start-scheduler.sh
```

#### 方法2：手动切换到正确目录
```bash
cd g:\rag\kret-rag\rag-scheduler
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 方法3：检查 __init__.py 文件
确保以下文件存在：
```
rag-scheduler/
├── app/
│   ├── __init__.py          # ✅ 必须有
│   ├── main.py
│   ├── routes/
│   │   └── __init__.py      # ✅ 必须有
│   ├── services/
│   │   └── __init__.py      # ✅ 必须有
│   ├── models/
│   │   └── __init__.py      # ✅ 必须有
│   └── core/
│       └── __init__.py      # ✅ 必须有
```

---

### 2. ImportError: cannot import name 'cached_download' from 'huggingface_hub'

**问题描述：**
```
ImportError: cannot import name 'cached_download' from 'huggingface_hub'
```

**原因：**
- `sentence-transformers==2.2.2` 版本太旧，与新版的 `huggingface_hub` 不兼容

**解决方案：**
升级 `sentence-transformers` 到 2.7.0 或更高版本：

```bash
pip install sentence-transformers==2.7.0
```

或者重新安装所有依赖：
```bash
cd rag-scheduler
pip install -r requirements.txt
```

---

### 3. ValueError: Keras 3 compatibility issue

**问题描述：**
```
ValueError: Your currently installed version of Keras is Keras 3, but this is not yet supported in Transformers. 
Please install the backwards-compatible tf-keras package with `pip install tf-keras`.
```

**原因：**
- 最新版的 `sentence-transformers` (5.x) 需要 `tf-keras` 依赖（约350MB）

**解决方案：**
使用 `sentence-transformers==2.7.0` 稳定版本，它不需要 `tf-keras`：

```bash
pip uninstall sentence-transformers
pip install sentence-transformers==2.7.0
```

---

### 4. Connection timeout to huggingface.co

**问题描述：**
```
TimeoutError: timed out
Connection to huggingface.co timed out. (connect timeout=10)
```

**原因：**
- 首次启动时需要从 Hugging Face 下载嵌入模型（all-MiniLM-L6-v2）
- 网络连接不稳定或被墙

**解决方案：**

#### 方法1：配置国内镜像（推荐）
在 `.env` 文件中添加：
```env
HF_ENDPOINT=https://hf-mirror.com
```

或者设置环境变量：
```bash
# Windows
set HF_ENDPOINT=https://hf-mirror.com

# Linux/Mac
export HF_ENDPOINT=https://hf-mirror.com
```

#### 方法2：预先下载模型
```python
from sentence_transformers import SentenceTransformer
import os

os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
model = SentenceTransformer('all-MiniLM-L6-v2')
```

#### 方法3：使用本地模型
如果已经下载过模型，可以指定本地路径：
```env
EMBEDDING_MODEL=./models/all-MiniLM-L6-v2
```

---

### 5. 缺少 rank-bm25 或 jieba 模块

**问题描述：**
```
ModuleNotFoundError: No module named 'rank_bm25'
ModuleNotFoundError: No module named 'jieba'
```

**解决方案：**
```bash
pip install rank-bm25==0.2.2 jieba==0.42.1
```

或者重新安装所有依赖：
```bash
pip install -r requirements.txt
```

---

## 🔧 完整安装步骤

### 1. 安装 Python 依赖
```bash
cd g:\rag\kret-rag\rag-scheduler
pip install -r requirements.txt
```

### 2. 验证依赖
```bash
python test_dependencies.py
```

应该看到所有依赖项显示为 ✅

### 3. 配置环境变量
复制 `.env.example` 为 `.env` 并配置：
```bash
cp .env.example .env
```

编辑 `.env` 文件，确保包含：
```env
HF_ENDPOINT=https://hf-mirror.com  # 解决网络问题
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

### 4. 启动服务
```bash
# 方式1：使用启动脚本
start-scheduler.bat

# 方式2：手动启动
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. 访问测试页面
- API文档: http://localhost:8000/docs
- 上传测试: http://localhost:8000/
- **查询测试**: http://localhost:8000/test-query ⭐

---

## 📊 依赖版本说明

| 包名 | 版本 | 说明 |
|------|------|------|
| sentence-transformers | 2.7.0 | 稳定版本，无需tf-keras |
| transformers | >=4.40.0 | 与sentence-transformers兼容 |
| huggingface-hub | >=0.15.1 | 支持新版API |
| chromadb | 0.4.18 | 向量数据库 |
| rank-bm25 | 0.2.2 | BM25混合检索 |
| jieba | 0.42.1 | 中文分词 |

---

## 💡 最佳实践

1. **始终在项目根目录执行命令**
   ```bash
   cd g:\rag\kret-rag\rag-scheduler
   ```

2. **使用虚拟环境**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

3. **定期更新依赖**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

4. **首次启动前预下载模型**
   ```python
   python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
   ```

5. **检查日志**
   启动时注意查看控制台输出，确认：
   - ✅ 数据库迁移完成
   - ✅ 向量服务初始化成功
   - ✅ 服务监听在 0.0.0.0:8000

---

## 🆘 获取帮助

如果以上方案都无法解决问题：

1. 检查 Python 版本（推荐 3.10+）
   ```bash
   python --version
   ```

2. 清理缓存后重新安装
   ```bash
   pip cache purge
   pip install -r requirements.txt --force-reinstall
   ```

3. 查看详细错误日志
   ```bash
   uvicorn app.main:app --log-level debug
   ```

4. 提交 Issue 时提供：
   - 完整的错误堆栈
   - Python 版本
   - 操作系统
   - 已安装的包版本 (`pip list`)
