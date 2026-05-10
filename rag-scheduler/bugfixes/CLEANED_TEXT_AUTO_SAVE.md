# 清洗后文本自动保存功能

## 📋 功能概述

rag-scheduler 服务现已实现**自动将清洗后的文本保存到 `uploads_text/` 目录**，文件命名与原文档 UUID 对应。

## 🎯 核心特性

### 1. 自动保存
- ✅ 文本清理完成后自动保存
- ✅ 保存到 `./uploads_text/` 目录
- ✅ 文件名格式：`{document_id}.txt`
- ✅ 使用 UTF-8 编码

### 2. 文件命名规则
```
原始文件: 智慧出清项目概要设计_202512_v1.0.docx
文档UUID: 550e8400-e29b-41d4-a716-446655440000
文本文件: uploads_text/550e8400-e29b-41d4-a716-446655440000.txt
```

### 3. 数据库记录
在 `document_metadata` 表中新增字段：
- `text_file_path`: 存储清洗后文本文件的完整路径

## 🔄 处理流程

```
用户上传文件
    ↓
验证文件格式和大小
    ↓
检查是否重复
    ↓
保存原始文件到 uploads/
    ↓
提取文本内容
    ↓
清理文本（去页眉页脚、水印、乱码等）
    ↓
⭐ 保存清洗后文本到 uploads_text/{uuid}.txt
    ↓
保存元数据到数据库（包含 text_file_path）
    ↓
返回响应
```

## 📂 目录结构

```
rag-scheduler/
├── uploads/                    # 原始文件目录
│   ├── 550e8400-..._test.pdf
│   ├── 660e8400-..._doc.docx
│   └── ...
├── uploads_text/               # 清洗后文本目录 ⭐ 新增
│   ├── 550e8400-e29b-41d4-a716-446655440000.txt
│   ├── 660e8400-e29b-41d4-a716-446655440001.txt
│   └── ...
├── data/
│   └── rag_scheduler.db
└── app/
    ├── models/
    │   └── db_models.py        # 新增 text_file_path 字段
    ├── repositories/
    │   └── document_repository.py  # 更新 create 方法
    └── services/
        └── document_service.py     # 新增 save_cleaned_text 方法
```

## 💻 代码实现

### 1. 初始化文本目录
**文件**: `app/services/document_service.py`

```python
class DocumentService:
    def __init__(self):
        """初始化文档服务，创建上传目录和数据库表"""
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建清洗后文本存储目录
        self.text_upload_dir = Path("./uploads_text")
        self.text_upload_dir.mkdir(parents=True, exist_ok=True)
        
        # ... 其他初始化代码
```

### 2. 保存文本方法
**文件**: `app/services/document_service.py`

```python
def save_cleaned_text(self, document_id: str, cleaned_text: str) -> str:
    """
    保存清洗后的文本到 uploads_text 目录
    
    Args:
        document_id: 文档UUID
        cleaned_text: 清洗后的文本内容
        
    Returns:
        str: 保存的文本文件路径
    """
    # 使用 UUID 作为文件名，扩展名为 .txt
    text_filename = f"{document_id}.txt"
    text_filepath = self.text_upload_dir / text_filename
    
    try:
        # 以 UTF-8 编码保存文本
        with open(text_filepath, 'w', encoding='utf-8') as f:
            f.write(cleaned_text)
        
        logger.info(f"清洗后的文本已保存: {text_filepath}")
        return str(text_filepath)
        
    except Exception as e:
        logger.error(f"保存清洗后文本失败: {str(e)}", exc_info=True)
        raise Exception(f"Failed to save cleaned text: {str(e)}")
```

### 3. 调用保存方法
**文件**: `app/services/document_service.py` - `upload_document()` 方法

```python
# 清理文本（去除页眉页脚、水印、乱码、空白等）
logger.info("开始清理文本内容...")
cleaned_text = self.clean_text(extracted_text)
logger.info(f"文本清理完成，清理后文本长度: {len(cleaned_text)} 字符")

# 保存清洗后的文本到 uploads_text 目录
logger.info("开始保存清洗后的文本文件...")
text_file_path = self.save_cleaned_text(document_id, cleaned_text)
logger.info(f"清洗后文本保存成功: {text_file_path}")

# 保存到数据库
logger.info("开始保存文档元数据到数据库...")
doc_metadata = repo.create(
    document_id=document_id,
    file_name=file.filename,
    file_type=file_extension,
    file_size=len(contents),
    storage_path=str(file_path),
    text_length=len(cleaned_text),
    text_file_path=text_file_path,  # ⭐ 传入文本文件路径
    metadata={
        **(metadata or {}),
        "text_length": len(cleaned_text)
    }
)
```

### 4. 数据库模型更新
**文件**: `app/models/db_models.py`

```python
class DocumentMetadata(db_manager.Base):
    """文档元数据表"""
    
    __tablename__ = "document_metadata"
    
    # ... 其他字段
    
    # 文件信息
    file_size = Column(Integer, nullable=False, comment="文件大小（字节）")
    text_length = Column(Integer, nullable=True, comment="提取的文本长度")
    storage_path = Column(String(1000), nullable=False, comment="原始文件存储路径")
    text_file_path = Column(String(1000), nullable=True, comment="清洗后文本文件路径")  # ⭐ 新增
    
    # ... 其他字段
```

