# 文档结构优化说明

## 📋 优化内容

根据项目规范，对根目录的md文件进行了整理和归类，确保根目录只保留README相关文件。

### 1. 创建 docs 目录
- 路径: `docs/`
- 用途: 存放项目级文档（快速开始、架构、API示例等）

### 2. 移动的文件
以下文件已从根目录移动到 `docs/` 目录：

| 文件名 | 类型 | 说明 |
|--------|------|------|
| QUICKSTART.md | 快速开始 | 环境配置和启动指南 |
| ARCHITECTURE.md | 架构设计 | 系统架构和技术选型 |
| API_EXAMPLES.md | API文档 | API使用示例和代码片段 |
| CHECKLIST.md | 运维检查 | 日常运维检查清单 |
| ISSUES_TRACKING.md | 问题跟踪 | 已知问题和修复计划 |

### 3. 保留的文件
根目录仅保留以下文件：
- **README.md** - 中文版本的项目主文档
- **README_en.md** - 英文版本的项目主文档

---

## 🎯 文档组织结构

```
kret-rag/
├── README.md                    # ✨ 根目录：中文主文档
├── README_en.md                 # ✨ 根目录：英文主文档
│
├── docs/                        # ✨ 新增：项目文档目录
│   ├── README.md                # docs目录索引
│   ├── QUICKSTART.md            # 快速开始指南
│   ├── ARCHITECTURE.md          # 系统架构文档
│   ├── API_EXAMPLES.md          # API使用示例
│   ├── CHECKLIST.md             # 日常检查清单
│   └── ISSUES_TRACKING.md       # 问题跟踪记录
│
├── rag-scheduler/               # RAG调度器服务
│   ├── README.md                # 服务文档
│   ├── QUERY_TEST_GUIDE.md      # 功能文档
│   ├── HYBRID_SEARCH_RERANK.md  # 功能文档
│   ├── RAG_*.md                 # 功能文档
│   ├── DATABASE_*.md            # 数据库文档
│   ├── TABLE_*.md               # 表格处理文档
│   ├── DUPLICATE_DETECTION.md   # 功能文档
│   └── bugfixes/                # 修复文档目录
│       ├── README.md            # bugfixes索引
│       ├── CLEANUP_NOTES.md     # 清理说明
│       ├── FIX_SUMMARY.md       # 修复总结
│       ├── TROUBLESHOOTING.md   # 故障排查
│       └── ...                  # 其他修复文档
│
└── llm-session/                 # LLM会话管理服务
    └── README.md                # 服务文档
```

---

## 📖 文档分类原则

### 根目录 (Root)
**保留内容**: 
- README.md (中英文版本)
- 作用: 项目入口文档，提供概览和快速导航

### docs/ 目录
**存放内容**:
- 快速开始指南 (QUICKSTART.md)
- 架构设计文档 (ARCHITECTURE.md)
- API使用文档 (API_EXAMPLES.md)
- 运维检查清单 (CHECKLIST.md)
- 问题跟踪记录 (ISSUES_TRACKING.md)

**特点**: 项目级别的通用文档，适用于整个系统

### rag-scheduler/ 目录
**存放内容**:
- 服务特定的功能文档
- 数据库相关文档
- 表格处理文档
- RAG功能文档

**特点**: 与rag-scheduler服务直接相关的技术文档

### rag-scheduler/bugfixes/ 目录
**存放内容**:
- 问题修复记录
- 故障排查指南
- 启动问题解决
- 依赖冲突处理

**特点**: 历史问题修复记录，用于参考和学习

---

## 🔗 链接更新

### README.md 更新
- ✅ 添加"文档导航"部分
- ✅ 更新所有内部链接指向 `docs/` 目录
- ✅ 添加故障排查指南链接

### README_en.md 更新
- ✅ 添加"Documentation Navigation"部分
- ✅ 更新所有内部链接指向 `docs/` 目录
- ✅ 添加中英文版本互链

### docs/README.md 新建
- ✅ 创建完整的文档索引
- ✅ 按类别组织文档列表
- ✅ 提供使用建议和快速链接

---

## 💡 使用建议

### 新用户入门流程：
1. 阅读根目录 [README.md](../README.md) 了解项目概况
2. 查看 [docs/QUICKSTART.md](./QUICKSTART.md) 进行快速开始
3. 参考 [docs/API_EXAMPLES.md](./API_EXAMPLES.md) 学习API使用

### 开发者工作流程：
1. 查看 [docs/ARCHITECTURE.md](./ARCHITECTURE.md) 了解系统设计
2. 阅读各服务的 README.md 了解具体实现
3. 参考 [docs/API_EXAMPLES.md](./API_EXAMPLES.md) 进行开发

### 遇到问题时：
1. 首先查看 [rag-scheduler/bugfixes/TROUBLESHOOTING.md](../rag-scheduler/bugfixes/TROUBLESHOOTING.md)
2. 参考 [docs/CHECKLIST.md](./CHECKLIST.md) 进行检查
3. 查看 [docs/ISSUES_TRACKING.md](./ISSUES_TRACKING.md) 了解已知问题

---

## ✅ 优化完成清单

- [x] 创建 docs/ 目录
- [x] 移动5个文档到 docs/ 目录
- [x] 创建 docs/README.md 索引文件
- [x] 更新 README.md 的链接和导航
- [x] 更新 README_en.md 的链接和导航
- [x] 验证根目录只保留README文件
- [x] 确保所有链接有效

---

## 📊 文档统计

| 位置 | 文件数量 | 说明 |
|------|----------|------|
| 根目录 | 2 | README.md, README_en.md |
| docs/ | 6 | 项目级文档 + 索引 |
| rag-scheduler/ | ~19 | 服务功能文档 |
| rag-scheduler/bugfixes/ | 12 | 修复文档 + 索引 |
| **总计** | **~39** | **结构化组织** |

---

## 🔄 维护规范

### 新增文档时：
1. **项目级文档** → 放入 `docs/` 目录
2. **服务级文档** → 放入对应服务目录
3. **修复类文档** → 放入 `bugfixes/` 目录
4. 在相应的 README.md 中添加索引链接

### 更新文档时：
1. 确保中英文版本同步更新
2. 检查所有内部链接是否有效
3. 保持文档格式一致性

### 删除文档时：
1. 从索引文件中移除链接
2. 确认没有其他文档引用该文件
3. 如有必要，添加迁移说明

---

**优化日期**: 2026-05-11  
**执行人**: AI Assistant  
**遵循规范**: process rule - 修复文档不放在根目录
