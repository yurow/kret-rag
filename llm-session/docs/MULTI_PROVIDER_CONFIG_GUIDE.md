# 多平台LLM配置指南

## 🎯 概述

本系统支持**多个LLM提供商平台**的配置，可以灵活组合不同平台的模型，实现：
- ✅ 跨平台自动降级（如：火山引擎 → OpenAI → Anthropic）
- ✅ 按优先级选择提供商
- ✅ 每个提供商独立管理多个模型
- ✅ 统一的Token使用量跟踪

---

## 📁 配置文件结构

### 位置
```
llm-session/config/llm_models.json
```

### 完整示例（多平台）

```json
{
  "providers": [
    {
      "name": "火山引擎-豆包",
      "baseUrl": "https://ark.cn-beijing.volces.com/api/v3",
      "apiKey": "${VOLCES_API_KEY}",
      "api": "openai-completions",
      "priority": 1,
      "models": [
        {
          "id": "doubao-seed-1-6-lite-251015",
          "name": "Doubao Seed 1.6 Lite",
          "tier": "small",
          "enabled": true,
          "reasoning": false,
          "input": ["text", "image"],
          "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0},
          "contextWindow": 128000,
          "maxTokens": 96000,
          "dailyTokenLimit": 1000000,
          "timeout": 60
        }
      ]
    },
    {
      "name": "OpenAI",
      "baseUrl": "https://api.openai.com/v1",
      "apiKey": "${OPENAI_API_KEY}",
      "api": "openai-completions",
      "priority": 2,
      "models": [
        {
          "id": "gpt-4o-mini",
          "name": "GPT-4o Mini",
          "tier": "medium",
          "enabled": true,
          "reasoning": false,
          "input": ["text", "image"],
          "cost": {"input": 0.00015, "output": 0.0006, "cacheRead": 0, "cacheWrite": 0},
          "contextWindow": 128000,
          "maxTokens": 16384,
          "dailyTokenLimit": 100000,
          "timeout": 60
        }
      ]
    },
    {
      "name": "Anthropic Claude",
      "baseUrl": "https://api.anthropic.com",
      "apiKey": "${ANTHROPIC_API_KEY}",
      "api": "anthropic-messages",
      "priority": 3,
      "models": [
        {
          "id": "claude-3-haiku-20240307",
          "name": "Claude 3 Haiku",
          "tier": "small",
          "enabled": true,
          "reasoning": false,
          "input": ["text", "image"],
          "cost": {"input": 0.00025, "output": 0.00125, "cacheRead": 0, "cacheWrite": 0},
          "contextWindow": 200000,
          "maxTokens": 4096,
          "dailyTokenLimit": 200000,
          "timeout": 60
        }
      ]
    }
  ]
}
```

---

## 🔧 配置字段说明

### 根结构

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `providers` | array | ✅ | 提供商列表（数组） |

---

### 提供商配置 (Provider)

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `name` | string | ✅ | - | 提供商名称（用于显示和日志） |
| `baseUrl` | string | ✅ | - | API基础URL |
| `apiKey` | string | ✅ | - | API密钥（支持环境变量） |
| `api` | string | ✅ | - | API协议：`openai-completions` 或 `anthropic-messages` |
| `priority` | int | ❌ | `1` | 优先级（数字越小优先级越高） |
| `models` | array | ✅ | - | 该提供商下的模型列表 |

---

### 模型配置 (Model)

与单平台版本相同，见下表：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `id` | string | ✅ | - | 模型唯一标识符 |
| `name` | string | ✅ | - | 模型显示名称 |
| `tier` | string | ❌ | `"small"` | 模型层级 |
| `enabled` | boolean | ❌ | `true` | 是否启用 |
| `reasoning` | boolean | ❌ | `false` | 是否支持深度思考 |
| `input` | array | ❌ | `["text"]` | 支持的输入类型 |
| `cost` | object | ❌ | 见下方 | 成本配置 |
| `contextWindow` | int | ❌ | `128000` | 上下文窗口大小 |
| `maxTokens` | int | ❌ | `96000` | 最大输出token数 |
| `dailyTokenLimit` | int | ❌ | `1000000` | 每日Token限制 |
| `timeout` | int | ❌ | `60` | 超时时间（秒） |

---

## 🚀 工作流程

### **启动时选择模型**

```
加载所有提供商配置
  ↓
按 priority 排序（1, 2, 3...）
  ↓
从优先级最高的提供商开始检查
  ↓
找到第一个启用的、未超限的模型
  ↓
设置为当前模型
```

---

### **调用失败时的切换策略**

```
API调用失败
  ↓
尝试当前提供商的下一个模型
  ├─ 成功 → 继续
  └─ 失败 → 切换到下一个提供商
              ↓
         从下一个提供商中选择第一个可用模型
              ├─ 成功 → 继续
              └─ 失败 → 返回错误
```

---

## 💡 最佳实践

### 1. **按成本和可靠性设置优先级**

