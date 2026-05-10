# 🗄️ 数据库存储功能实现总结

## ✅ 已完成的功能

### 1. SQLite 数据库集成
- ✅ 自动创建数据库文件和表结构
- ✅ 支持文档元数据存储
- ✅ 完整的 CRUD 操作
- ✅ 分页查询和搜索功能

### 2. 可扩展架构设计
- ✅ **Repository Pattern（仓储模式）** - 解耦业务逻辑和数据访问
- ✅ **DatabaseManager** - 统一管理数据库连接
- ✅ 支持 SQLite（默认）和 PostgreSQL
- ✅ 易于扩展到 MySQL、Oracle 等其他数据库

### 3. 数据模型
创建了 `document_metadata` 表，包含以下字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 自增主键 |
| document_id | VARCHAR(100) | 文档UUID（唯一索引） |
| file_name | VARCHAR(500) | 原始文件名 |
| file_type | VARCHAR(50) | 文件类型扩展名 |
| file_size | INTEGER | 文件大小（字节） |
| text_length | INTEGER | 提取的文本长度 |
| storage_path | VARCHAR(1000) | 文件存储路径 |
| created_at | DATETIME | 上传时间 |
| updated_at | DATETIME | 更新时间 |
| status | VARCHAR(20) | 处理状态 |
| metadata | JSON | 额外元数据 |

### 4. API 接口增强

#### 新增接口
- `GET /documents/search?keyword=xxx` - 搜索文档
- `GET /documents/?file_type=pdf&status=completed` - 过滤查询

#### 改进接口
- `POST /documents/upload` - 自动保存元数据到数据库
- `GET /documents/{id}` - 从数据库查询文档信息
- `DELETE /documents/{id}` - 同时删除文件和数据库记录
- `GET /documents/` - 支持分页和过滤

---

## 📁 项目文件结构

```
rag-scheduler/
├── app/
│   ├── core/
│   │   └── config.py                  # ✏️ 已更新：添加数据库配置
│   ├── db/
│   │   └── database.py                # ✏️ 已重写：支持多数据库
│   ├── models/
│   │   └── db_models.py               # 🆕 新建：数据库模型
│   ├── repositories/
│   │   └── document_repository.py     # 🆕 新建：文档仓储层
│   ├── services/
│   │   └── document_service.py        # ✏️ 已重写：集成数据库
│   └── routes/
│       └── documents.py               # ✏️ 已更新：添加搜索接口
├── data/
│   └── documents.db                   # 🆕 自动生成：SQLite数据库
├── uploads/                           # 文件存储目录
├── .env.example                       # 🆕 新建：环境变量模板
├── test_database.py                   # 🆕 新建：数据库测试脚本
└── DATABASE_GUIDE.md                  # 🆕 新建：数据库配置指南
```

---

## 🚀 快速开始

### 1. 启动服务

```bash
cd g:\rag\kret-rag\rag-scheduler
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

服务会自动：
- ✅ 创建 `./data` 目录
- ✅ 初始化 `documents.db` 数据库
- ✅ 创建 `document_metadata` 表

### 2. 测试上传

访问 http://localhost:8000/ 上传文档，元数据会自动保存到数据库。

### 3. 查询文档

```bash
# 列出所有文档
curl http://localhost:8000/documents/

# 按类型过滤
curl "http://localhost:8000/documents/?file_type=pdf"

# 搜索文档
curl "http://localhost:8000/documents/search?keyword=测试"

# 获取单个文档
curl http://localhost:8000/documents/{document_id}
```

---

## 🧪 测试结果

运行数据库测试脚本：

```bash
python test_database.py
```

**结果**: ✅ 7/7 测试全部通过

```
✅ 数据库初始化
✅ 创建文档记录
✅ 查询文档
✅ 列出所有文档
✅ 搜索文档
✅ 更新文档
✅ 删除文档
```

---

## 🔧 技术实现细节

### 1. Repository Pattern

```python
# 业务层不直接操作数据库
class DocumentService:
    async def upload_document(self, file, metadata):
        # ... 处理文档 ...
        
        repo = DocumentRepository(db_session)
        doc = repo.create(...)  # ← 通过仓储层操作
        
        return response
```

**优势**:
- 解耦业务逻辑和数据访问
- 易于单元测试（可以 mock Repository）
- 统一的数据访问接口
- 方便切换数据库

### 2. 数据库管理器

```python
class DatabaseManager:
    def _initialize_database(self):
        db_type = settings.DATABASE_TYPE
        
        if db_type == "sqlite":
            self._setup_sqlite()
        elif db_type == "postgresql":
            self._setup_postgresql()
        # 可以轻松添加其他数据库
```

### 3. 事务管理

```python
db_session = db_manager.SessionLocal()
try:
    # 执行数据库操作
    repo.create(...)
    db_session.commit()  # 提交事务
except Exception as e:
    db_session.rollback()  # 回滚事务
    raise e
finally:
    db_session.close()  # 关闭会话
```

---

## 📊 API 使用示例

### 上传文档

```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@test.pdf" \
  -F 'metadata={"author":"张三","category":"技术"}'
```

**响应**:
```json
{
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Document uploaded and processed successfully. Extracted 1234 characters."
}
```

### 查询文档列表

```bash
# 基本查询
curl "http://localhost:8000/documents/?page=1&page_size=10"

# 按类型过滤
curl "http://localhost:8000/documents/?file_type=pdf"

# 按状态过滤
curl "http://localhost:8000/documents/?status=completed"

