# LLM模型配置指南

## 📋 概述

本系统支持**动态LLM模型配置**，可以从JSON文件加载多个模型配置，并自动管理Token使用量和模型切换。

---

## 🎯 核心特性

### 1. **多模型支持**
- 支持配置多个LLM模型
- 自动选择可用模型
- 超过限制时自动切换

### 2. **多协议支持**
- ✅ OpenAI兼容API（`openai-completions`）
- ✅ Anthropic API（`anthropic-messages`）
- 可扩展其他协议

### 3. **智能限流**
- 每日Token限制
- 自动跟踪使用量
- 超限自动切换模型

### 4. **动态配置**
- 无需重启服务
- 热重载配置文件
- 实时查看使用统计

---

## 📁 配置文件结构

### 位置
```
llm-session/config/llm_models.json
```

### 完整示例

```json
{
  "baseUrl": "https://ark.cn-beijing.volces.com/api/v3",
  "apiKey": "${apiKey}",
  "api": "openai-completions",
  "models": [
    {
      "id": "doubao-seed-1-6-lite-251015",
      "name": "Doubao Seed 1.6 Lite",
      "tier": "small",
      "enabled": true,
      "api": "openai-completions",
      "reasoning": false,
      "input": ["text", "image"],
      "cost": {
        "input": 0,
        "output": 0,
        "cacheRead": 0,
        "cacheWrite": 0
      },
      "contextWindow": 128000,
      "maxTokens": 96000,
      "dailyTokenLimit": 1000000,
      "timeout": 60
    },
    {
      "id": "doubao-seed-1-6-pro-251015",
      "name": "Doubao Seed 1.6 Pro",
      "tier": "large",
      "enabled": true,
      "api": "openai-completions",
      "reasoning": true,
      "input": ["text", "image"],
      "cost": {
        "input": 0.008,
        "output": 0.02,
        "cacheRead": 0.004,
        "cacheWrite": 0.008
      },
      "contextWindow": 256000,
      "maxTokens": 128000,
      "dailyTokenLimit": 500000,
      "timeout": 120
    }
  ]
}
```

---

## 🔧 配置字段说明

### 顶层配置

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `baseUrl` | string | ✅ | API基础URL |
| `apiKey` | string | ✅ | API密钥（支持环境变量替换） |
| `api` | string | ✅ | API协议：`openai-completions` 或 `anthropic-messages` |
| `models` | array | ✅ | 模型列表 |

---

### 模型配置

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `id` | string | ✅ | - | 模型唯一标识符 |
| `name` | string | ✅ | - | 模型显示名称 |
| `tier` | string | ❌ | `"small"` | 模型层级：`small`, `medium`, `large` |
| `enabled` | boolean | ❌ | `true` | 是否启用该模型 |
| `api` | string | ❌ | `"openai-completions"` | 模型使用的API协议 |
| `reasoning` | boolean | ❌ | `false` | 是否支持深度思考 |
| `input` | array | ❌ | `["text"]` | 支持的输入类型：`text`, `image`, `audio` |
| `cost` | object | ❌ | 见下方 | 成本配置 |
| `contextWindow` | int | ❌ | `128000` | 上下文窗口大小 |
| `maxTokens` | int | ❌ | `96000` | 最大输出token数 |
| `dailyTokenLimit` | int | ❌ | `1000000` | 每日Token限制 |
| `timeout` | int | ❌ | `60` | 超时时间（秒） |

---

### Cost配置

```json
"cost": {
  "input": 0.001,      // 输入token成本（每1K tokens）
  "output": 0.002,     // 输出token成本
  "cacheRead": 0.0005, // 缓存读取成本
  "cacheWrite": 0.001  // 缓存写入成本
}
```

---

## 🚀 使用流程

### 1. **首次配置**

#### 步骤1：复制示例配置

```bash
cd llm-session
cp config/llm_models.json.example config/llm_models.json
```

#### 步骤2：编辑配置

```bash
nano config/llm_models.json
```

修改以下字段：
- `baseUrl`: 你的API地址
- `apiKey`: 你的API密钥
- `models`: 添加你的模型配置

---

### 2. **启动服务**

```bash
cd llm-session
uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload
```

服务启动时会自动：
- 加载配置文件
- 选择第一个可用的模型
- 初始化使用量跟踪器

---

### 3. **查看配置状态**

#### API方式

```bash
# 查看所有模型
curl http://localhost:9000/config/models

# 查看使用量统计
curl http://localhost:9000/config/usage
```

#### 返回示例

