# 文件去重功能 - 快速参考

## 🎯 核心概念

**去重策略**：文件名 + 文件大小（字节）完全匹配

## 📍 关键代码位置

| 层级 | 文件 | 方法/类 | 说明 |
|------|------|---------|------|
| Repository | `app/repositories/document_repository.py` | `find_duplicate()` | 查询重复文档 |
| Service | `app/services/document_service.py` | `upload_document()` | 去重检查逻辑 |
| Schema | `app/models/schemas.py` | `DocumentUploadResult` | 返回结果模型 |
| Route | `app/routes/documents.py` | `upload_document()` | API 响应处理 |

## 🔍 去重流程

```python
# 1. 验证文件格式和大小
# 2. 查询数据库
existing_doc = repo.find_duplicate(file.filename, file.size)

# 3. 判断是否重复
if existing_doc:
    return DocumentUploadResult(doc_response, is_duplicate=True)
else:
    # 正常处理流程
    return DocumentUploadResult(doc_response, is_duplicate=False)
```

## 📡 API 响应

### 请求
```bash
POST /documents/upload
Content-Type: multipart/form-data

file: <binary>
metadata: {"key": "value"} (可选)
```

### 响应 - 新文件
```json
{
  "document_id": "uuid",
  "message": "Document uploaded and processed successfully. Extracted 1234 characters.",
  "is_duplicate": false
}
```

### 响应 - 重复文件
```json
{
  "document_id": "uuid",
  "message": "Document already exists. No need to reprocess. Extracted 1234 characters.",
  "is_duplicate": true
}
```

## 🧪 测试命令

```bash
# 启动服务
cd rag-scheduler
uvicorn app.main:app --reload

# 运行测试脚本
python test_duplicate_upload.py

# 手动测试
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@test.pdf"
```

## ⚡ 性能优势

- **避免重复解析**：跳过 PDF/DOCX 等格式的文件解析
- **避免重复分块**：跳过文本清理和分块操作
- **避免重复入库**：跳过向量数据库写入
- **快速响应**：仅需一次数据库查询（< 10ms）

## 🔮 未来优化

1. **内容哈希去重**：使用 MD5/SHA256 替代文件名+大小
2. **异步检查**：将去重检查放入后台任务
3. **缓存层**：使用 Redis 缓存常见文件的哈希值
4. **批量去重**：支持批量上传时的去重检测

## 📚 相关文档

- [DUPLICATE_DETECTION.md](DUPLICATE_DETECTION.md) - 详细说明
- [IMPLEMENTATION_SUMMARY_DUPLICATE.md](IMPLEMENTATION_SUMMARY_DUPLICATE.md) - 实现总结
- [README.md](README.md) - 项目说明
