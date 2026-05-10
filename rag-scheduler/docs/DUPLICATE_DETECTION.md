# 文件上传去重功能说明

## 功能概述

rag-scheduler 服务现已实现基于**文件名 + 文件大小**的简易去重机制，避免重复处理相同的文件。

## 去重逻辑

### 判断标准
- **文件名**：原始文件名（不含路径）
- **文件大小**：文件字节数

当用户上传文件时，系统会检查数据库中是否存在**同名且同大小**的文件记录：
- ✅ **存在** → 直接返回已有文档信息，跳过解析、切片、入库流程
- ❌ **不存在** → 正常执行完整的文档处理流程

### 工作流程

```
用户上传文件
    ↓
验证文件格式和大小
    ↓
查询数据库（file_name + file_size）
    ↓
    ├─ 存在重复 → 返回已有文档 (is_duplicate=true)
    └─ 不存在 → 解析文本 → 清理文本 → 保存到数据库 → 返回新文档 (is_duplicate=false)
```

## API 响应变化

### UploadResponse 新增字段

```json
{
  "document_id": "uuid-string",
  "message": "Document already exists. No need to reprocess. Extracted 1234 characters.",
  "is_duplicate": true
}
```

**字段说明：**
- `is_duplicate`: 
  - `true` - 文件已存在，未重复处理
  - `false` - 新文件，已完成处理

### 响应消息示例

#### 新文件上传
```json
{
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Document uploaded and processed successfully. Extracted 5678 characters.",
  "is_duplicate": false
}
```

#### 重复文件上传
```json
{
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Document already exists. No need to reprocess. Extracted 5678 characters.",
  "is_duplicate": true
}
```

## 代码实现位置

### 1. Repository 层
**文件**: `app/repositories/document_repository.py`

新增方法：
```python
def find_duplicate(self, file_name: str, file_size: int) -> Optional[DocumentMetadata]:
    """根据文件名和文件大小查找重复文档"""
    return self.db.query(DocumentMetadata).filter(
        DocumentMetadata.file_name == file_name,
        DocumentMetadata.file_size == file_size
    ).first()
```

### 2. Service 层
**文件**: `app/services/document_service.py`

修改 `upload_document` 方法，在文件验证后立即检查重复：
```python
# 检查是否存在重复文件（同名 + 同大小）
existing_doc = repo.find_duplicate(file.filename, file.size)
if existing_doc:
    # 文件已存在，直接返回已有文档信息
    doc_response = DocumentResponse(...)
    return DocumentUploadResult(
        document_response=doc_response,
        is_duplicate=True
    )
```

### 3. Schema 层
**文件**: `app/models/schemas.py`

新增模型：
```python
class DocumentUploadResult(BaseModel):
    """文档上传结果（内部使用）"""
    document_response: DocumentResponse
    is_duplicate: bool = False
```

修改响应模型：
```python
class UploadResponse(BaseModel):
    """上传响应"""
    document_id: str
    message: str
    is_duplicate: bool = Field(default=False, description="是否为重复文件")
```

### 4. Route 层
**文件**: `app/routes/documents.py`

根据 `is_duplicate` 返回不同消息：
```python
if result.is_duplicate:
    message = f"Document already exists. No need to reprocess..."
else:
    message = f"Document uploaded and processed successfully..."
```

## 测试方法

### 使用测试脚本

项目提供了测试脚本 `test_duplicate_upload.py`：

```bash
cd rag-scheduler
python test_duplicate_upload.py
```

### 手动测试

1. 启动 rag-scheduler 服务：
   ```bash
   cd rag-scheduler
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. 第一次上传文件：
   ```bash
   curl -X POST "http://localhost:8000/documents/upload" \
     -F "file=@test.pdf"
   ```

3. 第二次上传相同文件：
   ```bash
   curl -X POST "http://localhost:8000/documents/upload" \
     -F "file=@test.pdf"
   ```

4. 观察响应中的 `is_duplicate` 字段和 `message` 内容

## 优势

1. **性能优化**：避免重复的文本提取、清理、分块和向量入库操作
2. **存储节省**：不会重复存储相同内容的文件
3. **用户体验**：快速响应，明确告知用户文件已存在
4. **数据一致性**：确保相同文件始终指向同一个文档ID

## 注意事项

### 当前限制

1. **仅基于文件名和大小**：
   - 如果两个不同内容的文件恰好同名同大小，会被误判为重复
   - 如果同一文件改名后上传，会被视为新文件

2. **不适用于动态内容**：
   - 对于经常变化的文件（如日志文件），可能需要更复杂的去重策略

### 未来优化方向

1. **基于内容哈希**：
   - 计算文件的 MD5/SHA256 哈希值
   - 更准确地识别相同内容的文件
   - 不受文件名影响

2. **混合策略**：
   - 先检查文件名+大小（快速）
   - 再检查内容哈希（精确）
   - 平衡性能和准确性

3. **可配置的去重策略**：
   - 允许用户选择去重级别
   - 支持关闭去重功能

## 相关文档

- [API_EXAMPLES.md](../API_EXAMPLES.md) - API 使用示例
- [README.md](README.md) - 项目说明
- [QUICKSTART.md](../QUICKSTART.md) - 快速开始指南
