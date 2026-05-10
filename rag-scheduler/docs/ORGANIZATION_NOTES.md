# rag-scheduler 文档整理说明

## 📋 整理内容

根据项目规范，对 rag-scheduler 根目录的 md 文件进行了整理和归类。

### 1. 创建 docs 目录
- 路径: `rag-scheduler/docs/`
- 用途: 存放 rag-scheduler 服务的功能文档和技术指南

### 2. 移动的文件（18个）
以下文件已从 rag-scheduler 根目录移动到 `docs/` 目录：

| 文件名 | 类别 | 说明 |
|--------|------|------|
| QUICKSTART_UPLOAD.md | 快速开始 | 上传功能快速入门 |
| UPLOAD_TEST_README.md | 快速开始 | 上传测试页面指南 |
| TEST_FILES_GUIDE.md | 快速开始 | 测试文件说明 |
| QUERY_TEST_GUIDE.md | 查询检索 | 查询测试页面指南 ⭐ |
| RAG_QUERY_FEATURE.md | 查询检索 | RAG查询功能详解 |
| HYBRID_SEARCH_RERANK.md | 查询检索 | 混合检索和重排序 |
| RAG_COMPLETE_FEATURES.md | 查询检索 | RAG完整功能特性 |
| RAG_PIPELINE_IMPLEMENTATION.md | 查询检索 | RAG流水线实现 |
| FILE_PROCESSING_FLOW.md | 文档处理 | 文件处理流程 |
| TABLE_TO_MARKDOWN.md | 文档处理 | 表格转Markdown |
| TABLE_OCR_OPTIMIZATION.md | 文档处理 | 表格OCR优化 |
| DATABASE_GUIDE.md | 数据库 | 数据库使用指南 |
| DATABASE_IMPLEMENTATION_SUMMARY.md | 数据库 | 数据库实现总结 |
| DATABASE_MIGRATION_GUIDE.md | 数据库 | 数据库迁移指南 |
| DUPLICATE_DETECTION.md | 去重机制 | 去重机制详解 |
| IMPLEMENTATION_SUMMARY_DUPLICATE.md | 去重机制 | 去重实现总结 |
| QUICKREF_DUPLICATE.md | 去重机制 | 去重快速参考 |
| IMPLEMENTATION_SUMMARY.md | 实现总结 | 整体实现总结 |

### 3. 保留的文件
rag-scheduler 根目录仅保留：
- **README.md** - 服务主文档（已更新添加文档导航）

---

## 🎯 文档组织结构

```
rag-scheduler/
│
├── README.md                    # ✨ 根目录：服务主文档（唯一保留）
│
├── docs/                        # ✨ 新增：功能文档目录
│   ├── README.md                # 文档索引（按类别组织）
│   │
│   ├── 快速开始 (3个)
│   │   ├── QUICKSTART_UPLOAD.md
│   │   ├── UPLOAD_TEST_README.md
│   │   └── TEST_FILES_GUIDE.md
│   │
│   ├── 查询检索 (5个)
│   │   ├── QUERY_TEST_GUIDE.md          ⭐ 重点推荐
│   │   ├── RAG_QUERY_FEATURE.md
│   │   ├── HYBRID_SEARCH_RERANK.md
│   │   ├── RAG_COMPLETE_FEATURES.md
│   │   └── RAG_PIPELINE_IMPLEMENTATION.md
│   │
│   ├── 文档处理 (3个)
│   │   ├── FILE_PROCESSING_FLOW.md
│   │   ├── TABLE_TO_MARKDOWN.md
│   │   └── TABLE_OCR_OPTIMIZATION.md
│   │
│   ├── 数据库 (3个)
│   │   ├── DATABASE_GUIDE.md
│   │   ├── DATABASE_IMPLEMENTATION_SUMMARY.md
│   │   └── DATABASE_MIGRATION_GUIDE.md
│   │
│   ├── 去重机制 (3个)
│   │   ├── DUPLICATE_DETECTION.md
│   │   ├── IMPLEMENTATION_SUMMARY_DUPLICATE.md
│   │   └── QUICKREF_DUPLICATE.md
│   │
│   └── 实现总结 (1个)
│       └── IMPLEMENTATION_SUMMARY.md
│
└── bugfixes/                    # 修复文档目录
    ├── README.md
    ├── FIX_SUMMARY.md
    ├── TROUBLESHOOTING.md
    └── ...
```

