# 文件上传处理流程说明

## 📋 概述

rag-scheduler 服务的文件上传处理采用**分步式处理流程**，确保文件先保存到本地存储，再进行文本提取和数据库入库。

## 🔄 处理流程

### 完整流程图

```
用户上传文件
    ↓
1. 验证阶段
   ├─ 验证文件大小（最大 10MB）
   ├─ 验证文件格式（PDF/DOCX/TXT/MD等）
   └─ 日志记录：格式验证通过
    ↓
2. 去重检查
   ├─ 查询数据库：文件名 + 文件大小
   ├─ 存在重复 → 返回已有文档 (is_duplicate=true)
   └─ 不存在重复 → 继续处理
    ↓
3. 文件保存 ⭐
   ├─ 生成唯一文档ID (UUID)
   ├─ 构建安全文件名: {uuid}_{原始文件名}
   ├─ 保存文件到上传目录: ./uploads/
   └─ 日志记录：文件保存成功
    ↓
4. 文本提取
   ├─ 根据文件类型选择解析器
   ├─ PDF → pypdf
   ├─ DOCX → python-docx
   ├─ PPTX → python-pptx
   ├─ XLSX → pandas/openpyxl
   ├─ TXT/MD → chardet检测编码后读取
   └─ 日志记录：文本提取完成
    ↓
5. 文本清理
   ├─ 统一换行符
   ├─ 去除页眉页脚
   ├─ 去除水印文本
   ├─ 去除乱码和特殊字符
   ├─ 去除多余空白
   └─ 日志记录：文本清理完成
    ↓
6. 数据库入库
   ├─ 创建文档元数据记录
   ├─ 保存字段：document_id, file_name, file_type, 
   │            file_size, storage_path, text_length
   ├─ 提交事务
   └─ 日志记录：元数据保存成功
    ↓
7. 返回响应
   ├─ document_id: UUID
   ├─ message: 处理结果消息
   └─ is_duplicate: false
```

## 📂 文件存储结构

### 上传目录
```
rag-scheduler/
├── uploads/                    # 文件上传目录
│   ├── {uuid}_document1.pdf
│   ├── {uuid}_document2.docx
│   └── {uuid}_document3.txt
├── data/                       # 数据库文件（SQLite）
│   └── rag_scheduler.db
└── app/
    └── services/
        └── document_service.py
```

### 文件命名规则
- **格式**: `{uuid}_{原始文件名}`
- **示例**: `550e8400-e29b-41d4-a716-446655440000_智慧出清项目概要设计.docx`
- **优点**: 
  - 避免文件名冲突
  - 保留原始文件名便于追溯
  - UUID 保证唯一性

## 📝 日志记录

### 日志级别
- **INFO**: 正常处理流程
- **WARNING**: 验证失败（文件大小、格式）
- **ERROR**: 处理异常

### 日志示例

#### 成功处理
```
INFO:app.services.document_service:开始处理文件上传: test.pdf, 大小: 1024000 bytes
INFO:app.services.document_service:文件格式验证通过: pdf
INFO:app.services.document_service:检查是否存在重复文件: test.pdf, 大小: 1024000
INFO:app.services.document_service:生成文档ID: 550e8400-e29b-41d4-a716-446655440000, 保存路径: uploads/550e8400..._test.pdf
INFO:app.services.document_service:开始保存文件到上传目录...
INFO:app.services.document_service:文件保存成功: uploads/550e8400..._test.pdf, 大小: 1024000 bytes
INFO:app.services.document_service:开始提取文本内容，文件格式: pdf
INFO:app.services.document_service:文本提取完成，原始文本长度: 15000 字符
INFO:app.services.document_service:开始清理文本内容...
INFO:app.services.document_service:文本清理完成，清理后文本长度: 14500 字符
INFO:app.services.document_service:开始保存文档元数据到数据库...
INFO:app.services.document_service:文档元数据保存成功: 550e8400-e29b-41d4-a716-446655440000
INFO:app.services.document_service:文件处理完成: 550e8400-e29b-41d4-a716-446655440000
```

#### 重复文件
```
INFO:app.services.document_service:开始处理文件上传: test.pdf, 大小: 1024000 bytes
INFO:app.services.document_service:文件格式验证通过: pdf
INFO:app.services.document_service:检查是否存在重复文件: test.pdf, 大小: 1024000
INFO:app.services.document_service:发现重复文件，直接返回已有文档: 550e8400-e29b-41d4-a716-446655440000
```

