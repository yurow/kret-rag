# 动态LLM配置系统实现总结

## 🎯 实现目标

实现一个**灵活、智能的LLM模型配置系统**，支持：
- ✅ 从JSON文件动态加载配置
- ✅ 支持多种API协议（OpenAI、Anthropic）
- ✅ 自动跟踪Token使用量
- ✅ 超过限制时自动切换模型
- ✅ 无需重启即可更新配置

---

## 📁 文件结构

```
llm-session/
├── app/
│   ├── core/
│   │   ├── config.py                    # 配置定义（新增LLM模型Schema）
│   │   └── llm_config_manager.py        # ⭐ 配置管理器（新建）
│   ├── services/
│   │   └── llm_service.py               # ⭐ LLM服务（重写）
│   ├── routes/
│   │   ├── chat.py                      # 聊天路由
│   │   ├── sessions.py                  # 会话路由
│   │   └── llm_config.py                # ⭐ 配置管理路由（新建）
│   └── main.py                          # 主应用（注册新路由）
├── config/
│   └── llm_models.json.example          # ⭐ 配置示例（新建）
├── docs/
│   └── LLM_MODEL_CONFIG_GUIDE.md        # ⭐ 配置指南（新建）
├── test_llm_config.py                   # ⭐ 测试脚本（新建）
└── .env.example                         # 环境变量示例（更新）
```

---

## 🔧 核心组件

### 1. **配置Schema** ([config.py](file://g:\rag\kret-rag\llm-session\app\core\config.py))

```python
class ModelCostConfig(BaseModel):
    """模型成本配置"""
    input: float = 0.0
    output: float = 0.0
    cacheRead: float = 0.0
    cacheWrite: float = 0.0

class LLMModelConfig(BaseModel):
    """单个LLM模型配置"""
    id: str
    name: str
    tier: str = "small"
    enabled: bool = True
    api: str = "openai-completions"
    reasoning: bool = False
    input: List[str] = ["text"]
    cost: ModelCostConfig
    contextWindow: int = 128000
    maxTokens: int = 96000
    dailyTokenLimit: int = 1000000
    timeout: int = 60
    
    # 运行时状态
    used_tokens_today: int = 0
    
    def can_use(self) -> bool:
        """检查模型是否可用"""
        
    def record_usage(self, tokens: int):
        """记录token使用"""

class LLMProviderConfig(BaseModel):
    """LLM提供商配置"""
    baseUrl: str
    apiKey: str
    api: str
    models: List[LLMModelConfig]
```

---

### 2. **配置管理器** ([llm_config_manager.py](file://g:\rag\kret-rag\llm-session\app\core\llm_config_manager.py))

**核心功能**：
- 从JSON文件加载配置
- 选择可用模型
- 跟踪Token使用量
- 自动切换模型
- 支持热重载

**关键方法**：
```python
class LLMConfigManager:
    def _load_config()           # 加载配置
    def get_current_model()      # 获取当前模型
    def switch_to_next_model()   # 切换模型
    def record_token_usage()     # 记录使用量
    def reload_config()          # 重新加载
    def get_api_endpoint()       # 获取API端点
    def get_headers()            # 获取请求头
```

---

### 3. **LLM服务** ([llm_service.py](file://g:\rag\kret-rag\llm-session\app\services\llm_service.py))

**重写要点**：
- 使用配置管理器获取模型信息
- 支持OpenAI和Anthropic两种协议
- 自动记录Token使用
- 失败时自动切换模型重试

**核心流程**：
```
1. 获取当前可用模型
2. 根据API协议构建请求
3. 调用API
4. 记录Token使用
5. 如果失败 → 切换模型 → 重试
```

---

### 4. **配置管理API** ([llm_config.py](file://g:\rag\kret-rag\llm-session\app\routes\llm_config.py))

**提供的端点**：

| 端点 | 方法 | 功能 |
|------|------|------|
| `/config/models` | GET | 获取所有模型列表 |
| `/config/usage` | GET | 获取使用量统计 |
| `/config/reload` | POST | 重新加载配置 |
| `/config/switch-model` | POST | 切换模型 |
| `/config/reset-usage/{model_id}` | POST | 重置使用量 |

---

## 📊 工作流程

### **启动流程**

```
服务启动
  ↓
加载 config/llm_models.json
  ↓
验证配置有效性
  ↓
选择第一个可用模型
  ↓
初始化使用量跟踪器
  ↓
记录日志：当前使用的模型
```

---

### **调用流程**

```
用户请求
  ↓
获取当前模型
  ↓
构建API请求（根据协议）
  ↓
调用LLM API
  ↓
成功？
  ├─ 是 → 记录Token使用 → 返回结果
  └─ 否 → 切换到下一个模型 → 重试
              ↓
          还有可用模型？
              ├─ 是 → 重试
              └─ 否 → 返回错误
```

