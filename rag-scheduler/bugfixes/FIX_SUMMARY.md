# 问题修复总结

## 🎯 本次解决的问题

### 1. ModuleNotFoundError: No module named 'app'

**问题原因：**
- PowerShell的 `cd` 命令在某些情况下不会正确切换工作目录
- Windows批处理需要使用 `cd /d` 来确保切换到正确的驱动器和目录

**解决方案：**
✅ 更新了 [start-scheduler.bat](file://g:\rag\kret-rag\start-scheduler.bat)，使用 `cd /d "%~dp0rag-scheduler"` 确保正确切换目录
✅ 创建了 [TROUBLESHOOTING.md](file://g:\rag\kret-rag\rag-scheduler\TROUBLESHOOTING.md) 详细说明各种启动问题的解决方案

---

### 2. sentence-transformers 依赖冲突

**问题演变：**

#### 第一阶段：旧版本不兼容
```
ImportError: cannot import name 'cached_download' from 'huggingface_hub'
```
- 原因：`sentence-transformers==2.2.2` 太旧
- 解决：升级到新版本

#### 第二阶段：新版本需要tf-keras
```
ValueError: Keras 3 is not yet supported. Please install tf-keras.
```
- 原因：升级到5.4.1后需要350MB+的tf-keras依赖
- 解决：使用2.7.0稳定版本

**最终方案：**
✅ 固定使用 `sentence-transformers==2.7.0`
- 完全兼容新版 huggingface_hub
- 不需要 tf-keras 依赖
- 体积小，安装快速
- 功能完整

---

### 3. 缺少混合检索依赖

**问题：**
```
ModuleNotFoundError: No module named 'rank_bm25'
ModuleNotFoundError: No module named 'jieba'
```

**解决方案：**
✅ 安装了 `rank-bm25==0.2.2` 和 `jieba==0.42.1`
✅ 更新了 [requirements.txt](file://g:\rag\kret-rag\rag-scheduler\requirements.txt)

---

### 4. 网络连接超时

**问题：**
首次启动时尝试从 huggingface.co 下载嵌入模型时超时

**解决方案：**
✅ 在 [TROUBLESHOOTING.md](file://g:\rag\kret-rag\rag-scheduler\TROUBLESHOOTING.md) 中提供了三种解决方案：
1. 配置国内镜像（HF_ENDPOINT=https://hf-mirror.com）
2. 预先下载模型
3. 使用本地模型路径

---

## 📁 新增/修改的文件

### 新增文件
1. **[test_dependencies.py](file://g:\rag\kret-rag\rag-scheduler\test_dependencies.py)** - 依赖验证脚本
   - 自动检查所有必需的包是否可以正常导入
   - 显示详细的错误信息
   
2. **[TROUBLESHOOTING.md](file://g:\rag\kret-rag\rag-scheduler\TROUBLESHOOTING.md)** - 故障排查指南
   - 详细的问题描述和解决方案
   - 完整的安装步骤
   - 最佳实践建议

### 修改文件
1. **[requirements.txt](file://g:\rag\kret-rag\rag-scheduler\requirements.txt)** 
   - 将 `sentence-transformers>=2.2.2` 改为 `sentence-transformers==2.7.0`
   
2. **[start-scheduler.bat](file://g:\rag\kret-rag\start-scheduler.bat)**
   - 使用 `cd /d` 确保正确切换目录
   - 添加了更清晰的提示信息

3. **[README.md](file://g:\rag\kret-rag\README.md)**
   - 添加了网络问题配置的说明
   - 链接到故障排查指南

---

## ✅ 验证结果

运行 [test_dependencies.py](file://g:\rag\kret-rag\rag-scheduler\test_dependencies.py) 的结果：

```
📦 核心框架:
✅ FastAPI
✅ Uvicorn
✅ Pydantic

🗄️  数据库:
✅ SQLAlchemy
✅ PostgreSQL驱动

🧠 向量数据库和嵌入:
✅ ChromaDB
✅ Sentence Transformers
✅ Transformers

📄 文档处理:
✅ PyPDF
✅ python-docx
✅ OpenPyXL
✅ python-pptx
✅ BeautifulSoup

🔧 其他依赖:
✅ NumPy
✅ Redis
✅ HTTPX
✅ Rank-BM25
✅ Jieba分词
```

所有依赖项均已成功安装！✅

---

## 🚀 下一步操作

### 1. 配置环境变量
在 `.env` 文件中添加（如果还没有）：
```env
HF_ENDPOINT=https://hf-mirror.com
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

### 2. 预下载模型（可选但推荐）
```bash
cd rag-scheduler
python -c "import os; os.environ['HF_ENDPOINT']='https://hf-mirror.com'; from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### 3. 启动服务
```bash
# Windows
start-scheduler.bat

# 或手动启动
cd rag-scheduler
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 访问测试页面
- **查询测试页面**: http://localhost:8000/test-query ⭐
- API文档: http://localhost:8000/docs

---

## 📚 相关文档

- [查询测试页面使用指南](./QUERY_TEST_GUIDE.md)
- [故障排查指南](./TROUBLESHOOTING.md)
- [项目主README](../README.md)

---

## 💡 经验总结

1. **依赖版本管理很重要**
   - 不要使用 `>=` 或 `*` 这样的宽松版本约束
   - 固定经过测试的稳定版本
   - 定期更新并测试依赖

2. **跨平台兼容性**
   - Windows批处理和Linux shell脚本有差异
   - PowerShell和CMD的命令也不同
   - 使用 `cd /d` 而不是单纯的 `cd`

3. **网络问题处理**
   - 国内访问Hugging Face可能不稳定
   - 提供多种镜像源选项
   - 支持离线/本地模型

4. **文档化**
   - 详细记录常见问题和解决方案
   - 创建验证脚本自动化检查
   - 保持文档与代码同步
