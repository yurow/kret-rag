# 文档清理说明

## 📋 清理内容

根据项目规范，对md文件进行了整理和归类：

### 1. 创建 bugfixes 目录
- 路径: `rag-scheduler/bugfixes/`
- 用途: 存放所有问题修复相关的文档

### 2. 移动的文件
以下文件已移动到 `rag-scheduler/bugfixes/` 目录：

| 文件名 | 说明 |
|--------|------|
| FIX_SUMMARY.md | 最新问题修复总结 |
| TROUBLESHOOTING.md | 综合故障排查指南 |
| STARTUP_CHECKLIST.md | 启动检查清单 |
| BUGFIX_DATETIME_VALIDATION.md | 日期时间验证修复 |
| FIX_404_ERROR.md | 404错误修复 |
| FIX_RESPONSE_VALIDATION.md | 响应验证修复 |
| DEPENDENCY_FIX.md | 依赖冲突修复 |
| DOCX_EXTRACTION_ERROR_GUIDE.md | DOCX提取错误指南 |
| TABLE_MARKDOWN_DEBUG.md | 表格Markdown转换调试 |
| CLEANED_TEXT_AUTO_SAVE.md | 清洗文本自动保存 |

### 3. 保留的文件
以下文件保留在原有位置（功能文档和使用指南）：

**根目录**:
- README.md - 项目主文档（中文）
- README_en.md - 项目主文档（英文）✨ 新增
- API_EXAMPLES.md - API示例
- ARCHITECTURE.md - 架构说明
- CHECKLIST.md - 检查清单
- ISSUES_TRACKING.md - 问题跟踪
- QUICKSTART.md - 快速开始

**rag-scheduler目录**:
- README.md - rag-scheduler文档
- QUERY_TEST_GUIDE.md - 查询测试指南
- HYBRID_SEARCH_RERANK.md - 混合检索和重排序
- RAG_COMPLETE_FEATURES.md - RAG完整功能
- RAG_PIPELINE_IMPLEMENTATION.md - RAG流水线实现
- RAG_QUERY_FEATURE.md - RAG查询功能
- DUPLICATE_DETECTION.md - 去重机制
- FILE_PROCESSING_FLOW.md - 文件处理流程
- IMPLEMENTATION_SUMMARY.md - 实现总结
- IMPLEMENTATION_SUMMARY_DUPLICATE.md - 去重实现总结
- QUICKREF_DUPLICATE.md - 去重快速参考
- QUICKSTART_UPLOAD.md - 上传快速开始
- TABLE_OCR_OPTIMIZATION.md - 表格OCR优化
- TABLE_TO_MARKDOWN.md - 表格转Markdown
- TEST_FILES_GUIDE.md - 测试文件指南
- UPLOAD_TEST_README.md - 上传测试说明
- DATABASE_GUIDE.md - 数据库指南
- DATABASE_IMPLEMENTATION_SUMMARY.md - 数据库实现总结
- DATABASE_MIGRATION_GUIDE.md - 数据库迁移指南

**llm-session目录**:
- README.md - llm-session文档

### 4. 新增文件
- **README_en.md** - 英文版本的项目文档 ✨
- **rag-scheduler/bugfixes/README.md** - bugfixes目录索引

---

## 🎯 文档组织原则

### 修复类文档 → bugfixes/
包含：
- 问题修复记录
- 故障排查指南
- 启动检查清单
- 依赖问题解决

### 功能类文档 → 原位置保留
包含：
- 功能使用说明
- API文档
- 架构设计
- 实现总结

### 项目级文档 → 根目录
包含：
- README（中英文）
- 快速开始
- 架构说明
- 问题跟踪

---

## 📖 使用建议

### 遇到问题时：
1. 查看 `rag-scheduler/bugfixes/TROUBLESHOOTING.md`
2. 参考 `rag-scheduler/bugfixes/STARTUP_CHECKLIST.md`
3. 浏览 `rag-scheduler/bugfixes/FIX_SUMMARY.md`

### 学习功能时：
1. 阅读根目录 `README.md` 或 `README_en.md`
2. 查看各服务的 README.md
3. 参考具体功能的文档

### 开发参考时：
1. 查看 `ARCHITECTURE.md` 了解架构
2. 阅读 `API_EXAMPLES.md` 学习API使用
3. 参考实现总结文档

---

## 🔄 维护规范

### 新增修复文档时：
1. 保存到 `rag-scheduler/bugfixes/` 目录
2. 文件名格式：`FIX_问题描述.md` 或 `BUGFIX_模块名.md`
3. 在 `bugfixes/README.md` 中添加索引

### 新增功能文档时：
1. 保存到对应服务目录
2. 保持文件名清晰易懂
3. 在主README中适当位置添加链接

### 更新README时：
1. 同时更新中文版和英文版
2. 保持内容同步
3. 确保链接有效

---

## ✅ 清理完成

- [x] 创建 bugfixes 目录
- [x] 移动修复类文档到 bugfixes/
- [x] 创建 bugfixes/README.md 索引
- [x] 创建 README_en.md 英文版本
- [x] 更新所有相关路径引用
- [x] 验证文档结构清晰合理

---

**清理日期**: 2026-05-11  
**执行人**: AI Assistant
