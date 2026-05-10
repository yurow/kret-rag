# KRET-RAG 快速检查清单

> 用于日常代码审查和修复进度跟踪

---

## 🔴 高优先级（必须修复）

- [x] ✅ **问题 1**: eval() 安全漏洞 - 已修复 (2026-05-09)
- [ ] ⏳ **问题 2**: 添加全局异常处理中间件
- [ ] ⏳ **问题 3**: 配置数据库连接池
- [ ] ⏳ **问题 4**: 使用 SecretStr 保护敏感信息
- [ ] ⏳ **问题 5**: 配置 CORS 白名单

---

## 🟡 中优先级（本周内完成）

- [ ] ⏳ **问题 6**: 完善类型注解
- [ ] ⏳ **问题 7**: 添加完整的 Docstring
- [ ] ⏳ **问题 8**: 实现 Redis 会话持久化
- [ ] ⏳ **问题 9**: 添加日志记录系统
- [ ] ⏳ **问题 10**: 处理 TODO 标记（至少完成 P0/P1）

---

## 🟢 低优先级（本月内完成）

- [ ] ⏳ **问题 11**: 调整依赖版本范围
- [ ] ⏳ **问题 12**: 创建 .gitignore 文件
- [ ] ⏳ **问题 13**: 编写单元测试（目标覆盖率 80%）
- [ ] ⏳ **问题 14**: 重构复杂方法（降低代码复杂度）
- [ ] ⏳ **问题 15**: 性能优化（缓存、异步等）

---

## 📊 当前进度

**总体进度**: 1/15 = 6.7%

| 类别 | 进度 |
|------|------|
| 🔴 高优先级 | 1/5 (20%) |
| 🟡 中优先级 | 0/5 (0%) |
| 🟢 低优先级 | 0/5 (0%) |

---

## 🎯 下一步行动

**立即执行**（今天）:
1. 添加全局异常处理中间件
2. 配置数据库连接池

**本周完成**:
3. 保护敏感信息（SecretStr）
4. 配置 CORS 白名单
5. 开始处理 TODO 标记

---

## 💡 快速参考

### 安全检查命令
```bash
# 查找危险的 eval/exec 使用
grep -r "eval(" rag-scheduler/ llm-session/
grep -r "exec(" rag-scheduler/ llm-session/

# 检查明文 API Key
grep -r "OPENAI_API_KEY.*=" rag-scheduler/ llm-session/ --include="*.py"

# 检查通配符 CORS
grep -r 'allow_origins=\["\*"\]' rag-scheduler/ llm-session/
```

### 代码质量检查
```bash
# 运行 mypy 类型检查
mypy rag-scheduler/app/ llm-session/app/

# 运行 flake8 代码风格检查
flake8 rag-scheduler/app/ llm-session/app/

# 运行 pytest 测试
pytest rag-scheduler/tests/ llm-session/tests/ --cov=.
```

---

**最后更新**: 2026-05-09  
**详细文档**: 查看 [ISSUES_TRACKING.md](./ISSUES_TRACKING.md)
