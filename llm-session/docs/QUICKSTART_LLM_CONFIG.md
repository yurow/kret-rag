# LLM动态配置快速开始

## 🚀 5分钟快速上手

### 步骤1：准备配置文件

```bash
cd llm-session
cp config/llm_models.json.example config/llm_models.json
```

---

### 步骤2：编辑配置

打开 `config/llm_models.json`，修改以下字段：

```json
{
  "baseUrl": "https://ark.cn-beijing.volces.com/api/v3",
  "apiKey": "你的实际API密钥",
  "api": "openai-completions",
  "models": [
    {
      "id": "doubao-seed-1-6-lite-251015",
      "name": "Doubao Seed 1.6 Lite",
      "enabled": true,
      "dailyTokenLimit": 1000000,
      "timeout": 60
    }
  ]
}
```

**必填字段**：
- ✅ `baseUrl`: API地址
- ✅ `apiKey`: 你的API密钥
- ✅ `models`: 至少一个启用的模型

---

### 步骤3：运行测试

```bash
python test_llm_config.py
```

**预期输出**：
```
================================================================================
LLM配置管理器测试
================================================================================

================================================================================
测试1: 配置加载
================================================================================
✅ 配置加载成功
   Base URL: https://ark.cn-beijing.volces.com/api/v3
   API协议: openai-completions
   模型数量: 1

...

================================================================================
✅ 所有测试完成！
================================================================================
```

---

### 步骤4：启动服务

```bash
uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload
```

---

### 步骤5：验证API

```bash
# 查看模型列表
curl http://localhost:9000/config/models

# 查看使用量
curl http://localhost:9000/config/usage
```

---

## 📋 常用操作

### 重新加载配置

修改配置文件后，无需重启：

```bash
curl -X POST http://localhost:9000/config/reload
```

---

### 切换模型

```bash
curl -X POST http://localhost:9000/config/switch-model
```

---

### 重置使用量

```bash
curl -X POST http://localhost:9000/config/reset-usage/doubao-seed-1-6-lite-251015
```

---

## 🎯 完整示例

### 多模型配置（自动降级）

```json
{
  "baseUrl": "https://ark.cn-beijing.volces.com/api/v3",
  "apiKey": "${VOLCES_API_KEY}",
  "api": "openai-completions",
  "models": [
    {
      "id": "doubao-pro",
      "name": "Doubao Pro（高质量）",
      "tier": "large",
      "enabled": true,
      "dailyTokenLimit": 100000,
      "maxTokens": 128000,
      "timeout": 120
    },
    {
      "id": "doubao-lite",
      "name": "Doubao Lite（标准）",
      "tier": "medium",
      "enabled": true,
      "dailyTokenLimit": 500000,
      "maxTokens": 96000,
      "timeout": 60
    },
    {
      "id": "doubao-mini",
      "name": "Doubao Mini（经济）",
      "tier": "small",
      "enabled": true,
      "dailyTokenLimit": 2000000,
      "maxTokens": 64000,
      "timeout": 30
    }
  ]
}
```

**工作流程**：
1. 优先使用 Pro 模型（高质量）
2. Pro 达到每日限制 → 自动切换到 Lite
3. Lite 也达到限制 → 切换到 Mini
4. 全部用完 → 返回错误

---

## 🔧 环境变量方式

如果不想硬编码API密钥：

### 1. 在 `.env` 文件中设置

```env
VOLCES_API_KEY=your_actual_api_key_here
```

### 2. 在配置文件中引用

```json
{
  "apiKey": "${VOLCES_API_KEY}"
}
```

### 3. 代码中替换

```python
import os
api_key = os.environ.get('VOLCES_API_KEY', config_data['apiKey'])
```

---

## 💡 最佳实践

### 1. **按优先级排序模型**

```json
"models": [
  {"id": "premium", "dailyTokenLimit": 50000},    // 最贵，质量最高
  {"id": "standard", "dailyTokenLimit": 200000},  // 中等
  {"id": "economy", "dailyTokenLimit": 1000000}   // 最便宜，保底
]
```

---

### 2. **合理设置超时**

| 模型类型 | timeout | 说明 |
|---------|---------|------|
| 小模型 | 30秒 | 响应快 |
| 中等模型 | 60秒 | 平衡 |
| 大模型 | 120秒+ | 可能需要更长时间 |

---

### 3. **监控使用量**

```bash
# 添加到crontab，每小时检查
0 * * * * curl -s http://localhost:9000/config/usage >> /var/log/llm_usage.log
```

---

## 🐛 常见问题

### Q1: 配置文件在哪里？

**A**: `llm-session/config/llm_models.json`

---

### Q2: 如何添加新模型？

**A**: 直接在JSON文件的 `models` 数组中添加即可，然后调用 `/config/reload` 重新加载。

---

### Q3: 支持哪些API协议？

**A**: 
- `openai-completions` - OpenAI兼容API
- `anthropic-messages` - Anthropic Claude API

---

### Q4: 如何禁用某个模型？

**A**: 设置 `"enabled": false`

```json
{
  "id": "old-model",
  "enabled": false
}
```

---

### Q5: Token使用量存储在哪里？

**A**: `llm-session/data/model_usage.json`

---

## 📚 更多信息

- 📖 [完整配置指南](LLM_MODEL_CONFIG_GUIDE.md)
- 📊 [实现总结](LLM_CONFIG_IMPLEMENTATION_SUMMARY.md)
- 🧪 [测试脚本](../test_llm_config.py)

---

**祝你使用愉快！** 🎉
