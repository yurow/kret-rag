# max_tokens参数验证修复

## 🐛 问题描述

调用LLM API时出现错误：

```json
{
  "error": {
    "code": "InvalidParameter",
    "message": "The parameter `max_tokens` specified in the request are not valid: integer above maximum value, expected a value <= 131072, but got 256000 instead."
  }
}
```

**原因**：
- 配置文件中 [maxTokens](file://g:\rag\kret-rag\llm-session\app\core\config.py#L29-L29) 设置为 256000
- 但API实际只支持最大 131072
- 代码直接使用该值发送请求，未做验证

---

## ✅ 修复方案

### 1. **代码层防护** - 自动限制max_tokens

在发送请求前验证并限制 [max_tokens](file://g:\rag\kret-rag\llm-session\app\core\config.py#L29-L29) 值：

#### OpenAI兼容API

```python
async def _call_openai_compatible(...):
    # 验证并限制max_tokens在模型支持范围内
    actual_max_tokens = min(max_tokens, model.maxTokens)
    if actual_max_tokens != max_tokens:
        logger.warning(
            f"max_tokens超出模型限制: 请求={max_tokens}, "
            f"模型上限={model.maxTokens}, 调整为={actual_max_tokens}"
        )
    
    request_data = {
        "model": model.id,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": actual_max_tokens  # 使用限制后的值
    }
```

#### Anthropic API

```python
async def _call_anthropic(...):
    # 同样的验证逻辑
    actual_max_tokens = min(max_tokens, model.maxTokens)
    
    request_data = {
        "model": model.id,
        "messages": user_messages,
        "max_tokens": actual_max_tokens,  # 使用限制后的值
        "temperature": temperature
    }
```

---

### 2. **配置文件修正** - 更新示例值

修正 [llm_models.json.example](file://g:\rag\kret-rag\llm-session\config\llm_models.json.example) 中的不合理值：

**修改前**：
```json
{
  "id": "doubao-seed-1-6-pro-251015",
  "maxTokens": 128000  // ❌ 可能超过某些API的限制
}
```

**修改后**：
```json
{
  "id": "doubao-seed-1-6-pro-251015",
  "maxTokens": 131072  // ✅ 符合API最大限制
}
```

---

## 📊 常见模型的max_tokens限制

| 模型提供商 | 模型 | contextWindow | maxTokens上限 | 推荐配置 |
|-----------|------|---------------|--------------|---------|
| **火山引擎** | Doubao Lite | 128000 | 96000 | 96000 |
| **火山引擎** | Doubao Pro | 256000 | 131072 | 131072 |
| **OpenAI** | GPT-4o Mini | 128000 | 16384 | 16384 |
| **OpenAI** | GPT-4o | 128000 | 16384 | 16384 |
| **Anthropic** | Claude 3 Haiku | 200000 | 4096 | 4096 |
| **Anthropic** | Claude 3 Sonnet | 200000 | 4096 | 4096 |

**注意**：
- `maxTokens` 必须 ≤ API实际支持的最大值
- 通常 `maxTokens` < `contextWindow`
- 建议查阅各平台官方文档获取准确限制

---

## 🔍 工作原理

### **双层保护机制**

```
用户请求 (max_tokens=256000)
  ↓
代码验证: min(256000, model.maxTokens)
  ↓
如果 model.maxTokens=131072
  → 实际发送: max_tokens=131072 ✅
  → 记录警告日志
  
如果 model.maxTokens=256000
  → 实际发送: max_tokens=256000 ✅
  → 无警告
```

---

### **优势**

1. **容错性** - 即使配置错误也不会导致API调用失败
2. **透明性** - 通过日志告知用户参数被调整
3. **灵活性** - 允许配置较大的值，运行时自动适配
4. **兼容性** - 支持不同API的不同限制

---

## 💡 最佳实践

### 1. **配置前查阅官方文档**

在设置 [maxTokens](file://g:\rag\kret-rag\llm-session\app\core\config.py#L29-L29) 前，务必查阅对应平台的API文档：

- **火山引擎**: https://www.volcengine.com/docs/...
- **OpenAI**: https://platform.openai.com/docs/models
- **Anthropic**: https://docs.anthropic.com/claude/docs/models-overview

---

### 2. **保守配置原则**

```json
{
  "contextWindow": 256000,  // 上下文窗口可以大
  "maxTokens": 100000       // 但maxTokens要保守（留有余量）
}
```

**理由**：
- 避免触及API边界
- 为未来API变更留出缓冲
- 减少意外错误

---

### 3. **分层设置策略**

```json
"models": [
  {
    "id": "fast-model",
    "maxTokens": 8000,      // 快速响应，小输出
    "timeout": 30
  },
  {
    "id": "balanced-model",
    "maxTokens": 32000,     // 平衡性能和成本
    "timeout": 60
  },
  {
    "id": "powerful-model",
    "maxTokens": 131072,    // 最大能力，长文本
    "timeout": 120
  }
]
```

---

## 🧪 测试验证

### 1. **运行测试脚本**

```bash
cd llm-session
python test_llm_config.py
```

确认配置加载正常。

---

### 2. **发送测试请求**

```bash
curl -X POST http://localhost:9000/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "请写一篇长文章",
    "max_tokens": 200000
  }'
```

**预期行为**：
- ✅ 不会报400错误
- ✅ 日志中显示警告："max_tokens超出模型限制，调整为XXX"
- ✅ 实际使用模型支持的最大值

---

### 3. **检查日志**

查看服务日志，应该看到类似信息：

```
WARNING: max_tokens超出模型限制: 请求=200000, 模型上限=131072, 调整为=131072
INFO: 调用LLM API: [火山引擎-豆包] Doubao Seed 1.6 Pro
```

---

## 📚 相关文件

| 文件 | 修改内容 |
|------|---------|
| [[llm_service.py](file://g:\rag\kret-rag\llm-session\app\services\llm_service.py)] | 添加max_tokens验证逻辑（2处） |
| [[llm_models.json.example](file://g:\rag\kret-rag\llm-session\config\llm_models.json.example)] | 修正示例配置中的maxTokens值 |

---

## 🎯 总结

通过这次修复：
- ✅ **代码层面**：添加了自动验证和限制机制
- ✅ **配置层面**：更新了示例文件的合理值
- ✅ **用户体验**：即使配置错误也能正常工作
- ✅ **可观测性**：通过日志清晰展示参数调整

**核心原则**：**防御性编程** - 不要信任配置，始终在运行时验证！
