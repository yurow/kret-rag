# 多平台LLM配置系统 - 更新总结

## 🎯 核心改进

将单平台配置升级为**多平台数组结构**，支持：
- ✅ 同时配置多个LLM提供商（火山引擎、OpenAI、Anthropic等）
- ✅ 按优先级自动选择提供商
- ✅ 跨平台自动降级和切换
- ✅ 统一的Token管理和监控

---

## 📊 架构对比

### **之前（单平台）**

```json
{
  "baseUrl": "...",
  "apiKey": "...",
  "api": "openai-completions",
  "models": [...]
}
```

**限制**：
- ❌ 只能配置一个提供商
- ❌ 无法跨平台降级
- ❌ 灵活性差

---

### **现在（多平台）**

```json
{
  "providers": [
    {
      "name": "火山引擎",
      "baseUrl": "...",
      "apiKey": "...",
      "priority": 1,
      "models": [...]
    },
    {
      "name": "OpenAI",
      "baseUrl": "...",
      "apiKey": "...",
      "priority": 2,
      "models": [...]
    }
  ]
}
```

**优势**：
- ✅ 支持无限个提供商
- ✅ 智能优先级管理
- ✅ 跨平台容错
- ✅ 灵活组合

---

## 🔧 主要修改

### 1. **Schema定义** ([config.py](file://g:\rag\kret-rag\llm-session\app\core\config.py))

#### 新增 `MultiProviderConfig`

```python
class MultiProviderConfig(BaseModel):
    """多提供商配置（根结构）"""
    providers: List[LLMProviderConfig]
    
    def get_sorted_providers(self) -> List[LLMProviderConfig]:
        """按优先级排序"""
        
    def get_first_available_model(self) -> Optional[tuple]:
        """获取第一个可用模型 (provider, model)"""
```

#### 更新 `LLMProviderConfig`

```python
class LLMProviderConfig(BaseModel):
    name: str              # 新增：提供商名称
    baseUrl: str
    apiKey: str
    api: str
    priority: int = 1      # 新增：优先级
    models: List[LLMModelConfig]
```

---

### 2. **配置管理器** ([llm_config_manager.py](file://g:\rag\kret-rag\llm-session\app\core\llm_config_manager.py))

#### 新增字段

```python
class LLMConfigManager:
    multi_provider_config: Optional[MultiProviderConfig]  # 新增
    current_provider: Optional[LLMProviderConfig]         # 新增
    current_model: Optional[LLMModelConfig]
```

#### 增强切换逻辑

```python
def switch_to_next_model(self) -> bool:
    """
    两级切换策略：
    1. 先尝试当前提供商的下一个模型
    2. 如果当前提供商没有可用模型，切换到下一个提供商
    """
```

#### 新增方法

```python
def get_current_provider() -> Optional[LLMProviderConfig]
def get_all_providers_info() -> list
```

---

### 3. **LLM服务** ([llm_service.py](file://g:\rag\kret-rag\llm-session\app\services\llm_service.py))

#### 更新方法签名

```python
async def _call_openai_compatible(
    self,
    messages: List[Dict[str, str]],
    provider: Any,      # 新增：提供商信息
    model: Any,
    temperature: float,
    max_tokens: int,
    timeout: int
) -> str:
```

#### 增强错误处理

```python
# 失败时自动切换提供商
if self.config_manager.switch_to_next_model():
    next_model = self.config_manager.get_current_model()
    next_provider = self.config_manager.get_current_provider()
    # 重试...
```

---

### 4. **配置文件示例** ([llm_models.json.example](file://g:\rag\kret-rag\llm-session\config\llm_models.json.example))

提供完整的多平台示例：
- 火山引擎（优先级1）
- OpenAI（优先级2）
- Anthropic（优先级3）

---

## 🚀 使用流程

### **启动时**

```
加载所有提供商配置
  ↓
按 priority 排序
  ↓
选择第一个可用模型
  ↓
记录：[提供商名称] 模型名称
```

---

### **调用时**