#### 处理失败
```
INFO:app.services.document_service:开始处理文件上传: corrupted.pdf, 大小: 512000 bytes
INFO:app.services.document_service:文件格式验证通过: pdf
INFO:app.services.document_service:检查是否存在重复文件: corrupted.pdf, 大小: 512000
INFO:app.services.document_service:生成文档ID: 660e8400-e29b-41d4-a716-446655440001, 保存路径: uploads/660e8400..._corrupted.pdf
INFO:app.services.document_service:开始保存文件到上传目录...
INFO:app.services.document_service:文件保存成功: uploads/660e8400..._corrupted.pdf, 大小: 512000 bytes
INFO:app.services.document_service:开始提取文本内容，文件格式: pdf
ERROR:app.services.document_service:文件处理失败: PDF extraction failed: ...
Traceback (most recent call last):
  ...
INFO:app.services.document_service:删除失败的文件: uploads/660e8400..._corrupted.pdf
```

## 🔧 关键代码位置

### 1. 文件保存
**文件**: `app/services/document_service.py`  
**方法**: `upload_document()`  
**行数**: ~96-100

```python
# 保存文件到服务器
logger.info("开始保存文件到上传目录...")
contents = await file.read()
with open(file_path, "wb") as f:
    f.write(contents)
logger.info(f"文件保存成功: {file_path}, 大小: {len(contents)} bytes")
```

### 2. 文本提取
**文件**: `app/services/document_service.py`  
**方法**: `extract_text()`  
**行数**: ~130-145

```python
# 提取文本内容
logger.info(f"开始提取文本内容，文件格式: {file_extension}")
extracted_text = await self.extract_text(str(file_path), file_extension)
logger.info(f"文本提取完成，原始文本长度: {len(extracted_text)} 字符")
```

### 3. 文本清理
**文件**: `app/services/document_service.py`  
**方法**: `clean_text()`  
**行数**: ~148-151

```python
# 清理文本
logger.info("开始清理文本内容...")
cleaned_text = self.clean_text(extracted_text)
logger.info(f"文本清理完成，清理后文本长度: {len(cleaned_text)} 字符")
```

## 🎯 设计优势

### 1. 分步处理
- ✅ 文件先保存到本地，确保数据安全
- ✅ 文本提取失败时可清理临时文件
- ✅ 每个步骤独立，便于调试和维护

### 2. 详细日志
- ✅ 跟踪文件处理的每个环节
- ✅ 快速定位问题所在
- ✅ 便于性能分析和优化

### 3. 错误处理
- ✅ 失败时自动回滚数据库事务
- ✅ 失败时自动删除已上传的文件
- ✅ 完整的异常堆栈记录

### 4. 去重优化
- ✅ 在文件保存前检查重复
- ✅ 避免不必要的文件IO和文本处理
- ✅ 提升系统整体性能

## 📊 性能指标

### 典型处理时间（1MB PDF文件）
- 文件保存: ~10-50ms
- 文本提取: ~100-500ms
- 文本清理: ~10-50ms
- 数据库入库: ~5-20ms
- **总计**: ~125-620ms

### 去重场景
- 数据库查询: ~5-10ms
- **节省时间**: ~120-610ms（跳过后续处理）

## 🔍 故障排查

### 问题1：文件保存失败
**症状**: 日志显示 "文件保存成功" 但文件不存在  
**原因**: 磁盘空间不足或权限问题  
**解决**: 
```bash
# 检查磁盘空间
df -h

# 检查目录权限
ls -la uploads/
chmod 755 uploads/
```

### 问题2：文本提取失败
**症状**: 日志显示 "文本提取完成" 但长度为0  
**原因**: 文件损坏或格式不支持  
**解决**: 
- 检查文件是否可正常打开
- 查看 ERROR 日志中的详细异常信息
- 尝试手动转换文件格式

### 问题3：数据库入库失败
**症状**: 日志显示 "文档元数据保存成功" 但查询不到  
**原因**: 事务未提交或回滚  
**解决**: 
- 检查是否有未捕获的异常
- 查看数据库连接配置
- 检查数据库文件权限

## 🚀 启动服务并测试

```bash
# 启动服务（带日志输出）
cd rag-scheduler
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 查看实时日志
tail -f logs/app.log  # 如果配置了文件日志

# 测试上传
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@test.pdf" \
  -v
```

## 📚 相关文档

- [DUPLICATE_DETECTION.md](DUPLICATE_DETECTION.md) - 文件去重功能
- [BUGFIX_DATETIME_VALIDATION.md](BUGFIX_DATETIME_VALIDATION.md) - 时间字段验证修复
- [README.md](README.md) - 项目说明
