# 数据库文件路径优化

## 📋 变更说明

将 `rag_documents.db` 数据库文件从 rag-scheduler 根目录移动到 `data/` 目录，实现更好的文件组织和管理。

---

## ✅ 已完成的变更

### 1. 移动数据库文件
- **源位置**: `rag-scheduler/rag_documents.db`
- **目标位置**: `rag-scheduler/data/rag_documents.db`
- **操作**: 使用 `Move-Item` 命令安全移动文件

### 2. 更新配置文件
**文件**: [`app/core/config.py`](../app/core/config.py)

```python
# 数据库配置
DATABASE_TYPE: str = "sqlite"
DATABASE_URL: str = "sqlite:///./data/documents.db"  # ✅ 指向 data 目录
SQLITE_DATABASE_PATH: str = "./data/documents.db"    # ✅ 指向 data 目录
```

### 3. 创建 .env 配置文件
**文件**: `.env`

```env
# 数据库配置
DATABASE_TYPE=sqlite
DATABASE_URL=sqlite:///./data/documents.db
SQLITE_DATABASE_PATH=./data/documents.db
```

### 4. 验证 .env.example
**文件**: `.env.example` - 已确认配置正确

---

## 🎯 优势

### 1. 更好的文件组织
```
rag-scheduler/
├── data/                    # ✨ 数据文件集中管理
│   ├── documents.db         # SQLite 数据库
│   ├── rag_documents.db     # 旧数据库（可删除）
│   └── chromadb/            # ChromaDB 向量数据
├── uploads/                 # 上传的文件
├── uploads_text/            # 清洗后的文本
└── app/                     # 应用代码
```

### 2. 便于备份和迁移
- 所有数据文件在同一个目录
- 可以轻松备份整个 `data/` 目录
- 部署时只需复制 `data/` 目录

### 3. 避免根目录混乱
- 根目录保持简洁
- 符合项目规范（非 README 文件不放在根目录）
- 易于维护和清理

---

## 🔧 配置说明

### 当前使用的数据库文件
根据配置文件，系统使用的是：
- **文件**: `data/documents.db`
- **路径**: `./data/documents.db`

### 旧数据库文件
- **文件**: `data/rag_documents.db`
- **状态**: 已移动但未使用
- **建议**: 如果确认不再需要，可以删除

---

## 📝 注意事项

### 1. 首次启动
服务启动时会自动：
- ✅ 检查 `data/` 目录是否存在
- ✅ 如果不存在则创建目录
- ✅ 初始化数据库表结构

### 2. 数据迁移
如果需要从旧数据库迁移数据：

```bash
# 方法1：手动复制表
sqlite3 data/rag_documents.db ".dump document_metadata" | sqlite3 data/documents.db

# 方法2：使用 Python 脚本
python migrate_database.py
```

### 3. 环境变量优先级
配置加载顺序：
1. `.env` 文件（最高优先级）
2. 系统环境变量
3. `config.py` 中的默认值

---

## 🚀 验证步骤

### 1. 检查文件位置
```bash
# 确认数据库文件在 data 目录
ls -la data/*.db
```

预期输出：
```
documents.db
rag_documents.db (可选，旧文件)
```

### 2. 启动服务
```bash
cd rag-scheduler
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 测试上传
```bash
curl -X POST http://localhost:8000/documents/upload \
  -F "file=@test.txt"
```

### 4. 验证数据存储
```bash
# 查询数据库
sqlite3 data/documents.db "SELECT COUNT(*) FROM document_metadata;"
```

---

## 💡 最佳实践

### 1. 定期备份
```bash
# 备份整个 data 目录
cp -r data/ data.backup.$(date +%Y%m%d)
```

### 2. 监控文件大小
```bash
# 查看数据库文件大小
du -h data/*.db
```

### 3. 清理旧数据
```bash
# 删除过期的数据库文件
rm data/rag_documents.db  # 确认不再使用后
```

---

## 📊 相关文件

| 文件 | 说明 |
|------|------|
| `app/core/config.py` | 数据库配置定义 |
| `.env` | 实际环境配置 |
| `.env.example` | 配置模板 |
| `data/documents.db` | 当前使用的数据库 |
| `data/rag_documents.db` | 旧数据库（待清理） |

---

## 🔄 后续优化建议

1. **统一数据库文件名**
   - 考虑将 `rag_documents.db` 重命名为 `documents.db`
   - 或反之，保持一致性

2. **添加数据库版本管理**
   - 使用 Alembic 进行 schema 迁移
   - 记录数据库版本号

3. **实现自动备份**
   - 定期自动备份 `data/` 目录
   - 保留最近 N 个备份

4. **监控和告警**
   - 监控数据库文件大小
   - 当超过阈值时发出警告

---

**变更日期**: 2026-05-11  
**执行人**: AI Assistant  
**影响范围**: 数据库文件路径配置
