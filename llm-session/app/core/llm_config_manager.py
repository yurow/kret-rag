"""
动态LLM模型配置管理器（多平台支持）

**功能**：
- 从JSON文件加载多个提供商的配置
- 按优先级选择提供商和模型
- 自动跟踪每日Token使用量
- 支持跨平台模型切换
- 支持OpenAI和Anthropic两种API协议
"""
import json
import os
from datetime import datetime, date
from typing import Optional, Dict, Any, Tuple
from pathlib import Path
import logging

from app.core.config import MultiProviderConfig, LLMProviderConfig, LLMModelConfig, settings

logger = logging.getLogger(__name__)


class ModelUsageTracker:
    """模型使用量跟踪器"""
    
    def __init__(self, storage_path: str = "./data/model_usage.json"):
        self.storage_path = Path(storage_path)
        self.usage_data: Dict[str, Dict[str, Any]] = {}
        self._load_usage_data()
    
    def _load_usage_data(self):
        """加载使用量数据"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    self.usage_data = json.load(f)
                logger.info(f"已加载模型使用量数据: {len(self.usage_data)} 个模型")
            except Exception as e:
                logger.error(f"加载使用量数据失败: {e}")
                self.usage_data = {}
        else:
            self.usage_data = {}
    
    def _save_usage_data(self):
        """保存使用量数据"""
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(self.usage_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存使用量数据失败: {e}")
    
    def get_today_usage(self, model_id: str) -> int:
        """获取今日使用量"""
        today = date.today().isoformat()
        if model_id not in self.usage_data:
            return 0
        
        model_usage = self.usage_data[model_id]
        if model_usage.get('date') != today:
            # 新的一天，重置计数
            model_usage['date'] = today
            model_usage['tokens'] = 0
            self._save_usage_data()
            return 0
        
        return model_usage.get('tokens', 0)
    
    def record_usage(self, model_id: str, tokens: int):
        """记录使用量"""
        today = date.today().isoformat()
        
        if model_id not in self.usage_data:
            self.usage_data[model_id] = {'date': today, 'tokens': 0}
        
        self.usage_data[model_id]['tokens'] += tokens
        self._save_usage_data()
    
    def reset_daily_usage(self, model_id: str):
        """重置每日使用量"""
        if model_id in self.usage_data:
            self.usage_data[model_id]['tokens'] = 0
            self._save_usage_data()


class LLMConfigManager:
    """LLM配置管理器（多平台支持）"""
    
    def __init__(self):
        self.multi_provider_config: Optional[MultiProviderConfig] = None
        self.current_provider: Optional[LLMProviderConfig] = None
        self.current_model: Optional[LLMModelConfig] = None
        self.usage_tracker = ModelUsageTracker()
        self._load_config()
    
    def _load_config(self):
        """从JSON文件加载配置"""
        config_path = Path(settings.LLM_CONFIG_PATH)
        
        if not config_path.exists():
            logger.warning(f"配置文件不存在: {config_path}，使用默认配置")
            self._create_default_config()
            return
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            self.multi_provider_config = MultiProviderConfig(**config_data)
            logger.info(f"成功加载LLM配置: {len(self.multi_provider_config.providers)} 个提供商")
            
            # 选择第一个可用的模型（按优先级）
            result = self.multi_provider_config.get_first_available_model()
            if result:
                provider, model = result
                self.current_provider = provider
                self.current_model = model
                logger.info(f"当前使用: [{provider.name}] {model.name} ({model.id})")
            else:
                logger.warning("没有可用的模型")
                
        except Exception as e:
            logger.error(f"加载LLM配置失败: {e}", exc_info=True)
            self._create_default_config()
    
    def _create_default_config(self):
        """创建默认配置"""
        default_config = {
            "providers": [
                {
                    "name": "OpenAI",
                    "baseUrl": "https://api.openai.com/v1",
                    "apiKey": "",
                    "api": "openai-completions",
                    "priority": 1,
                    "models": [
                        {
                            "id": "gpt-3.5-turbo",
                            "name": "GPT-3.5 Turbo",
                            "tier": "small",
                            "enabled": True,
                            "reasoning": False,
                            "input": ["text"],
                            "cost": {"input": 0.001, "output": 0.002, "cacheRead": 0, "cacheWrite": 0},
                            "contextWindow": 16385,
                            "maxTokens": 4096,
                            "dailyTokenLimit": 100000,
                            "timeout": 60
                        }
                    ]
                }
            ]
        }
        
        self.multi_provider_config = MultiProviderConfig(**default_config)
        
        # 选择第一个可用模型
        result = self.multi_provider_config.get_first_available_model()
        if result:
            provider, model = result
            self.current_provider = provider
            self.current_model = model
        
        # 保存默认配置
        config_path = Path(settings.LLM_CONFIG_PATH)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
        
        logger.info(f"已创建默认配置文件: {config_path}")
    
    def get_current_model(self) -> Optional[LLMModelConfig]:
        """获取当前模型"""
        return self.current_model
    
    def get_current_provider(self) -> Optional[LLMProviderConfig]:
        """获取当前提供商"""
        return self.current_provider
    
    def switch_to_next_model(self) -> bool:
        """
        切换到下一个可用模型
        
        **策略**：
        1. 先尝试当前提供商的下一个模型
        2. 如果当前提供商没有可用模型，切换到下一个提供商
        """
        if not self.current_model or not self.multi_provider_config:
            return False
        
        # 1. 尝试当前提供商的下一个模型
        next_model = self.current_provider.switch_to_next_model(self.current_model.id)
        if next_model:
            logger.info(f"切换模型: {self.current_model.name} -> {next_model.name} (同提供商)")
            self.current_model = next_model
            return True
        
        # 2. 切换到下一个提供商
        sorted_providers = self.multi_provider_config.get_sorted_providers()
        current_idx = None
        for i, provider in enumerate(sorted_providers):
            if provider.name == self.current_provider.name:
                current_idx = i
                break
        
        if current_idx is not None:
            # 尝试下一个提供商
            for i in range(current_idx + 1, len(sorted_providers)):
                next_provider = sorted_providers[i]
                next_model = next_provider.get_available_model()
                if next_model:
                    logger.info(
                        f"切换提供商: [{self.current_provider.name}] -> [{next_provider.name}], "
                        f"模型: {next_model.name}"
                    )
                    self.current_provider = next_provider
                    self.current_model = next_model
                    return True
        
        logger.error("没有可用的模型可以切换")
        return False
    
    def record_token_usage(self, tokens: int):
        """记录Token使用量"""
        if self.current_model:
            self.current_model.record_usage(tokens)
            self.usage_tracker.record_usage(self.current_model.id, tokens)
            
            # 检查是否超过限制
            if not self.current_model.can_use():
                logger.warning(
                    f"模型 {self.current_model.name} 今日Token已达上限 "
                    f"({self.current_model.used_tokens_today}/{self.current_model.dailyTokenLimit})"
                )
                # 自动切换到下一个模型
                self.switch_to_next_model()
    
    def reload_config(self):
        """重新加载配置"""
        logger.info("重新加载LLM配置...")
        self._load_config()
    
    def get_api_endpoint(self) -> str:
        """获取API端点"""
        if not self.current_provider or not self.current_model:
            raise ValueError("LLM配置未初始化")
        
        base_url = self.current_provider.baseUrl.rstrip('/')
        
        if self.current_provider.api == "openai-completions":
            return f"{base_url}/chat/completions"
        elif self.current_provider.api == "anthropic-messages":
            return f"{base_url}/v1/messages"
        else:
            raise ValueError(f"不支持的API协议: {self.current_provider.api}")
    
    def get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        if not self.current_provider:
            raise ValueError("LLM配置未初始化")
        
        if self.current_provider.api == "openai-completions":
            return {
                "Authorization": f"Bearer {self.current_provider.apiKey}",
                "Content-Type": "application/json"
            }
        elif self.current_provider.api == "anthropic-messages":
            return {
                "x-api-key": self.current_provider.apiKey,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
        else:
            raise ValueError(f"不支持的API协议: {self.current_provider.api}")
    
    def get_all_providers_info(self) -> list:
        """获取所有提供商信息"""
        if not self.multi_provider_config:
            return []
        
        result = []
        for provider in self.multi_provider_config.get_sorted_providers():
            models_info = []
            for model in provider.models:
                models_info.append({
                    "id": model.id,
                    "name": model.name,
                    "enabled": model.enabled,
                    "canUse": model.can_use(),
                    "usedTokensToday": model.used_tokens_today,
                    "dailyLimit": model.dailyTokenLimit,
                    "isCurrent": self.current_model and model.id == self.current_model.id
                })
            
            result.append({
                "name": provider.name,
                "baseUrl": provider.baseUrl,
                "api": provider.api,
                "priority": provider.priority,
                "models": models_info
            })
        
        return result


# 全局实例
llm_config_manager = LLMConfigManager()
