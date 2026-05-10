# 🔧 404 错误修复说明

## 问题原因

访问 `http://localhost:8000/documents/upload` 返回 404 错误，是因为 **路由没有在主应用中注册**。

## 已修复内容

在 `rag-scheduler/app/main.py` 中添加了路由注册：

```python
# 注册路由
from app.routes import documents, query

app.include_router(documents.router)
app.include_router(query.router)
```

## 🚀 解决方案

### 方法一：等待自动重载（推荐）

如果你使用 `--reload` 参数启动的服务，uvicorn 会自动检测文件变化并重启：

```bash
# 服务应该会自动重启，等待几秒钟
# 查看终端输出，应该看到类似：
# INFO:     Detected file change in 'app\main.py'. Reloading...
```

### 方法二：手动重启服务

如果自动重载没有生效，请手动重启：

1. **停止当前服务**
   - 在运行 uvicorn 的终端按 `Ctrl+C`

2. **重新启动服务**
   ```bash
   cd g:\rag\kret-rag\rag-scheduler
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **或使用启动脚本**
   ```bash
   start-upload-test.bat
   ```

## ✅ 验证修复

### 1. 检查服务是否正常

访问以下地址确认服务已启动：
- 主页：http://localhost:8000/
- 健康检查：http://localhost:8000/health
- API 文档：http://localhost:8000/docs

### 2. 测试上传接口

#### 方式一：使用测试页面
1. 打开 `upload_test.html`
2. 上传一个测试文件
3. 应该能成功上传（不再返回 404）

#### 方式二：使用 curl 命令
```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@test.txt"
```

#### 方式三：使用 API 文档
1. 访问 http://localhost:8000/docs
2. 找到 `/documents/upload` 接口
3. 点击 "Try it out"
4. 选择文件并执行

### 3. 查看所有可用路由

启动服务后，应该能看到以下路由：

```
GET  /                      # 主页
GET  /health                # 健康检查
POST /documents/upload      # 上传文档 ✅
GET  /documents/{id}        # 获取文档
DELETE /documents/{id}      # 删除文档
GET  /documents/            # 列出文档
POST /query/                # 查询文档
POST /query/search          # 向量搜索
```

## 📋 完整的路由注册流程

### 项目结构
```
rag-scheduler/
├── app/
│   ├── main.py              # ← 在这里注册路由
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── documents.py     # ← 定义路由
│   │   └── query.py         # ← 定义路由
│   └── ...
```

### 注册步骤

**步骤 1**: 在路由文件中定义 router
```python
# app/routes/documents.py
from fastapi import APIRouter

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)

@router.post("/upload")
async def upload_document(...):
    ...
```

**步骤 2**: 在主应用中导入并注册
```python
# app/main.py
from app.routes import documents, query

app.include_router(documents.router)
app.include_router(query.router)
```

## ⚠️ 常见错误

### 错误 1: 忘记导入路由模块
```python
# ❌ 错误
app.include_router(documents.router)  # NameError: name 'documents' is not defined

# ✅ 正确
from app.routes import documents
app.include_router(documents.router)
```

### 错误 2: 路由前缀重复
```python
# ❌ 错误：会导致 /documents/documents/upload
router = APIRouter(prefix="/documents")
app.include_router(router, prefix="/documents")

# ✅ 正确：只在 router 或 include_router 中设置一次前缀
router = APIRouter(prefix="/documents")
app.include_router(router)
```

### 错误 3: 服务未重启
修改代码后必须重启服务才能生效（除非使用 `--reload`）

## 🔍 调试技巧

### 1. 查看所有注册的路由

在 Python 中运行：
```python
from app.main import app

for route in app.routes:
    print(f"{route.methods} {route.path}")
```

### 2. 检查路由是否正确导入

```python
from app.routes import documents
print(dir(documents))  # 应该包含 'router'
```

### 3. 查看 uvicorn 日志

启动服务时应该看到：
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

如果路由有问题，可能会看到导入错误。

## 📞 如果仍然 404

1. **确认服务已重启**
   ```bash
   # 检查进程
   Get-Process | Where-Object {$_.ProcessName -like "*uvicorn*"}
   
   # 如果没有，重新启动
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **检查端口是否正确**
   ```bash
   # 确认服务运行在 8000 端口
   netstat -ano | findstr :8000
   ```

3. **查看终端错误信息**
   - 检查是否有导入错误
   - 检查是否有语法错误

4. **清除 Python 缓存**
   ```bash
   # 删除 __pycache__ 目录
   Remove-Item -Recurse -Force app\__pycache__
   Remove-Item -Recurse -Force app\routes\__pycache__
   
   # 重启服务
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

5. **测试其他路由**
   ```bash
   # 测试主页
   curl http://localhost:8000/
   
   # 测试健康检查
   curl http://localhost:8000/health
   
   # 如果这些可以访问，说明服务正常，只是路由问题
   ```

## ✨ 总结

**问题**: 路由未注册导致 404  
**原因**: `main.py` 中没有 `include_router`  
**解决**: 添加路由注册并重启服务  
**验证**: 访问 API 文档或测试上传功能

现在重启服务后，应该可以正常访问上传接口了！🎉
