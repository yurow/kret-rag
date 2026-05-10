"""
LLM模型配置管理路由

**功能**：
- 查看当前配置
- 重新加载配置
- 切换模型
- 查看使用量统计
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.core.llm_config_manager import llm_config_manager
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/config", tags=["LLM配置管理"])


@router.get("/models")
async def get_models():
    """
    获取所有可用模型列表
    
    **返回**：
    - 所有提供商及其模型列表
    - 当前使用的提供商和模型
    - 每个模型的使用状态
    """
    try:
        providers_info = llm_config_manager.get_all_providers_info()
        
        current_model = llm_config_manager.get_current_model()
        current_provider = llm_config_manager.get_current_provider()
        
        return {
            "currentProvider": {
                "name": current_provider.name if current_provider else None,
                "api": current_provider.api if current_provider else None
            } if current_provider else None,
            "currentModel": {
                "id": current_model.id if current_model else None,
                "name": current_model.name if current_model else None
            } if current_model else None,
            "providers": providers_info
        }
        
    except Exception as e:
        logger.error(f"获取模型列表失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reload")
async def reload_config():
    """
    重新加载配置文件
    
    **用途**：
    - 修改配置文件后无需重启服务
    - 动态更新模型配置
    """
    try:
        llm_config_manager.reload_config()
        return {"status": "success", "message": "配置已重新加载"}
    except Exception as e:
        logger.error(f"重新加载配置失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/switch-model")
async def switch_model():
    """
    切换到下一个可用模型
    
    **用途**：
    - 手动切换模型
    - 测试不同模型的效果
    """
    try:
        success = llm_config_manager.switch_to_next_model()
        if success:
            current_model = llm_config_manager.get_current_model()
            return {
                "status": "success",
                "message": f"已切换到模型: {current_model.name}",
                "model": {
                    "id": current_model.id,
                    "name": current_model.name
                }
            }
        else:
            raise HTTPException(status_code=400, detail="没有可用的模型可以切换")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"切换模型失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/usage")
async def get_usage_stats():
    """
    获取模型使用量统计
    
    **返回**：
    - 每个模型的今日使用量
    - 剩余可用量
    - 使用百分比
    """
    try:
        multi_config = llm_config_manager.multi_provider_config
        if not multi_config:
            raise HTTPException(status_code=500, detail="LLM配置未初始化")
        
        usage_stats = []
        for provider in multi_config.providers:
            for model in provider.models:
                usage_percentage = (model.used_tokens_today / model.dailyTokenLimit * 100) if model.dailyTokenLimit > 0 else 0
                
                usage_stats.append({
                    "modelId": model.id,
                    "modelName": model.name,
                    "providerName": provider.name,
                    "usedTokens": model.used_tokens_today,
                    "dailyLimit": model.dailyTokenLimit,
                    "remainingTokens": model.dailyTokenLimit - model.used_tokens_today,
                    "usagePercentage": round(usage_percentage, 2),
                    "canUse": model.can_use()
                })
        
        return {
            "date": "today",
            "models": usage_stats
        }
        
    except Exception as e:
        logger.error(f"获取使用量统计失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset-usage/{model_id}")
async def reset_usage(model_id: str):
    """
    重置指定模型的每日使用量
    
    **参数**：
    - model_id: 模型ID
    
    **用途**：
    - 测试时重置计数器
    - 手动调整使用量
    """
    try:
        llm_config_manager.usage_tracker.reset_daily_usage(model_id)
        
        # 重新加载配置以更新内存中的计数
        llm_config_manager.reload_config()
        
        return {
            "status": "success",
            "message": f"模型 {model_id} 的使用量已重置"
        }
        
    except Exception as e:
        logger.error(f"重置使用量失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
