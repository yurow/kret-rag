# KRET-RAG 调度器

RAG调度服务，负责文档处理、向量检索和知识库管理。

## 📚 文档导航

- **[快速开始](./docs/QUICKSTART_UPLOAD.md)** - 上传功能快速入门
- **[查询测试](./docs/QUERY_TEST_GUIDE.md)** - 可视化测试页面使用指南 ⭐
- **[文件处理](./docs/FILE_PROCESSING_FLOW.md)** - 文档处理流程详解
- **[混合检索](./docs/HYBRID_SEARCH_RERANK.md)** - BM25 + 向量混合检索
- **[数据库指南](./docs/DATABASE_GUIDE.md)** - PostgreSQL配置和使用
- **[去重机制](./docs/DUPLICATE_DETECTION.md)** - 文档去重实现
- **[完整文档索引](./docs/README.md)** - 查看所有技术文档

**故障排查**: [bugfixes/README.md](./bugfixes/README.md) - 常见问题解决方案

---

## 功能模块

- **文档服务**: 文档上传、解析、分块
- **向量服务**: 文本向量化、存储、相似度搜索
- **RAG服务**: 检索增强生成

## API文档

启动服务后访问: http://localhost:8000/docs

## 开发指南

### 安装依赖
```bash
pip install -r requirements.txt
```

### 配置环境
```bash
cp .env.example .env
# 编辑 .env 文件填写正确配置
```

### 启动服务
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