---

### **限流流程**

```
每次调用后
  ↓
累加 used_tokens_today
  ↓
检查是否 >= dailyTokenLimit
  ↓
超限？
  ├─ 是 → 记录警告 → 自动切换模型
  └─ 否 → 继续
```

---

## 💡 关键特性

### 1. **多协议支持**

**OpenAI兼容**：
```python
if provider_config.api == "openai-completions":
    endpoint = f"{base_url}/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
```

**Anthropic**：
```python
elif provider_config.api == "anthropic-messages":
    endpoint = f"{base_url}/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    }
```

---

### 2. **智能模型切换**

```python
def switch_to_next_model(self, current_model_id: str):
    """找到当前模型的下一个可用模型"""
    found_current = False
    for model in self.models:
        if found_current and model.can_use():
            return model
        if model.id == current_model_id:
            found_current = True
    return None
```

---

### 3. **持久化使用量跟踪**

```python
class ModelUsageTracker:
    def _load_usage_data():
        # 从 data/model_usage.json 加载
        
    def _save_usage_data():
        # 保存到 data/model_usage.json
        
    def get_today_usage(model_id):
        # 检查日期，如果是新的一天则重置
```

---

## 🚀 使用示例

### **配置文件**

```json
{
  "baseUrl": "https://ark.cn-beijing.volces.com/api/v3",
  "apiKey": "${VOLCES_API_KEY}",
  "api": "openai-completions",
  "models": [
    {
      "id": "doubao-seed-1-6-lite",
      "name": "Doubao Seed 1.6 Lite",
      "enabled": true,
      "dailyTokenLimit": 1000000,
      "timeout": 60
    },
    {
      "id": "doubao-seed-1-6-pro",
      "name": "Doubao Seed 1.6 Pro",
      "enabled": true,
      "dailyTokenLimit": 500000,
      "timeout": 120
    }
  ]
}
```

---

### **API调用**

```bash
# 查看模型列表
curl http://localhost:9000/config/models

# 查看使用量
curl http://localhost:9000/config/usage

# 重新加载配置
curl -X POST http://localhost:9000/config/reload

# 切换模型
curl -X POST http://localhost:9000/config/switch-model
```

---

## 📈 优势对比

| 特性 | 旧方案 | 新方案 |
|------|--------|--------|
| **配置方式** | 硬编码在.env | JSON文件，灵活配置 |
| **多模型支持** | ❌ 单一模型 | ✅ 多个模型 |
| **自动切换** | ❌ 不支持 | ✅ 超限自动切换 |
| **使用量跟踪** | ❌ 无 | ✅ 自动跟踪 |
| **热重载** | ❌ 需重启 | ✅ 无需重启 |
| **多协议** | ❌ 仅OpenAI | ✅ OpenAI + Anthropic |
| **实时监控** | ❌ 无 | ✅ API查询 |

---

## 🎯 下一步优化建议

### 1. **流式响应支持**
- 实现真正的流式API调用
- 实时返回Token使用量

### 2. **成本计算**
- 根据cost配置计算实际费用
- 生成月度报告

### 3. **负载均衡**
- 按权重分配流量
- A/B测试不同模型

### 4. **缓存优化**
- 缓存常用回答
- 减少重复调用

### 5. **监控告警**
- 使用量接近限制时告警
- API错误率监控

---

## 📚 相关文档

| 文档 | 说明 |
|------|------|
| [`docs/LLM_MODEL_CONFIG_GUIDE.md`](file://g:\rag\kret-rag\llm-session\docs\LLM_MODEL_CONFIG_GUIDE.md) | ⭐ 完整配置指南 |
| [[config/llm_models.json.example](file://g:\rag\kret-rag\llm-session\config\llm_models.json.example)](file://g:\rag\kret-rag\llm-session\config\llm_models.json.example) | 配置示例 |
| [[test_llm_config.py](file://g:\rag\kret-rag\llm-session\test_llm_config.py)](file://g:\rag\kret-rag\llm-session\test_llm_config.py) | 测试脚本 |

---

## ✅ 验证清单

部署前请确认：

- [ ] 创建 `config/llm_models.json` 配置文件
- [ ] 配置正确的 `baseUrl` 和 `apiKey`
- [ ] 至少启用一个模型
- [ ] 运行测试脚本验证功能
- [ ] 检查API端点是否正常
- [ ] 验证Token使用量跟踪
- [ ] 测试模型切换功能

---

**立即开始使用**：

```bash
cd llm-session

# 1. 复制示例配置
cp config/llm_models.json.example config/llm_models.json

# 2. 编辑配置
nano config/llm_models.json

# 3. 运行测试
python test_llm_config.py

# 4. 启动服务
uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload
```

🎉 享受智能的LLM模型管理！
