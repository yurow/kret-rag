# Bug Fixes 文档索引

本目录包含 rag-scheduler 服务的所有问题修复文档和故障排查指南。

## 📋 文档列表

### 🔧 核心修复文档

1. **[FIX_SUMMARY.md](./FIX_SUMMARY.md)** - 最新问题修复总结
   - ModuleNotFoundError 解决方案
   - sentence-transformers 依赖冲突处理
   - 完整的安装和验证步骤

2. **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** - 综合故障排查指南
   - 5个常见启动问题的详细解决方案
   - 网络超时处理方法
   - 依赖版本兼容性说明

3. **[STARTUP_CHECKLIST.md](./STARTUP_CHECKLIST.md)** - 启动检查清单
   - 启动前/后的完整检查项
   - 快速问题诊断流程
   - 性能优化建议

---

### 🐛 历史修复记录

4. **[BUGFIX_DATETIME_VALIDATION.md](./BUGFIX_DATETIME_VALIDATION.md)** - 日期时间验证修复
   - Pydantic与SQLAlchemy字段类型一致性问题
   - Optional类型使用规范

5. **[FIX_404_ERROR.md](./FIX_404_ERROR.md)** - 404错误修复
   - 路由配置问题
   - 静态文件服务配置

6. **[FIX_RESPONSE_VALIDATION.md](./FIX_RESPONSE_VALIDATION.md)** - 响应验证修复
   - Pydantic模型验证问题
   - 可选字段处理

7. **[DEPENDENCY_FIX.md](./DEPENDENCY_FIX.md)** - 依赖冲突修复
   - 包版本兼容性问题
   - 依赖树分析

8. **[DOCX_EXTRACTION_ERROR_GUIDE.md](./DOCX_EXTRACTION_ERROR_GUIDE.md)** - DOCX提取错误指南
   - 文档解析异常处理
   - 容错机制实现

9. **[TABLE_MARKDOWN_DEBUG.md](./TABLE_MARKDOWN_DEBUG.md)** - 表格Markdown转换调试
   - 表格格式问题排查
   - Markdown输出优化

10. **[CLEANED_TEXT_AUTO_SAVE.md](./CLEANED_TEXT_AUTO_SAVE.md)** - 清洗文本自动保存
    - 文本持久化功能
    - 缓存机制实现

---

## 🎯 使用建议

### 遇到问题时：
1. 首先查看 [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - 综合故障排查
2. 如果是启动问题，参考 [STARTUP_CHECKLIST.md](./STARTUP_CHECKLIST.md)
3. 如果是最近的问题，查看 [FIX_SUMMARY.md](./FIX_SUMMARY.md)

### 开发参考：
- 了解历史问题和解决方案
- 学习最佳实践和避免常见陷阱
- 参考代码修复模式

---

## 📝 文档维护规范

### 新增修复文档时：
1. 文件名格式：`FIX_问题描述.md` 或 `BUGFIX_功能模块.md`
2. 必须包含：
   - 问题描述（含错误信息）
   - 根本原因分析
   - 解决方案（含代码示例）
   - 验证方法
3. 在本文档中添加链接

### 文档内容结构：
```markdown
# 问题标题

## 问题描述
[详细的错误信息和场景]

## 根本原因
[深入的原因分析]

## 解决方案
[具体的解决步骤和代码]

## 验证方法
[如何确认问题已解决]

## 预防措施
[如何避免类似问题]
```

---

## 🔄 更新记录

- **2026-05-11**: 创建bugfixes目录，整理所有修复文档
- 后续每次修复问题时，在此添加新文档

---

**提示**: 保持文档简洁明了，便于快速定位和解决问题。
