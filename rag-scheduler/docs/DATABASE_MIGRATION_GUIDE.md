# 数据库迁移指南

## 📋 概述

本文档说明如何管理 rag-scheduler 服务的数据库 schema 变更，特别是添加新字段时的迁移流程。

## 🐛 问题背景

当在数据库模型中添加新字段（如 `text_file_path`）时，已有的 SQLite 数据库文件不会自动更新表结构，导致运行时错误：

```
sqlite3.OperationalError: no such column: document_metadata.text_file_path
```

## ✅ 解决方案

### 方案 1：自动迁移（推荐）⭐

系统现已集成**自动迁移机制**，在服务启动时自动检测并执行待执行的迁移。

#### 工作原理

1. **服务启动时**：[DocumentService.__init__()](file://g:\rag\kret-rag\rag-scheduler\app\services\document_service.py#L31-L48) 自动调用 [run_migrations()](file://g:\rag\kret-rag\rag-scheduler\app\db\db_migrator.py#L108-L112)
2. **迁移管理器**：检查每个迁移是否已执行
3. **智能跳过**：如果字段已存在，自动跳过该迁移
4. **安全执行**：使用事务确保数据一致性

#### 代码位置

- **迁移管理器**: [`app/db/db_migrator.py`](file://g:\rag\kret-rag\rag-scheduler\app\db\db_migrator.py)
- **自动调用**: [`app/services/document_service.py`](file://g:\rag\kret-rag\rag-scheduler\app\services\document_service.py#L43-L44)

#### 日志示例

```
INFO:app.services.document_service:检查并执行数据库迁移...
============================================================
开始执行数据库迁移
============================================================
✅ [Migration 001] text_file_path 字段已存在，跳过
============================================================
✅ 所有迁移完成！成功执行 1/1 个迁移
============================================================
INFO:app.services.document_service:数据库初始化完成
```

### 方案 2：手动迁移

如果需要手动执行迁移（例如在部署脚本中）：

```bash
cd rag-scheduler
python migrate_add_text_file_path.py
```

或通用迁移命令：

```bash
cd rag-scheduler
python -m app.db.db_migrator
```

### 方案 3：重建数据库（仅开发环境）

⚠️ **警告**：这会删除所有数据！

```bash
# 删除旧数据库
rm data/rag_scheduler.db

# 重启服务，自动创建新表结构
uvicorn app.main:app --reload
```

## 🔄 添加新迁移的步骤

### 步骤 1：在 db_migrator.py 中添加迁移方法

```python
class DatabaseMigrator:
    def __init__(self):
        self.migrations = [
            self._migration_001_add_text_file_path,
            self._migration_002_add_xxx_field,  # ⭐ 新增
        ]
    
    def _migration_002_add_xxx_field(self):
        """
        迁移 002: 为 xxx 表添加 yyy 字段
        
        版本: 0.0.2
        日期: 2026-05-XX
        描述: 支持 xxx 功能
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # 检查是否已存在
            if self._check_column_exists(cursor, "table_name", "column_name"):
                print("✅ [Migration 002] 字段已存在，跳过")
                conn.close()
                return True
            
            print("🔄 [Migration 002] 添加字段...")
            
            # 添加新字段
            cursor.execute("""
                ALTER TABLE table_name 
                ADD COLUMN column_name VARCHAR(255)
            """)
            
            conn.commit()
            print("✅ [Migration 002] 成功")
            
            conn.close()
            return True
            
        except Exception as e:
            conn.rollback()
            conn.close()
            print(f"❌ [Migration 002] 失败: {str(e)}")
            raise
```

### 步骤 2：更新数据库模型

在 [`app/models/db_models.py`](file://g:\rag\kret-rag\rag-scheduler\app\models\db_models.py) 中添加字段：

```python
class DocumentMetadata(db_manager.Base):
    # ... 其他字段
    new_column = Column(String(255), nullable=True, comment="新字段")
```

### 步骤 3：更新 Repository 层

在 [`app/repositories/document_repository.py`](file://g:\rag\kret-rag\rag-scheduler\app\repositories\document_repository.py) 中更新相关方法。

### 步骤 4：测试迁移

```bash
# 1. 备份数据库
cp data/rag_scheduler.db data/rag_scheduler.db.backup

# 2. 运行迁移
python -m app.db.db_migrator

# 3. 验证
sqlite3 data/rag_scheduler.db ".schema document_metadata"
```

## 📊 当前迁移列表

| 版本号 | 迁移名称 | 日期 | 状态 | 描述 |
|--------|---------|------|------|------|
| 001 | add_text_file_path | 2026-05-10 | ✅ 已完成 | 添加清洗后文本文件路径字段 |

## 🔍 故障排查

### 问题 1：迁移失败

**症状**：
```
❌ [Migration 001] 失败: duplicate column name
```

**原因**：字段已存在但迁移检查逻辑有问题

**解决**：
- 检查 `_check_column_exists` 方法
- 手动验证字段是否存在：
  ```bash
  sqlite3 data/rag_scheduler.db "PRAGMA table_info(document_metadata);"
  ```

### 问题 2：数据库锁定

**症状**：
```
sqlite3.OperationalError: database is locked
```

**原因**：有其他进程正在访问数据库

**解决**：
1. 停止所有正在运行的服务
2. 检查是否有未关闭的数据库连接
3. 重启服务

### 问题 3：迁移后仍然报错

**症状**：迁移成功但运行时仍报 "no such column"

**原因**：使用了旧的数据库连接

**解决**：
1. 完全重启服务
2. 清除 Python 缓存：
   ```bash
   find . -type d -name __pycache__ -exec rm -rf {} +
   ```
3. 重新启动服务

## 💡 最佳实践

### 1. 始终使用迁移
- ✅ 不要手动修改数据库 schema
- ✅ 所有变更都通过迁移脚本
- ✅ 保持迁移脚本的版本控制

### 2. 测试迁移
- ✅ 在开发环境充分测试
- ✅ 备份生产数据库
- ✅ 准备回滚方案

### 3. 向后兼容
- ✅ 新字段设置为 `nullable=True`
- ✅ 提供默认值
- ✅ 避免删除字段（改为标记废弃）

### 4. 文档化
- ✅ 每个迁移都要有清晰的注释
- ✅ 记录迁移的目的和影响
- ✅ 更新 CHANGELOG

## 🚀 未来改进方向

1. **迁移版本追踪**：创建 `migration_history` 表记录已执行的迁移
2. **Alembic 集成**：使用专业的数据库迁移工具
3. **回滚支持**：实现向下迁移（downgrade）
4. **自动化测试**：为每个迁移编写测试用例

## 📚 相关文档

- [CLEANED_TEXT_AUTO_SAVE.md](CLEANED_TEXT_AUTO_SAVE.md) - 清洗后文本保存功能
- [FILE_PROCESSING_FLOW.md](FILE_PROCESSING_FLOW.md) - 文件处理流程
- [README.md](README.md) - 项目说明

## 🔗 参考资料

- [SQLite ALTER TABLE 文档](https://www.sqlite.org/lang_altertable.html)
- [SQLAlchemy Schema Migration](https://docs.sqlalchemy.org/en/20/core/metadata.html)
- [Alembic - SQLAlchemy 迁移工具](https://alembic.sqlalchemy.org/)
