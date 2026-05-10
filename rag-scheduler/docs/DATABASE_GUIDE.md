# 🗄️ 数据库配置与扩展指南

## 📋 概述

KRET-RAG 系统使用 **Repository Pattern（仓储模式）** 实现数据访问层，支持 SQLite（默认）和 PostgreSQL，并可轻松扩展到其他数据库。

---

## 🎯 当前架构

```
┌─────────────────┐
│   DocumentService │  ← 业务逻辑层
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ DocumentRepository│  ← 数据访问层（仓储模式）
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   DatabaseManager │  ← 数据库连接管理
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
 SQLite   PostgreSQL (可扩展)
```

---

## ⚙️ 配置 SQLite（默认）

### 1. 环境配置

编辑 `.env` 文件：

```bash
DATABASE_TYPE=sqlite
SQLITE_DATABASE_PATH=./data/documents.db
```

### 2. 自动初始化

服务启动时会自动：
- ✅ 创建 `./data` 目录
- ✅ 创建 `documents.db` 数据库文件
- ✅ 创建 `document_metadata` 表

### 3. 验证

```bash
# 启动服务
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 上传一个测试文件
curl -X POST http://localhost:8000/documents/upload \
  -F "file=@test.txt"

# 查询列表（应该返回刚上传的文档）
curl http://localhost:8000/documents/
```

---

## 🔄 切换到 PostgreSQL

### 1. 安装 PostgreSQL

**Windows**:
```bash
# 下载并安装 PostgreSQL
# https://www.postgresql.org/download/windows/
```

**Linux**:
```bash
sudo apt-get install postgresql postgresql-contrib
```

**macOS**:
```bash
brew install postgresql
```

### 2. 创建数据库

```bash
# 连接到 PostgreSQL
psql -U postgres

# 创建数据库
CREATE DATABASE rag_db;

# 创建用户（可选）
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

服务会自动创建表结构。

---

## 🔧 扩展到其他数据库

### 支持的数据库类型

| 数据库 | 状态 | 连接字符串示例 |
|--------|------|----------------|
| **SQLite** | ✅ 已支持 | `sqlite:///./data/documents.db` |
| **PostgreSQL** | ✅ 已支持 | `postgresql://user:pass@localhost/db` |
| **MySQL** | 🔜 待实现 | `mysql+pymysql://user:pass@localhost/db` |
| **MariaDB** | 🔜 待实现 | `mariadb+pymysql://user:pass@localhost/db` |
| **Oracle** | 🔜 待实现 | `oracle+cx_oracle://user:pass@localhost/db` |

### 添加新数据库支持

#### 步骤 1: 在 `DatabaseManager` 中添加配置方法

```python
# app/db/database.py

def _setup_mysql(self):
    """配置 MySQL 数据库"""
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

#### 步骤 2: 在 `_initialize_database` 中添加分支

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

#### 步骤 3: 更新配置

```bash
# .env
DATABASE_TYPE=mysql
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/rag_db
```

#### 步骤 4: 安装驱动

```bash
pip install pymysql
```

---

## 📊 数据库表结构

### document_metadata 表

| 字段 | 类型 | 说明 |
|------|------|------|
| **id** | INTEGER | 自增主键 |
| **document_id** | VARCHAR(100) | 文档UUID（唯一索引） |
| **file_name** | VARCHAR(500) | 原始文件名 |
| **file_type** | VARCHAR(50) | 文件类型扩展名 |
| **file_size** | INTEGER | 文件大小（字节） |
| **text_length** | INTEGER | 提取的文本长度 |
| **storage_path** | VARCHAR(1000) | 文件存储路径 |
| **created_at** | DATETIME | 上传时间 |
| **updated_at** | DATETIME | 更新时间 |
| **status** | VARCHAR(20) | 处理状态 |
| **metadata** | JSON | 额外元数据（JSON格式） |

### 索引

- `idx_document_id`: 文档ID索引（加速查询）
- `idx_file_type`: 文件类型索引（加速过滤）
- `idx_created_at`: 创建时间索引（加速排序）
- `idx_status`: 状态索引（加速过滤）

---

## 🛠️ Repository 模式优势

### 1. 解耦业务逻辑和数据访问

```python
# 业务层不需要知道数据存储细节
async def upload_document(self, file, metadata):
    # ... 处理文档 ...
    
    repo = DocumentRepository(db_session)
    repo.create(...)  # ← 调用仓储层
    
    # 如果更换数据库，业务代码无需修改
