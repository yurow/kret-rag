# RAG Scheduler 文档

本目录包含 rag-scheduler 服务的详细功能文档和技术指南。

## 📋 文档分类

### 🚀 快速开始

1. **[QUICKSTART_UPLOAD.md](./QUICKSTART_UPLOAD.md)** - 上传功能快速开始
   - 文档上传流程
   - 支持的格式说明
   - 常见问题解答

2. **[UPLOAD_TEST_README.md](./UPLOAD_TEST_README.md)** - 上传测试页面使用指南
   - 测试页面功能介绍
   - 使用步骤
   - 调试技巧

3. **[TEST_FILES_GUIDE.md](./TEST_FILES_GUIDE.md)** - 测试文件指南
   - 示例文件说明
   - 测试用例
   - 验证方法

---

### 🔍 查询与检索

4. **[QUERY_TEST_GUIDE.md](./QUERY_TEST_GUIDE.md)** - 查询测试页面使用指南 ⭐
   - 完整查询测试
   - 向量搜索测试
   - RAG生成测试
   - 参数调整说明

5. **[RAG_QUERY_FEATURE.md](./RAG_QUERY_FEATURE.md)** - RAG查询功能详解
   - 查询重写机制
   - 混合检索策略
   - Rerank重排序
   - 性能优化建议

6. **[HYBRID_SEARCH_RERANK.md](./HYBRID_SEARCH_RERANK.md)** - 混合检索和重排序
   - BM25 + 向量混合检索
   - Rerank算法实现
   - 相似度计算
   - 配置参数说明

7. **[RAG_COMPLETE_FEATURES.md](./RAG_COMPLETE_FEATURES.md)** - RAG完整功能特性
   - 端到端流程
   - 核心组件
   - 高级功能
   - 最佳实践

8. **[RAG_PIPELINE_IMPLEMENTATION.md](./RAG_PIPELINE_IMPLEMENTATION.md)** - RAG流水线实现
   - 架构设计
   - 数据流图
   - 组件交互
   - 扩展点说明

---

### 📄 文档处理

9. **[FILE_PROCESSING_FLOW.md](./FILE_PROCESSING_FLOW.md)** - 文件处理流程
   - 上传验证
   - 文本提取
   - 文本清理
   - OCR处理
   - 表格转换

10. **[TABLE_TO_MARKDOWN.md](./TABLE_TO_MARKDOWN.md)** - 表格转Markdown
    - 表格识别
    - Markdown格式转换
    - 复杂表格处理
    - 质量保证

11. **[TABLE_OCR_OPTIMIZATION.md](./TABLE_OCR_OPTIMIZATION.md)** - 表格OCR优化
    - OCR引擎选择
    - 预处理策略
    - 后处理优化
    - 性能调优

---

### 🗄️ 数据库相关

12. **[DATABASE_GUIDE.md](./DATABASE_GUIDE.md)** - 数据库使用指南
    - PostgreSQL配置
    - 表结构设计
    - 索引优化
    - 备份恢复

13. **[DATABASE_IMPLEMENTATION_SUMMARY.md](./DATABASE_IMPLEMENTATION_SUMMARY.md)** - 数据库实现总结
    - ORM模型设计
    - Repository模式
    - 迁移策略
    - 性能考虑

14. **[DATABASE_MIGRATION_GUIDE.md](./DATABASE_MIGRATION_GUIDE.md)** - 数据库迁移指南
    - 自动迁移机制
    - 手动迁移步骤
    - 版本管理
    - 回滚策略

---

### 🔧 去重机制

15. **[DUPLICATE_DETECTION.md](./DUPLICATE_DETECTION.md)** - 去重机制详解
    - 哈希算法
    - 相似度检测
    - 冲突处理
    - 性能优化

16. **[IMPLEMENTATION_SUMMARY_DUPLICATE.md](./IMPLEMENTATION_SUMMARY_DUPLICATE.md)** - 去重实现总结
    - 技术方案
    - 代码结构
    - 测试结果

17. **[QUICKREF_DUPLICATE.md](./QUICKREF_DUPLICATE.md)** - 去重快速参考
    - API接口
    - 配置参数
    - 常见问题

---

### 📊 实现总结

18. **[IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md)** - 整体实现总结
    - 架构概览
    - 核心模块
    - 技术亮点
    - 待改进项

---

## 🎯 使用建议

### 新用户：
1. 首先阅读根目录的 [README.md](../README.md)
2. 查看 [QUICKSTART_UPLOAD.md](./QUICKSTART_UPLOAD.md) 了解上传流程
3. 使用 [QUERY_TEST_GUIDE.md](./QUERY_TEST_GUIDE.md) 测试查询功能

### 开发者：
1. 查看 [RAG_PIPELINE_IMPLEMENTATION.md](./RAG_PIPELINE_IMPLEMENTATION.md) 了解架构
2. 阅读 [FILE_PROCESSING_FLOW.md](./FILE_PROCESSING_FLOW.md) 理解数据处理
3. 参考 [DATABASE_GUIDE.md](./DATABASE_GUIDE.md) 进行数据库开发

### 运维人员：
1. 查看 [DATABASE_MIGRATION_GUIDE.md](./DATABASE_MIGRATION_GUIDE.md) 了解迁移
2. 参考 [DATABASE_IMPLEMENTATION_SUMMARY.md](./DATABASE_IMPLEMENTATION_SUMMARY.md) 进行维护
3. 关注 [DUPLICATE_DETECTION.md](./DUPLICATE_DETECTION.md) 处理重复问题

---

## 📂 其他文档位置

### 故障排查文档
- **位置**: `bugfixes/` 目录
- **内容**: 问题修复记录、启动检查、依赖问题解决
- **索引**: [bugfixes/README.md](../bugfixes/README.md)

### 项目级文档
- **位置**: 项目根目录的 `docs/` 目录
- **内容**: 快速开始、架构设计、API示例等
- **索引**: [../../docs/README.md](../../docs/README.md)

---

## 🔄 文档维护规范

### 新增文档时：
1. 根据文档类型选择合适的子目录或分类
2. 文件名使用英文，清晰描述内容
3. 在本文档中添加索引链接
4. 保持文档格式规范（标题、列表、代码块等）

### 文档分类原则：
- **快速开始类** → 放在顶部
- **核心功能类** → 按功能模块分组
- **技术实现类** → 放在后面
- **修复记录类** → 移至 bugfixes/ 目录

### 文档内容结构：
```markdown
# 文档标题

## 概述
[简要说明文档内容和目的]

## 详细说明
[分章节详细说明]

## 示例代码
[提供实用的代码示例]

## 配置参数
[相关配置说明]

## 常见问题
[FAQ 部分]

## 相关资源
[相关链接和参考]
```

---

## 📊 文档统计

| 类别 | 数量 | 说明 |
|------|------|------|
| 快速开始 | 3 | 上传、测试、文件指南 |
| 查询检索 | 5 | RAG查询、混合检索等 |
| 文档处理 | 3 | 文件流程、表格处理 |
| 数据库 | 3 | 配置、实现、迁移 |
| 去重机制 | 3 | 检测、实现、参考 |
| 实现总结 | 1 | 整体总结 |
| **总计** | **18** | - |

---

## 🔗 快速链接

- [rag-scheduler 主文档](../README.md)
- [故障排查指南](../bugfixes/README.md)
- [项目文档索引](../../docs/README.md)
- [API 文档](http://localhost:8000/docs)
- [查询测试页面](http://localhost:8000/test-query)

---

**最后更新**: 2026-05-11  
**维护者**: KRET-RAG Team