```json
{
  "provider": {
    "baseUrl": "https://ark.cn-beijing.volces.com/api/v3",
    "api": "openai-completions"
  },
  "currentModel": {
    "id": "doubao-seed-1-6-lite-251015",
    "name": "Doubao Seed 1.6 Lite"
  },
  "models": [
    {
      "id": "doubao-seed-1-6-lite-251015",
      "name": "Doubao Seed 1.6 Lite",
      "tier": "small",
      "enabled": true,
      "canUse": true,
      "isCurrent": true,
      "usedTokensToday": 12345,
      "dailyTokenLimit": 1000000
    }
  ]
}
```

---

### 4. **动态更新配置**

修改配置文件后，无需重启服务：

```bash
# 重新加载配置
curl -X POST http://localhost:9000/config/reload
```

---

### 5. **手动切换模型**

```bash
# 切换到下一个可用模型
curl -X POST http://localhost:9000/config/switch-model
```

---

## 📊 Token使用量管理

### 自动跟踪

系统会自动：
- 记录每次调用的Token使用量
- 累计到每日计数器
- 检查是否超过限制

### 超限处理

当模型达到 `dailyTokenLimit` 时：
1. 记录警告日志
2. 自动切换到下一个可用模型
3. 如果没有可用模型，返回错误

### 重置使用量

```bash
# 重置指定模型的每日使用量
curl -X POST http://localhost:9000/config/reset-usage/doubao-seed-1-6-lite-251015
```

---

## 🔌 API协议支持

### OpenAI兼容API

**配置**：
```json
{
  "api": "openai-completions",
  "baseUrl": "https://api.openai.com/v1"
}
```

**端点**：`{baseUrl}/chat/completions`

**请求格式**：
```json
{
  "model": "gpt-3.5-turbo",
  "messages": [...],
  "temperature": 0.7,
  "max_tokens": 4096
}
```

---

### Anthropic API

**配置**：
```json
{
  "api": "anthropic-messages",
  "baseUrl": "https://api.anthropic.com"
}
```

**端点**：`{baseUrl}/v1/messages`

**请求格式**：
```json
{
  "model": "claude-3-opus-20240229",
  "messages": [...],
  "system": "...",
  "max_tokens": 4096,
  "temperature": 0.7
}
```

---

## 💡 最佳实践

### 1. **模型排序策略**

按优先级从高到低排列模型：

```json
"models": [
  {"id": "premium-model", "dailyTokenLimit": 100000},  // 高质量，低限额
  {"id": "standard-model", "dailyTokenLimit": 500000}, // 中等质量，中限额
  {"id": "economy-model", "dailyTokenLimit": 1000000}  // 基础质量，高限额
]
```

---

### 2. **合理设置限额**

根据预算和使用场景设置：

| 场景 | dailyTokenLimit | 说明 |
|------|----------------|------|
| **开发测试** | 100,000 | 较低限额，避免浪费 |
| **生产环境-低频** | 500,000 | 中等限额 |
| **生产环境-高频** | 2,000,000+ | 高限额，确保可用性 |

---

### 3. **监控使用量**

定期检查使用统计：

```bash
# 每小时检查一次
watch -n 3600 'curl -s http://localhost:9000/config/usage | jq'
```

---

### 4. **环境变量管理API密钥**

不要硬编码API密钥：

```json
{
  "apiKey": "${VOLCES_API_KEY}"
}
```

在 `.env` 文件中设置：
```env
VOLCES_API_KEY=your_actual_api_key_here
```

---

## 🐛 故障排查

### 问题1：配置文件未找到

**症状**：
```
WARNING: 配置文件不存在: ./config/llm_models.json
```

**解决**：
```bash
cp config/llm_models.json.example config/llm_models.json
```

---

### 问题2：没有可用模型

**症状**：
```
WARNING: 没有可用的模型
```

**原因**：
- 所有模型都被禁用（`enabled: false`）
- 所有模型都达到了每日限制

**解决**：
1. 检查模型配置中的 `enabled` 字段
2. 重置使用量或增加 `dailyTokenLimit`

---

### 问题3：API调用失败

**症状**：
```
ERROR: 调用LLM API失败: ...
```

**排查步骤**：
1. 检查 `baseUrl` 是否正确
2. 检查 `apiKey` 是否有效
3. 检查网络连接
4. 查看详细错误日志

---

## 📚 相关API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/config/models` | GET | 获取所有模型列表 |
| `/config/usage` | GET | 获取使用量统计 |
| `/config/reload` | POST | 重新加载配置 |
| `/config/switch-model` | POST | 切换到下一个模型 |
| `/config/reset-usage/{model_id}` | POST | 重置使用量 |

---

## 🎯 总结

通过动态LLM配置系统，你可以：
- ✅ 灵活配置多个模型
- ✅ 自动管理Token使用量
- ✅ 智能切换模型避免超限
- ✅ 无需重启即可更新配置
- ✅ 实时监控使用统计

**立即开始**：
1. 复制示例配置
2. 修改为你的API信息
3. 启动服务
4. 享受智能的模型管理！
