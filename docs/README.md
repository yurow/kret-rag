# KRET-RAG 项目文档

本目录包含 KRET-RAG 项目的详细文档和使用指南。

## 📋 文档列表

### 🚀 快速开始

1. **[QUICKSTART.md](./QUICKSTART.md)** - 快速开始指南
   - 环境要求
   - 安装步骤
   - 配置说明
   - 启动服务
   - 首次使用

---

### 🏗️ 架构设计

2. **[ARCHITECTURE.md](./ARCHITECTURE.md)** - 系统架构文档
   - 微服务架构说明
   - 组件交互关系
   - 数据流图
   - 技术选型理由

---

### 📖 API 文档

3. **[API_EXAMPLES.md](./API_EXAMPLES.md)** - API 使用示例
   - rag-scheduler API 示例
   - llm-session API 示例
   - cURL 命令示例
   - Python 代码示例
   - 常见场景演示

---

### ✅ 检查清单

4. **[CHECKLIST.md](./CHECKLIST.md)** - 日常检查清单
   - 启动前检查项
   - 运行中监控项
   - 维护任务清单
   - 性能优化建议

---

### 🐛 问题跟踪

5. **[ISSUES_TRACKING.md](./ISSUES_TRACKING.md)** - 问题跟踪与修复计划
   - 已知问题列表
   - 修复优先级
   - 进度跟踪
   - 版本规划

---

## 🎯 使用建议

### 新用户：
1. 首先阅读根目录的 [README.md](../README.md) 或 [README_en.md](../README_en.md)
2. 按照 [QUICKSTART.md](./QUICKSTART.md) 进行快速开始
3. 参考 [API_EXAMPLES.md](./API_EXAMPLES.md) 学习 API 使用

### 开发者：
1. 查看 [ARCHITECTURE.md](./ARCHITECTURE.md) 了解系统设计
2. 参考 [API_EXAMPLES.md](./API_EXAMPLES.md) 进行开发
3. 关注 [ISSUES_TRACKING.md](./ISSUES_TRACKING.md) 了解待办事项

### 运维人员：
1. 使用 [CHECKLIST.md](./CHECKLIST.md) 进行日常检查
2. 参考 [ARCHITECTURE.md](./ARCHITECTURE.md) 了解部署架构
3. 查看 [ISSUES_TRACKING.md](./ISSUES_TRACKING.md) 了解已知问题

---

## 📂 其他文档位置

### rag-scheduler 相关文档
- **功能文档**: `rag-scheduler/` 目录
- **故障排查**: `rag-scheduler/bugfixes/` 目录
- **查询测试**: `rag-scheduler/QUERY_TEST_GUIDE.md`

### llm-session 相关文档
- **服务文档**: `llm-session/README.md`

---

## 🔄 文档维护规范

### 新增文档时：
1. 根据文档类型选择合适的目录
2. 文件名使用英文，清晰描述内容
3. 在本文档中添加索引链接
4. 确保文档格式规范（标题、列表、代码块等）

### 文档分类原则：
- **快速开始类** → 根目录或 docs/
- **架构设计类** → docs/
- **API 使用类** → docs/
- **操作指南类** → docs/
- **问题跟踪类** → docs/
- **修复记录类** → bugfixes/
- **功能说明类** → 对应服务目录

### 文档内容结构：
```markdown
# 文档标题

## 概述
[简要说明文档内容和目的]

## 详细内容
[分章节详细说明]

## 示例代码
[提供实用的代码示例]

## 常见问题
[FAQ 部分]

## 相关资源
[相关链接和参考]
```

---

## 📊 文档统计

| 类别 | 数量 | 说明 |
|------|------|------|
| 快速开始 | 1 | QUICKSTART.md |
| 架构设计 | 1 | ARCHITECTURE.md |
| API 文档 | 1 | API_EXAMPLES.md |
| 运维检查 | 1 | CHECKLIST.md |
| 问题跟踪 | 1 | ISSUES_TRACKING.md |
| **总计** | **5** | - |

---

## 🔗 快速链接

- [项目主页 (中文)](../README.md)
- [Project Home (English)](../README_en.md)
- [rag-scheduler 文档](../rag-scheduler/README.md)
- [llm-session 文档](../llm-session/README.md)
- [故障排查指南](../rag-scheduler/bugfixes/README.md)

---

**最后更新**: 2026-05-11  
**维护者**: KRET-RAG Team