```

### 2. 易于测试

```python
# 可以 mock Repository 进行单元测试
class MockDocumentRepository:
    def create(self, ...):
        return MockDocumentMetadata()
    
    def get_by_id(self, document_id):
        return None
```

### 3. 统一的数据访问接口

所有数据库操作都通过 Repository，便于：
- 添加缓存层
- 记录审计日志
- 实现权限控制

---

## 🚀 性能优化建议

### 1. 连接池配置（PostgreSQL）

```python
# app/db/database.py
self.engine = create_engine(
    database_url,
    poolclass=pool.QueuePool,
    pool_size=10,           # 基础连接数
    max_overflow=20,        # 最大溢出连接数
    pool_timeout=30,        # 获取连接超时
    pool_recycle=1800,      # 连接回收时间（秒）
    pool_pre_ping=True,     # 使用前检查连接
)
```

### 2. 批量操作

```python
# 批量插入（未来实现）
def batch_create(self, documents: List[Dict]):
    self.db.bulk_insert_mappings(DocumentMetadata, documents)
    self.db.commit()
```

### 3. 查询优化

```python
# 使用索引字段过滤
docs = repo.list_all(file_type="pdf", status="completed")

# 避免 N+1 查询
# 使用 joinedload 预加载关联数据
```

---

## 📝 迁移现有数据

### 从 SQLite 迁移到 PostgreSQL

```python
# migration_script.py
import sqlite3
import psycopg2
from sqlalchemy import create_engine

# 1. 读取 SQLite 数据
sqlite_conn = sqlite3.connect('./data/documents.db')
sqlite_cursor = sqlite_conn.cursor()
sqlite_cursor.execute("SELECT * FROM document_metadata")
rows = sqlite_cursor.fetchall()

# 2. 写入 PostgreSQL
pg_engine = create_engine("postgresql://user:pass@localhost/rag_db")
with pg_engine.connect() as pg_conn:
    for row in rows:
        pg_conn.execute(
            text("""
                INSERT INTO document_metadata 
                (document_id, file_name, file_type, ...)
                VALUES (:document_id, :file_name, :file_type, ...)
            """),
            {
                "document_id": row[1],
                "file_name": row[2],
                "file_type": row[3],
                # ...
            }
        )
    pg_conn.commit()
```

---

## 🔍 故障排查

### 问题 1: SQLite 锁定错误

**症状**: `database is locked`

**解决**:
```python
# 确保每次使用后关闭会话
db_session.close()

# 或使用上下文管理器
with db_manager.SessionLocal() as db:
    # 使用 db
    pass  # 自动关闭
```

### 问题 2: PostgreSQL 连接失败

**症状**: `could not connect to server`

**检查**:
```bash
# 确认 PostgreSQL 正在运行
pg_lsclusters

# 检查端口
netstat -an | grep 5432

# 测试连接
psql -h localhost -U rag_user -d rag_db
```

### 问题 3: 表不存在

**症状**: `relation "document_metadata" does not exist`

**解决**:
```python
# 手动创建表
from app.db.database import db_manager
db_manager.create_tables()
```

---

## ✨ 总结

✅ **已实现**:
- SQLite 数据库支持（默认）
- PostgreSQL 数据库支持
- Repository Pattern 架构
- 完整的 CRUD 操作
- 分页和搜索功能

🎯 **可扩展**:
- 轻松添加 MySQL、Oracle 等数据库
- 统一的接口，业务代码无需修改
- 支持连接池和性能优化

📅 **下一步**:
- 实现数据迁移脚本
- 添加数据库备份功能
- 实现读写分离（主从复制）

**现在上传的文档元数据会自动保存到 SQLite 数据库！** 🎉