### 5. Repository 层更新
**文件**: `app/repositories/document_repository.py`

```python
def create(self, document_id: str, file_name: str, file_type: str, 
           file_size: int, storage_path: str, text_length: int = None,
           text_file_path: str = None, metadata: Dict[str, Any] = None) -> DocumentMetadata:
    """
    创建文档元数据记录
    
    Args:
        ...
        text_file_path: 清洗后文本文件路径  # ⭐ 新增参数
        ...
    """
    doc_metadata = DocumentMetadata(
        document_id=document_id,
        file_name=file_name,
        file_type=file_type,
        file_size=file_size,
        text_length=text_length,
        storage_path=storage_path,
        text_file_path=text_file_path,  # ⭐ 设置文本文件路径
        extra_metadata=metadata or {},
        status="completed"
    )
    
    # ... 保存逻辑
```

## 📝 日志示例

### 成功保存
```
INFO:app.services.document_service:开始清理文本内容...
INFO:app.services.document_service:文本清理完成，清理后文本长度: 14500 字符
INFO:app.services.document_service:开始保存清洗后的文本文件...
INFO:app.services.document_service:清洗后的文本已保存: uploads_text/550e8400-e29b-41d4-a716-446655440000.txt
INFO:app.services.document_service:清洗后文本保存成功: uploads_text/550e8400-e29b-41d4-a716-446655440000.txt
INFO:app.services.document_service:开始保存文档元数据到数据库...
INFO:app.services.document_service:文档元数据保存成功: 550e8400-e29b-41d4-a716-446655440000
```

### 保存失败
```
INFO:app.services.document_service:开始保存清洗后的文本文件...
ERROR:app.services.document_service:保存清洗后文本失败: Permission denied
Traceback (most recent call last):
  ...
```

## 🧪 测试方法

### 1. 启动服务
```bash
cd rag-scheduler
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. 上传文件
```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@test.pdf" \
  -v
```

### 3. 验证结果

#### 检查文件是否存在
```bash
# 查看 uploads_text 目录
ls -la uploads_text/

# 查看特定文件
cat uploads_text/550e8400-e29b-41d4-a716-446655440000.txt
```

#### 查询数据库
```bash
# 使用 SQLite 命令行
sqlite3 data/rag_scheduler.db

# 查询文档记录
SELECT document_id, file_name, text_file_path FROM document_metadata;
```

预期输出：
```
document_id                             | file_name    | text_file_path
----------------------------------------|--------------|-------------------------------------------
550e8400-e29b-41d4-a716-446655440000   | test.pdf     | uploads_text/550e8400-...-446655440000.txt
```

## 💡 优势

### 1. 便于调试
- ✅ 可以直接查看清洗后的文本内容
- ✅ 方便对比原始文本和清洗后文本
- ✅ 快速定位文本清理问题

### 2. 性能优化
- ✅ 避免重复文本提取和清理
- ✅ 可直接读取文本文件进行向量化
- ✅ 支持离线批量处理

### 3. 数据追溯
- ✅ 保留完整的处理链路
- ✅ 原始文件和清洗后文本一一对应
- ✅ 便于审计和问题排查

### 4. 灵活应用
- ✅ 可用于文本质量分析
- ✅ 支持手动修正清洗结果
- ✅ 便于构建训练数据集

## 🔍 常见问题

### Q1: 文本文件编码是什么？
**A**: 使用 UTF-8 编码保存，支持中英文混合内容。

### Q2: 如果保存失败会怎样？
**A**: 会抛出异常，整个上传流程失败，已上传的文件会被删除，数据库事务会回滚。

### Q3: 可以自定义文本文件名吗？
**A**: 当前使用 UUID 作为文件名以保证唯一性。如需自定义，可修改 `save_cleaned_text` 方法。

### Q4: 旧数据如何处理？
**A**: 对于已有的文档记录，`text_file_path` 字段为 `NULL`。可以重新上传或编写脚本批量生成文本文件。

### Q5: 文本文件会占用很多空间吗？
**A**: 文本文件通常比原始文件小很多（尤其是 PDF、DOCX 等格式）。例如：
- 10MB PDF → ~100KB 文本
- 5MB DOCX → ~50KB 文本

## 🚀 后续优化建议

1. **压缩存储**：对大文本文件使用 gzip 压缩
2. **分块存储**：将大文本按章节分块存储
3. **版本管理**：保留多次清洗结果的版本历史
4. **异步保存**：将文本保存改为后台任务，提升响应速度
5. **对象存储**：集成 MinIO/S3 存储大规模文本文件

## 📚 相关文档

- [FILE_PROCESSING_FLOW.md](FILE_PROCESSING_FLOW.md) - 文件处理流程说明
- [DUPLICATE_DETECTION.md](DUPLICATE_DETECTION.md) - 文件去重功能
- [README.md](README.md) - 项目说明
