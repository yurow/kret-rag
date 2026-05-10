# RAG Scheduler 启动检查清单

## ✅ 启动前检查

### 1. 环境检查
- [ ] Python版本 >= 3.10
  ```bash
  python --version
  ```

- [ ] 当前目录在 rag-scheduler 下
  ```bash
  cd g:\rag\kret-rag\rag-scheduler
  pwd  # 应该显示: g:\rag\kret-rag\rag-scheduler
  ```

### 2. 依赖检查
- [ ] 运行依赖验证脚本
  ```bash
  python test_dependencies.py
  ```
  
  预期输出：所有项目显示为 ✅

- [ ] 如果看到 ❌，安装缺失的包
  ```bash
  pip install -r requirements.txt
  ```

### 3. 配置文件检查
- [ ] `.env` 文件存在
  ```bash
  dir .env  # Windows
  ls .env   # Linux/Mac
  ```

- [ ] 如果不存在，复制示例文件
  ```bash
  cp .env.example .env
  ```

- [ ] 配置关键参数
  ```env
  # 数据库连接
  DATABASE_URL=postgresql://user:password@localhost:5432/rag_db
  
  # 向量模型
  EMBEDDING_MODEL=all-MiniLM-L6-v2
  
  # Hugging Face镜像（解决网络问题）
  HF_ENDPOINT=https://hf-mirror.com
  ```

### 4. 服务依赖检查
- [ ] PostgreSQL 正在运行
  ```bash
  # Windows
  Get-Service postgresql*
  
  # Linux
  systemctl status postgresql
  ```

- [ ] Redis 正在运行（如果使用）
  ```bash
  redis-cli ping  # 应该返回 PONG
  ```

---

## 🚀 启动步骤

### 方式1：使用启动脚本（推荐）⭐
```bash
start-scheduler.bat
```

**预期输出：**
```
========================================
 Starting KRET-RAG Scheduler
========================================

Current directory: G:\rag\kret-rag\rag-scheduler

Starting RAG Scheduler on port 8000...

📚 API Documentation: http://localhost:8000/docs
📤 Upload Test Page: http://localhost:8000/
🔍 Query Test Page: http://localhost:8000/test-query

INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
============================================================
开始执行数据库迁移
============================================================
✅ [Migration XXX] ...
============================================================
✅ 所有迁移完成！
============================================================
INFO:     Application startup complete.
```

### 方式2：手动启动
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🔍 启动后验证

### 1. 检查服务是否运行
```bash
# 浏览器访问
http://localhost:8000/docs

# 或使用curl
curl http://localhost:8000/health
```

### 2. 测试API端点
- [ ] 访问 API文档: http://localhost:8000/docs
- [ ] 访问上传页面: http://localhost:8000/
- [ ] 访问查询测试页: http://localhost:8000/test-query

### 3. 查看日志
确认没有以下错误：
- ❌ `ModuleNotFoundError`
- ❌ `ImportError`
- ❌ `Connection refused`
- ❌ `TimeoutError`

应该看到：
- ✅ `Application startup complete`
- ✅ `Uvicorn running on http://0.0.0.0:8000`

---

## ⚠️ 常见问题快速修复

### 问题1: ModuleNotFoundError: No module named 'app'
**解决：**
```bash
# 确保在正确的目录
cd g:\rag\kret-rag\rag-scheduler

# 或者使用启动脚本
start-scheduler.bat
```

### 问题2: ImportError: cannot import name 'cached_download'
**解决：**
```bash
pip install sentence-transformers==2.7.0
```

### 问题3: Connection timeout to huggingface.co
**解决：**
在 `.env` 文件中添加：
```env
HF_ENDPOINT=https://hf-mirror.com
```

然后重启服务。

### 问题4: Database connection failed
**解决：**
1. 检查PostgreSQL是否运行
2. 验证 `.env` 中的 `DATABASE_URL` 是否正确
3. 确保数据库已创建

```bash
# 创建数据库（如果需要）
psql -U postgres -c "CREATE DATABASE rag_db;"
```

### 问题5: Port 8000 already in use
**解决：**
```bash
# 查找占用端口的进程
netstat -ano | findstr :8000  # Windows
lsof -i :8000                  # Linux/Mac

# 终止进程
taskkill /PID <PID> /F         # Windows
kill -9 <PID>                  # Linux/Mac

# 或使用其他端口
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

---

## 📊 性能优化建议

### 1. 首次启动预加载模型
避免首次查询时的延迟：
```python
# 在启动时预加载
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
```

### 2. 启用GPU加速（如果有）
```env
# .env
USE_GPU=true
DEVICE=cuda
```

### 3. 调整批处理大小
```env
BATCH_SIZE=32  # 根据内存调整
```

### 4. 启用缓存
```env
REDIS_URL=redis://localhost:6379
ENABLE_CACHE=true
```

---

## 🎯 成功标志

当你看到以下内容时，说明启动成功：

1. ✅ 控制台显示 `Application startup complete`
2. ✅ 可以访问 http://localhost:8000/docs
3. ✅ 查询测试页面正常加载
4. ✅ 能够成功执行一次查询

---

## 📞 需要帮助？

如果遇到问题：

1. 查看 [故障排查指南](./TROUBLESHOOTING.md)
2. 检查 [问题修复总结](./FIX_SUMMARY.md)
3. 查看详细日志：
   ```bash
   uvicorn app.main:app --log-level debug
   ```
4. 提交Issue时提供：
   - 完整的错误信息
   - Python版本
   - 操作系统
   - `pip list` 输出

---

**祝使用愉快！** 🎉