---

## 📖 文档分类原则

### 根目录 (Root)
**保留内容**: 
- README.md
- 作用: 服务入口文档，提供概览和快速导航

### docs/ 目录
**存放内容**:
- 快速开始指南
- 功能详细说明
- 技术实现文档
- 配置和使用指南

**特点**: 与 rag-scheduler 服务直接相关的技术文档

### bugfixes/ 目录
**存放内容**:
- 问题修复记录
- 故障排查指南
- 启动问题解决
- 依赖冲突处理

**特点**: 历史问题修复记录

---

## 🔗 链接更新

### rag-scheduler/README.md 更新
- ✅ 添加"文档导航"部分
- ✅ 列出主要功能文档链接
- ✅ 添加故障排查指南链接

### 项目根 README.md 更新
- ✅ 添加 rag-scheduler 服务文档分类
- ✅ 列出关键文档链接（查询测试、文件处理等）
- ✅ 中英文版本同步更新

### docs/README.md 新建
- ✅ 创建完整的文档索引
- ✅ 按6个类别组织文档
- ✅ 提供使用建议和快速链接
- ✅ 包含文档统计和维护规范

---

## 💡 使用建议

### 新用户：
1. 阅读 [README.md](../README.md) 了解服务概况
2. 查看 [docs/QUICKSTART_UPLOAD.md](./QUICKSTART_UPLOAD.md) 开始使用
3. 使用 [docs/QUERY_TEST_GUIDE.md](./QUERY_TEST_GUIDE.md) 测试查询功能 ⭐

### 开发者：
1. 查看 [docs/RAG_PIPELINE_IMPLEMENTATION.md](./RAG_PIPELINE_IMPLEMENTATION.md) 了解架构
2. 阅读 [docs/FILE_PROCESSING_FLOW.md](./FILE_PROCESSING_FLOW.md) 理解数据处理
3. 参考 [docs/DATABASE_GUIDE.md](./DATABASE_GUIDE.md) 进行数据库开发

### 遇到问题时：
1. 首先查看 [bugfixes/TROUBLESHOOTING.md](../bugfixes/TROUBLESHOOTING.md)
2. 参考 [docs/QUERY_TEST_GUIDE.md](./QUERY_TEST_GUIDE.md) 进行测试
3. 查看 [docs/DUPLICATE_DETECTION.md](./DUPLICATE_DETECTION.md) 处理重复问题

---

## ✅ 整理完成清单

- [x] 创建 rag-scheduler/docs/ 目录
- [x] 移动18个文档到 docs/ 目录
- [x] 创建 docs/README.md 索引文件
- [x] 更新 rag-scheduler/README.md 添加文档导航
- [x] 更新项目根 README.md 添加 rag-scheduler 文档链接
- [x] 更新项目根 README_en.md 添加英文链接
- [x] 验证根目录只保留 README.md
- [x] 确保所有链接有效

---

## 📊 文档统计

| 位置 | 文件数量 | 说明 |
|------|----------|------|
| rag-scheduler 根目录 | 1 | README.md |
| rag-scheduler/docs/ | 19 | 功能文档 + 索引 |
| rag-scheduler/bugfixes/ | 12 | 修复文档 + 索引 |
| **总计** | **32** | **结构化组织** |

---

## 🔄 维护规范

### 新增文档时：
1. **功能文档** → 放入 `docs/` 目录
2. **修复文档** → 放入 `bugfixes/` 目录
3. 在相应的 README.md 中添加索引链接
4. 保持文档格式一致性

### 文档分类：
- 快速开始类 → docs/ 顶部
- 核心功能类 → docs/ 按模块分组
- 技术实现类 → docs/ 后面部分
- 修复记录类 → bugfixes/ 目录

### 更新文档时：
1. 确保相关索引文件同步更新
2. 检查所有内部链接是否有效
3. 保持文档标题清晰易懂

---

**整理日期**: 2026-05-11  
**执行人**: AI Assistant  
**遵循规范**: process rule - 修复和功能文档不放在根目录，只保留README
