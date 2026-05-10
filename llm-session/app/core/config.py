"""
LLM会话管理配置模块
"""
from pydantic_settings import BaseSettings
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ModelCostConfig(BaseModel):
    """模型成本配置"""
    input: float = 0.0  # 输入token成本（每1K tokens）
    output: float = 0.0  # 输出token成本
    cacheRead: float = 0.0  # 缓存读取成本
    cacheWrite: float = 0.0  # 缓存写入成本


class LLMModelConfig(BaseModel):
    """单个LLM模型配置"""
    id: str  # 模型ID，如 "doubao-seed-1-6-lite-251015"
    name: str  # 模型名称，如 "Doubao Seed 1.6 Lite"
    tier: str = "small"  # 模型层级: small, medium, large
    enabled: bool = True  # 是否启用
    reasoning: bool = False  # 是否支持深度思考
    input: List[str] = ["text"]  # 支持的输入类型: text, image, audio
    cost: ModelCostConfig = Field(default_factory=ModelCostConfig)  # 成本配置
    contextWindow: int = 128000  # 上下文窗口大小
    maxTokens: int = 96000  # 最大输出token数
    dailyTokenLimit: int = 1000000  # 每日Token限制
    timeout: int = 60  # 超时时间（秒）
    
    # 运行时状态（不保存到配置文件）
    used_tokens_today: int = 0  # 今日已使用token数
    
    def can_use(self) -> bool:
        """检查模型是否可用"""
        if not self.enabled:
            return False
        return self.used_tokens_today < self.dailyTokenLimit
    
    def record_usage(self, tokens: int):
        """记录token使用"""
        self.used_tokens_today += tokens
    
    def reset_daily_usage(self):
        """重置每日使用量"""
        self.used_tokens_today = 0


class LLMProviderConfig(BaseModel):
    """LLM提供商配置"""
    name: str  # 提供商名称，如 "火山引擎"、"OpenAI"
    baseUrl: str  # API基础URL
    apiKey: str  # API密钥
    api: str = "openai-completions"  # API协议: openai-completions, anthropic-messages
    priority: int = 1  # 优先级（数字越小优先级越高）
    models: List[LLMModelConfig]  # 该提供商下的模型列表
    
    def get_enabled_models(self) -> List[LLMModelConfig]:
        """获取所有启用的模型"""
        return [m for m in self.models if m.enabled]
    
    def get_available_model(self) -> Optional[LLMModelConfig]:
        """获取第一个可用的模型（未超过每日限制）"""
        for model in self.models:
            if model.can_use():
                return model
        return None
    
    def switch_to_next_model(self, current_model_id: str) -> Optional[LLMModelConfig]:
        """切换到下一个可用模型"""
        found_current = False
        for model in self.models:
            if found_current and model.can_use():
                return model
            if model.id == current_model_id:
                found_current = True
        return None


class MultiProviderConfig(BaseModel):
    """多提供商配置（根结构）"""
    providers: List[LLMProviderConfig]  # 提供商列表
    
    def get_sorted_providers(self) -> List[LLMProviderConfig]:
        """按优先级排序的提供商列表"""
        return sorted(self.providers, key=lambda p: p.priority)
    
    def get_all_models(self) -> List[tuple]:
        """获取所有模型及其所属提供商 [(provider, model), ...]"""
        result = []
        for provider in self.get_sorted_providers():
            for model in provider.models:
                result.append((provider, model))
        return result
    
    def get_first_available_model(self) -> Optional[tuple]:
        """获取第一个可用的模型 (provider, model)"""
        for provider in self.get_sorted_providers():
            model = provider.get_available_model()
            if model:
                return (provider, model)
        return None


class Settings(BaseSettings):
    """应用配置"""
    
    # 服务配置
    APP_NAME: str = "KRET-RAG LLM Session Manager"
    APP_VERSION: str = "1.0.0"
    HOST: str = "0.0.0.0"
    PORT: int = 9000
    
    # 数据库配置
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/session_db"
    
    # Redis配置（用于会话存储）
    REDIS_URL: str = "redis://localhost:6379/1"
    SESSION_TTL: int = 3600  # 会话过期时间（秒）
    
    # LLM配置 - 新格式
    LLM_CONFIG_PATH: str = "./config/llm_models.json"  # LLM模型配置文件路径
    
    # 对话配置
    MAX_CONTEXT_LENGTH: int = 10  # 最大上下文轮数
    MAX_TOKEN_LIMIT: int = 4096  # 最大token限制
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
