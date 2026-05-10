# 快速开始 - 本地模型配置

## 🚀 3步完成本地模型配置

### 步骤1：下载模型（仅需执行一次）

```bash
cd g:\rag\kret-rag\rag-scheduler
python download_embedding_model.py
```

**等待下载完成**（约2-5分钟，取决于网络速度）

---

### 步骤2：确认配置

检查 `.env` 文件：

```env
EMBEDDING_MODEL=./models/all-MiniLM-L6-v2
```

✅ 已自动配置，无需修改

---

### 步骤3：启动服务

```bash
.\start-scheduler.bat
```

**观察日志**：
```
INFO:     Application startup complete.
```

✅ 服务启动成功，耗时约3秒

---

## ✨ 优势对比

| 项目 | 在线模型 | 本地模型 |
|------|---------|---------|
| 首次启动 | 2-5分钟 ⏱️ | 3秒 ⚡ |
| 后续启动 | 10-30秒 | 2-3秒 |
| 网络依赖 | 需要 | 不需要 |
| 稳定性 | 受网络影响 | 稳定 |
| 磁盘占用 | ~100MB缓存 | ~100MB本地 |

---

## 📝 常见问题

### Q: 如何知道模型是否已下载？

```bash
Test-Path models\all-MiniLM-L6-v2
```

返回 `True` 表示已下载

---

### Q: 想重新下载怎么办？

```bash
python download_embedding_model.py
```

脚本会提示是否覆盖

---

### Q: 想切换回在线模型？

修改 `.env`：
```env
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

---

## 📚 详细文档

完整的使用说明请查看：
- [`docs/LOCAL_MODEL_GUIDE.md`](file://g:\rag\kret-rag\rag-scheduler\docs\LOCAL_MODEL_GUIDE.md)

---

**配置完成！** 🎉