# 组合过滤
curl "http://localhost:8000/documents/?file_type=pdf&status=completed&page=1&page_size=5"
```

**响应**:
```json
[
  {
    "document_id": "550e8400-...",
    "file_name": "test.pdf",
    "status": "completed",
    "created_at": "2026-05-09T18:15:09",
    "updated_at": null,
    "metadata": {
      "author": "张三",
      "category": "技术",
      "text_length": 1234
    }
  }
]
```

### 搜索文档

```bash
curl "http://localhost:8000/documents/search?keyword=测试&page=1&page_size=10"
```

**响应**: 返回文件名包含"测试"的文档列表

### 获取单个文档

```bash
curl http://localhost:8000/documents/550e8400-e29b-41d4-a716-446655440000
```

### 删除文档

```bash
curl -X DELETE http://localhost:8000/documents/550e8400-e29b-41d4-a716-446655440000
```

**效果**: 
- ✅ 删除数据库记录
- ✅ 删除物理文件

---

## 🔄 切换到 PostgreSQL

### 1. 安装 PostgreSQL

```bash
# Windows: 下载安装包
# https://www.postgresql.org/download/windows/

# Linux
sudo apt-get install postgresql

# macOS
brew install postgresql
```

### 2. 创建数据库

```bash
psql -U postgres
CREATE DATABASE rag_db;
CREATE USER rag_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE rag_db TO rag_user;
```

### 3. 修改配置

编辑 `.env` 文件：

```bash
DATABASE_TYPE=postgresql
DATABASE_URL=postgresql://rag_user:your_password@localhost:5432/rag_db
```

### 4. 安装依赖

```bash
pip install psycopg2-binary
```

### 5. 重启服务

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

服务会自动创建表结构，无需手动迁移！

---

## 💡 扩展到其他数据库

### 添加 MySQL 支持

#### 步骤 1: 在 DatabaseManager 中添加方法

```python
def _setup_mysql(self):
    """配置 MySQL"""
    from sqlalchemy import pool
    
    database_url = settings.DATABASE_URL
    
    self.engine = create_engine(
        database_url,
        poolclass=pool.QueuePool,
        pool_size=10,
        max_overflow=20,
        pool_recycle=1800,
        echo=settings.DEBUG
    )
    
    self.SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=self.engine
    )
```

#### 步骤 2: 添加分支

```python
def _initialize_database(self):
    db_type = settings.DATABASE_TYPE.lower()
    
    if db_type == "sqlite":
        self._setup_sqlite()
    elif db_type == "postgresql":
        self._setup_postgresql()
    elif db_type == "mysql":
        self._setup_mysql()  # 新增
    else:
        raise ValueError(f"Unsupported database type: {db_type}")
```

#### 步骤 3: 配置

```bash
# .env
DATABASE_TYPE=mysql
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/rag_db
```

#### 步骤 4: 安装驱动

```bash
pip install pymysql
```

**就这么简单！** 业务代码完全不需要修改。

---

## ⚠️ 注意事项

### 1. 数据库文件位置

SQLite 数据库文件位于：
```
g:\rag\kret-rag\rag-scheduler\data\documents.db
```

不要手动删除或修改此文件。

### 2. 事务管理

所有写操作都在事务中执行，确保数据一致性：
- 成功 → commit
- 失败 → rollback

### 3. 会话关闭

每次数据库操作后都会关闭会话，避免连接泄漏。

### 4. 索引优化

已为常用查询字段创建索引：
- `document_id` - 加速单条查询
- `file_type` - 加速类型过滤
- `created_at` - 加速时间排序
- `status` - 加速状态过滤

### 5. JSON 字段

`metadata` 字段使用 JSON 类型（SQLite 3.38+ 支持），可以存储任意结构的元数据。

---

## 📈 性能优化建议

### 1. 连接池（PostgreSQL）

已在 DatabaseManager 中配置：
```python
pool_size=10           # 基础连接数
max_overflow=20        # 最大溢出连接数
pool_recycle=1800      # 30分钟回收连接
pool_pre_ping=True     # 使用前检查连接
```

### 2. 批量操作（未来实现）

```python
def batch_create(self, documents: List[Dict]):
    """批量插入文档"""
    self.db.bulk_insert_mappings(DocumentMetadata, documents)
    self.db.commit()
```

### 3. 缓存层（未来实现）

```python
# 在 Repository 前添加缓存层
class CachedDocumentRepository:
    def __init__(self, repo, cache):
        self.repo = repo
        self.cache = cache
    
    def get_by_id(self, document_id):
        # 先查缓存
        cached = self.cache.get(document_id)
        if cached:
            return cached
        
        # 缓存未命中，查数据库
        doc = self.repo.get_by_id(document_id)
        self.cache.set(document_id, doc, ttl=300)
        return doc
```

---

## 📖 相关文档

- [DATABASE_GUIDE.md](DATABASE_GUIDE.md) - 详细的数据库配置和扩展指南
- [test_database.py](test_database.py) - 数据库功能测试脚本
- [.env.example](.env.example) - 环境变量配置模板

---

## ✨ 总结

✅ **已完成**:
- SQLite 数据库集成
- 完整的文档元数据存储
- Repository Pattern 架构
- 可扩展的数据库设计
- 7/7 测试全部通过

🎯 **特性**:
- 自动初始化数据库
- 支持 CRUD 操作
- 分页和搜索功能
- 事务管理
- 索引优化

🚀 **可扩展**:
- 轻松切换到 PostgreSQL
- 可添加 MySQL、Oracle 等
- 业务代码无需修改
- 支持连接池和缓存

**现在上传的文档元数据会自动保存到 SQLite 数据库，并支持完整的查询和管理功能！** 🎉