```json
"providers": [
  {
    "name": "国内优先（低成本）",
    "priority": 1,
    "models": [...]
  },
  {
    "name": "国际备选（高成本）",
    "priority": 2,
    "models": [...]
  },
  {
    "name": "兜底方案",
    "priority": 3,
    "models": [...]
  }
]
```

---

### 2. **混合不同API协议**

```json
"providers": [
  {
    "name": "火山引擎",
    "api": "openai-completions",  // OpenAI兼容
    "priority": 1
  },
  {
    "name": "Anthropic",
    "api": "anthropic-messages",  // Anthropic原生
    "priority": 2
  }
]
```

系统会自动根据 `api` 字段选择正确的调用方式。

---

### 3. **为每个提供商设置合理的限额**

```json
{
  "name": "火山引擎",
  "models": [
    {
      "id": "doubao-lite",
      "dailyTokenLimit": 1000000  // 高限额，作为主力
    }
  ]
},
{
  "name": "OpenAI",
  "models": [
    {
      "id": "gpt-4o-mini",
      "dailyTokenLimit": 100000   // 低限额，作为备选
    }
  ]
}
```

---

### 4. **环境变量管理多个API密钥**

在 `.env` 文件中：

```env
VOLCES_API_KEY=your_volces_key
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
```

在配置文件中引用：

```json
{
  "providers": [
    {
      "name": "火山引擎",
      "apiKey": "${VOLCES_API_KEY}"
    },
    {
      "name": "OpenAI",
      "apiKey": "${OPENAI_API_KEY}"
    }
  ]
}
```

---

## 📊 实际应用场景

### 场景1：成本优化

**目标**：优先使用便宜的国内模型，超限时自动切换到国际模型。

```json
{
  "providers": [
    {
      "name": "火山引擎（便宜）",
      "priority": 1,
      "models": [
        {
          "id": "doubao-lite",
          "dailyTokenLimit": 2000000,
          "cost": {"input": 0, "output": 0}
        }
      ]
    },
    {
      "name": "OpenAI（贵但稳定）",
      "priority": 2,
      "models": [
        {
          "id": "gpt-4o-mini",
          "dailyTokenLimit": 100000,
          "cost": {"input": 0.00015, "output": 0.0006}
        }
      ]
    }
  ]
}
```

---

### 场景2：高可用性

**目标**：多个平台互为备份，确保服务不中断。

```json
{
  "providers": [
    {"name": "平台A", "priority": 1, ...},
    {"name": "平台B", "priority": 2, ...},
    {"name": "平台C", "priority": 3, ...}
  ]
}
```

即使某个平台完全不可用，系统会自动切换到下一个平台。

---

### 场景3：功能互补

**目标**：某些任务需要特定模型的能力。

```json
{
  "providers": [
    {
      "name": "擅长推理",
      "priority": 1,
      "models": [
        {"id": "model-with-reasoning", "reasoning": true}
      ]
    },
    {
      "name": "通用模型",
      "priority": 2,
      "models": [
        {"id": "general-model", "reasoning": false}
      ]
    }
  ]
}
```

---

## 🔍 监控和管理

### 查看所有提供商状态

```bash
curl http://localhost:9000/config/models
```

**返回示例**：

```json
{
  "currentProvider": {
    "name": "火山引擎-豆包",
    "api": "openai-completions"
  },
  "currentModel": {
    "id": "doubao-seed-1-6-lite-251015",
    "name": "Doubao Seed 1.6 Lite"
  },
  "providers": [
    {
      "name": "火山引擎-豆包",
      "baseUrl": "https://ark.cn-beijing.volces.com/api/v3",
      "api": "openai-completions",
      "priority": 1,
      "models": [
        {
          "id": "doubao-seed-1-6-lite-251015",
          "name": "Doubao Seed 1.6 Lite",
          "enabled": true,
          "canUse": true,
          "usedTokensToday": 12345,
          "dailyLimit": 1000000,
          "isCurrent": true
        }
      ]
    },
    {
      "name": "OpenAI",
      "priority": 2,
      "models": [...]
    }
  ]
}
```

---

### 手动切换提供商

```bash
# 切换到下一个可用模型（可能跨越提供商）
curl -X POST http://localhost:9000/config/switch-model
```

---

## 🐛 常见问题

### Q1: 如何禁用某个提供商？

**A**: 将该提供商下所有模型的 `enabled` 设为 `false`，或删除该提供商。

---

### Q2: 优先级相同的处理？

**A**: 如果多个提供商优先级相同，按配置文件中的顺序选择。

---

### Q3: 所有提供商都不可用怎么办？

**A**: 系统会返回错误："没有可用的LLM模型"。建议至少保留一个高限额的兜底提供商。

---

### Q4: 如何查看哪个提供商正在使用？

**A**: 调用 `/config/models` API，查看 `currentProvider` 字段。

---

## 📚 相关文档

- [单平台配置指南](LLM_MODEL_CONFIG_GUIDE.md)
- [实现总结](LLM_CONFIG_IMPLEMENTATION_SUMMARY.md)
- [快速开始](QUICKSTART_LLM_CONFIG.md)

---

**祝你使用愉快！** 🎉