```
获取当前提供商和模型
  ↓
根据 provider.api 选择调用方式
  ├─ openai-completions → 调用OpenAI兼容API
  └─ anthropic-messages → 调用Anthropic API
  ↓
成功 → 返回结果
  ↓
失败 → 切换模型/提供商 → 重试
```

---

## 💡 关键特性

### 1. **智能优先级**

```json
"providers": [
  {"name": "国内便宜", "priority": 1},   // 优先使用
  {"name": "国际稳定", "priority": 2},   // 备选
  {"name": "兜底方案", "priority": 3}    // 最后手段
]
```

---

### 2. **跨平台切换**

```
火山引擎超限
  ↓
自动切换到 OpenAI
  ↓
OpenAI也超限
  ↓
自动切换到 Anthropic
```

---

### 3. **混合API协议**

```json
"providers": [
  {"api": "openai-completions"},     // OpenAI兼容
  {"api": "anthropic-messages"}      // Anthropic原生
]
```

系统自动识别并调用正确的API格式。

---

## 📈 实际应用场景

### 场景1：成本控制

```json
{
  "providers": [
    {
      "name": "免费模型",
      "priority": 1,
      "models": [{"dailyTokenLimit": 5000000}]
    },
    {
      "name": "付费模型",
      "priority": 2,
      "models": [{"dailyTokenLimit": 100000}]
    }
  ]
}
```

**效果**：优先使用免费额度，用完才付费。

---

### 场景2：高可用性

```json
{
  "providers": [
    {"name": "主平台A", "priority": 1},
    {"name": "备用平台B", "priority": 2},
    {"name": "应急平台C", "priority": 3}
  ]
}
```

**效果**：即使某个平台完全宕机，服务仍可用。

---

### 场景3：功能互补

```json
{
  "providers": [
    {
      "name": "推理专用",
      "models": [{"reasoning": true}]
    },
    {
      "name": "通用对话",
      "models": [{"reasoning": false}]
    }
  ]
}
```

---

## 🎯 API变更

### `/config/models` 返回格式

**之前**：
```json
{
  "currentModel": {...},
  "models": [...]
}
```

**现在**：
```json
{
  "currentProvider": {
    "name": "火山引擎",
    "api": "openai-completions"
  },
  "currentModel": {...},
  "providers": [
    {
      "name": "火山引擎",
      "priority": 1,
      "models": [...]
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

## 📚 相关文档

| 文档 | 说明 |
|------|------|
| [`docs/MULTI_PROVIDER_CONFIG_GUIDE.md`](file://g:\rag\kret-rag\llm-session\docs\MULTI_PROVIDER_CONFIG_GUIDE.md) | ⭐ 多平台配置详细指南 |
| [[config/llm_models.json.example](file://g:\rag\kret-rag\llm-session\config\llm_models.json.example)](file://g:\rag\kret-rag\llm-session\config\llm_models.json.example) | 多平台配置示例 |
| [`docs/LLM_MODEL_CONFIG_GUIDE.md`](file://g:\rag\kret-rag\llm-session\docs\LLM_MODEL_CONFIG_GUIDE.md) | 基础配置指南 |

---

## ✅ 迁移指南

### 从单平台升级到多平台

#### 步骤1：备份旧配置

```bash
cp config/llm_models.json config/llm_models.json.backup
```

---

#### 步骤2：创建新格式配置

```json
{
  "providers": [
    {
      "name": "我的提供商",
      "baseUrl": "旧的baseUrl",
      "apiKey": "旧的apiKey",
      "api": "旧的api",
      "priority": 1,
      "models": [旧的models数组]
    }
  ]
}
```

---

#### 步骤3：测试

```bash
python test_llm_config.py
```

---

#### 步骤4：重启服务

```bash
uvicorn app.main:app --reload
```

---

## 🎉 总结

通过多平台配置系统，你可以：
- ✅ 灵活组合不同LLM提供商
- ✅ 智能管理成本和可用性
- ✅ 实现跨平台自动降级
- ✅ 统一监控和管理

**立即开始**：复制示例配置，添加你的多个平台信息！
