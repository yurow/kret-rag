# 🚀 快速启动指南

## ✅ 最新改进

现在你可以直接通过浏览器访问 `http://localhost:8000/` 打开上传测试页面！

---

## 📋 启动步骤

### 方法一：使用启动脚本（最简单）

```bash
cd g:\rag\kret-rag\rag-scheduler
start-upload-test.bat
```

### 方法二：手动启动

```bash
# 1. 进入目录
cd g:\rag\kret-rag\rag-scheduler

# 2. 启动服务
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🌐 访问地址

启动成功后，在浏览器中访问：

### 主要入口
- **📄 上传测试页面**: http://localhost:8000/ ⭐（推荐）

### 其他地址
- **📚 API 文档**: http://localhost:8000/docs
- **💚 健康检查**: http://localhost:8000/health
- **🔍 ReDoc 文档**: http://localhost:8000/redoc

---

## 🎯 使用流程

### 1. 启动服务
运行启动命令后，等待看到以下输出：
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 2. 打开浏览器
访问：**http://localhost:8000/**

### 3. 上传文档
- 点击虚线框或拖拽文件
- 支持格式：PDF、DOCX、PPTX、XLSX、TXT、MD
- 点击"开始上传"按钮

### 4. 查看结果
- 显示上传状态（成功/失败）
- 显示提取的字符数
- 显示文档ID

---

## 📁 项目结构

```
rag-scheduler/
├── app/
│   ├── main.py              # ← 主应用（根路径返回测试页面）
│   ├── routes/
│   │   ├── documents.py     # 文档上传接口
│   │   └── query.py         # 查询接口
│   └── services/
│       └── document_service.py  # 文档解析服务
├── uploads/                  # 上传文件存储目录
├── upload_test.html          # 测试页面
└── start-upload-test.bat     # 启动脚本
```

---

## 🔧 技术实现

### 根路径路由
```python
@app.get("/")
async def root():
    """根路径 - 返回上传测试页面"""
    return FileResponse("upload_test.html")
```

这样当你访问 `http://localhost:8000/` 时，会自动返回 [upload_test.html](file://g:\rag\kret-rag\rag-scheduler\upload_test.html) 文件。

---

## ⚠️ 注意事项

### 1. 确保服务已重启
如果修改代码后访问的还是旧页面，请重启服务：
```bash
# Ctrl+C 停止服务
# 然后重新启动
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. 清除浏览器缓存
如果页面没有更新，尝试：
- 按 `Ctrl+F5` 强制刷新
- 或使用无痕模式打开

### 3. 检查端口占用
如果 8000 端口被占用：
```bash
# 查看占用端口的进程
netstat -ano | findstr :8000

# 结束进程或使用其他端口
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

---

## 🐛 常见问题

### Q1: 访问 http://localhost:8000/ 显示 JSON 而不是页面？
**原因**: 服务未重启  
**解决**: 重启 uvicorn 服务

### Q2: 页面加载但上传失败？
**原因**: 可能是 CORS 或后端错误  
**解决**: 
1. 按 F12 打开浏览器控制台查看错误
2. 检查终端中的后端日志
3. 确认文件格式和大小符合要求

### Q3: 如何同时访问 API 文档和测试页面？
**解决**: 
- 测试页面: http://localhost:8000/
- API 文档: http://localhost:8000/docs

两个地址可以同时使用！

---

## 📖 相关文档

- [详细使用说明](UPLOAD_TEST_README.md)
- [测试文件准备指南](TEST_FILES_GUIDE.md)
- [功能实现总结](IMPLEMENTATION_SUMMARY.md)
- [404 错误修复](FIX_404_ERROR.md)

---

## ✨ 总结

**现在只需一步**：
1. 运行 `start-upload-test.bat`
2. 浏览器访问 http://localhost:8000/
3. 开始上传测试！

就这么简单！🎉
