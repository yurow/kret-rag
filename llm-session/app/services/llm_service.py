"""
LLM调用服务 - 支持动态模型配置

**功能**：
- 从配置文件加载模型信息
- 支持OpenAI和Anthropic两种API协议
- 自动跟踪Token使用量
- 超过限制时自动切换模型
"""
import httpx
import json
from typing import List, Dict, Any, Optional, AsyncGenerator
from app.models.schemas import Message, MessageRole
from app.core.llm_config_manager import llm_config_manager
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class LLMService:
    """LLM调用服务"""
    
    def __init__(self):
        self.config_manager = llm_config_manager
    
    async def generate_response(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        生成LLM响应
        
        **流程**：
        1. 获取当前可用模型和提供商
        2. 构建请求
        3. 调用API
        4. 记录Token使用
        5. 如果失败，尝试切换模型/提供商并重试
        """
        # 获取当前模型和提供商
        current_model = self.config_manager.get_current_model()
        current_provider = self.config_manager.get_current_provider()
        
        if not current_model or not current_provider:
            raise ValueError("没有可用的LLM模型")
        
        # 转换消息格式
        formatted_messages = [
            {
                "role": msg.role.value,
                "content": msg.content
            }
            for msg in messages
        ]
        
        # 根据API协议调用不同的方法
        if current_provider.api == "openai-completions":
            return await self._call_openai_compatible(
                messages=formatted_messages,
                provider=current_provider,
                model=current_model,
                temperature=temperature or 0.7,
                max_tokens=max_tokens or current_model.maxTokens,
                timeout=current_model.timeout
            )
        elif current_provider.api == "anthropic-messages":
            return await self._call_anthropic(
                messages=formatted_messages,
                provider=current_provider,
                model=current_model,
                temperature=temperature or 0.7,
                max_tokens=max_tokens or current_model.maxTokens,
                timeout=current_model.timeout
            )
        else:
            raise ValueError(f"不支持的API协议: {current_provider.api}")
    
    async def _call_openai_compatible(
        self,
        messages: List[Dict[str, str]],
        provider: Any,
        model: Any,
        temperature: float,
        max_tokens: int,
        timeout: int
    ) -> str:
        """调用OpenAI兼容的API"""
        api_endpoint = self.config_manager.get_api_endpoint()
        headers = self.config_manager.get_headers()
        
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
            "max_tokens": actual_max_tokens
        }
        
        # 如果模型支持深度思考，添加reasoning参数
        if hasattr(model, 'reasoning') and model.reasoning:
            request_data["reasoning"] = True
        
        try:
            logger.info(f"调用LLM API: [{provider.name}] {model.name}, endpoint={api_endpoint}")
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    api_endpoint,
                    headers=headers,
                    json=request_data
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    
                    # 计算Token使用量（估算）
                    input_tokens = self._estimate_tokens(messages)
                    output_tokens = self._estimate_tokens([{"content": content}])
                    total_tokens = input_tokens + output_tokens
                    
                    # 记录使用量
                    self.config_manager.record_token_usage(total_tokens)
                    
                    logger.info(f"LLM响应成功: {len(content)} 字符, 约 {total_tokens} tokens")
                    return content
                else:
                    error_msg = f"API错误: {response.status_code}, {response.text}"
                    logger.error(error_msg)
                    
                    # 尝试切换到下一个模型/提供商
                    if self.config_manager.switch_to_next_model():
                        logger.info("切换到下一个模型/提供商重试...")
                        next_model = self.config_manager.get_current_model()
                        next_provider = self.config_manager.get_current_provider()
                        if next_model and next_provider:
                            return await self._call_openai_compatible(
                                messages, next_provider, next_model, temperature, max_tokens, timeout
                            )
                    else:
                        raise Exception(error_msg)
                        
        except Exception as e:
            logger.error(f"调用LLM API失败: {e}", exc_info=True)
            
            # 尝试切换到下一个模型/提供商
            if self.config_manager.switch_to_next_model():
                logger.info("切换到下一个模型/提供商重试...")
                next_model = self.config_manager.get_current_model()
                next_provider = self.config_manager.get_current_provider()
                if next_model and next_provider:
                    return await self._call_openai_compatible(
                        messages, next_provider, next_model, temperature, max_tokens, timeout
                    )
            
            raise
    
    async def _call_anthropic(
        self,
        messages: List[Dict[str, str]],
        provider: Any,
        model: Any,
        temperature: float,
        max_tokens: int,
        timeout: int
    ) -> str:
        """调用Anthropic API"""
        api_endpoint = self.config_manager.get_api_endpoint()
        headers = self.config_manager.get_headers()

        # Anthropic需要特殊的消息格式
        system_message = None
        user_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                user_messages.append(msg)
        
        # 验证并限制max_tokens在模型支持范围内
        actual_max_tokens = min(max_tokens, model.maxTokens)
        if actual_max_tokens != max_tokens:
            logger.warning(
                f"max_tokens超出模型限制: 请求={max_tokens}, "
                f"模型上限={model.maxTokens}, 调整为={actual_max_tokens}"
            )
        
        request_data = {
            "model": model.id,
            "messages": user_messages,
            "max_tokens": actual_max_tokens,
            "temperature": temperature
        }
        
        if system_message:
            request_data["system"] = system_message
        
        try:
            logger.info(f"调用Anthropic API: [{provider.name}] {model.name}")
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    api_endpoint,
                    headers=headers,
                    json=request_data
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data["content"][0]["text"]
                    
                    # 计算Token使用量
                    input_tokens = self._estimate_tokens(messages)
                    output_tokens = self._estimate_tokens([{"content": content}])
                    total_tokens = input_tokens + output_tokens
                    
                    # 记录使用量
                    self.config_manager.record_token_usage(total_tokens)
                    
                    logger.info(f"Anthropic响应成功: {len(content)} 字符")
                    return content
                else:
                    error_msg = f"Anthropic API错误: {response.status_code}, {response.text}"
                    logger.error(error_msg)
                    
                    # 尝试切换到下一个模型/提供商
                    if self.config_manager.switch_to_next_model():
                        logger.info("切换到下一个模型/提供商重试...")
                        next_model = self.config_manager.get_current_model()
                        next_provider = self.config_manager.get_current_provider()
                        if next_model and next_provider:
                            return await self._call_anthropic(
                                messages, next_provider, next_model, temperature, max_tokens, timeout
                            )
                    else:
                        raise Exception(error_msg)
                        
        except Exception as e:
            logger.error(f"调用Anthropic API失败: {e}", exc_info=True)
            
            # 尝试切换到下一个模型/提供商
            if self.config_manager.switch_to_next_model():
                logger.info("切换到下一个模型/提供商重试...")
                next_model = self.config_manager.get_current_model()
                next_provider = self.config_manager.get_current_provider()
                if next_model and next_provider:
                    return await self._call_anthropic(
                        messages, next_provider, next_model, temperature, max_tokens, timeout
                    )
            
            raise
    
    async def stream_response(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> AsyncGenerator[str, None]:
        """
        流式响应
        
        **流程**：
        1. 获取当前可用模型和提供商
        2. 构建流式请求
        3. 调用API并逐块返回
        """
        # 获取当前模型和提供商
        current_model = self.config_manager.get_current_model()
        current_provider = self.config_manager.get_current_provider()
        
        if not current_model or not current_provider:
            raise ValueError("没有可用的LLM模型")
        
        # 转换消息格式
        formatted_messages = [
            {
                "role": msg.role.value,
                "content": msg.content
            }
            for msg in messages
        ]
        
        # 根据API协议调用不同的流式方法
        if current_provider.api == "openai-completions":
            async for chunk in self._stream_openai_compatible(
                messages=formatted_messages,
                provider=current_provider,
                model=current_model,
                temperature=temperature or 0.7,
                max_tokens=max_tokens or current_model.maxTokens,
                timeout=current_model.timeout
            ):
                yield chunk
        elif current_provider.api == "anthropic-messages":
            async for chunk in self._stream_anthropic(
                messages=formatted_messages,
                provider=current_provider,
                model=current_model,
                temperature=temperature or 0.7,
                max_tokens=max_tokens or current_model.maxTokens,
                timeout=current_model.timeout
            ):
                yield chunk
        else:
            raise ValueError(f"不支持的API协议: {current_provider.api}")
    
    async def _stream_openai_compatible(
        self,
        messages: List[Dict[str, str]],
        provider: Any,
        model: Any,
        temperature: float,
        max_tokens: int,
        timeout: int
    ) -> AsyncGenerator[str, None]:
        """流式调用OpenAI兼容的API"""
        import httpx
        
        api_endpoint = f"{provider.baseUrl}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {provider.apiKey}"
        }
        
        # 验证并限制max_tokens
        actual_max_tokens = min(max_tokens, model.maxTokens)
        
        request_data = {
            "model": model.id,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": actual_max_tokens,
            "stream": True  # ⭐ 启用流式输出
        }
        
        try:
            logger.info(f"流式调用LLM API: [{provider.name}] {model.name}")
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                async with client.stream(
                    "POST",
                    api_endpoint,
                    headers=headers,
                    json=request_data
                ) as response:
                    if response.status_code != 200:
                        error_text = await response.aread()
                        error_msg = f"API错误: {response.status_code}, {error_text.decode('utf-8')}"
                        logger.error(error_msg)
                        raise Exception(error_msg)
                    
                    # 解析SSE流
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:]  # 去掉 "data: " 前缀
                            
                            if data_str.strip() == "[DONE]":
                                break
                            
                            try:
                                import json
                                data = json.loads(data_str)
                                
                                # 提取文本内容
                                choices = data.get("choices", [])
                                if choices:
                                    delta = choices[0].get("delta", {})
                                    content = delta.get("content", "")
                                    
                                    if content:
                                        yield content
                                        
                            except json.JSONDecodeError as e:
                                logger.warning(f"JSON解析失败: {e}")
                                continue
                                
        except Exception as e:
            logger.error(f"流式调用失败: {str(e)}", exc_info=True)
            raise
    
    async def _stream_anthropic(
        self,
        messages: List[Dict[str, str]],
        provider: Any,
        model: Any,
        temperature: float,
        max_tokens: int,
        timeout: int
    ) -> AsyncGenerator[str, None]:
        """流式调用Anthropic API"""
        import httpx
        
        api_endpoint = f"{provider.baseUrl}/v1/messages"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": provider.apiKey,
            "anthropic-version": "2023-06-01"
        }
        
        # Anthropic需要特殊的消息格式
        system_message = None
        user_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                user_messages.append(msg)
        
        # 验证并限制max_tokens
        actual_max_tokens = min(max_tokens, model.maxTokens)
        
        request_data = {
            "model": model.id,
            "messages": user_messages,
            "max_tokens": actual_max_tokens,
            "temperature": temperature,
            "stream": True  # ⭐ 启用流式输出
        }
        
        if system_message:
            request_data["system"] = system_message
        
        try:
            logger.info(f"流式调用Anthropic API: [{provider.name}] {model.name}")
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                async with client.stream(
                    "POST",
                    api_endpoint,
                    headers=headers,
                    json=request_data
                ) as response:
                    if response.status_code != 200:
                        error_text = await response.aread()
                        error_msg = f"API错误: {response.status_code}, {error_text.decode('utf-8')}"
                        logger.error(error_msg)
                        raise Exception(error_msg)
                    
                    # 解析SSE流
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:]
                            
                            if data_str.strip() == "[DONE]":
                                break
                            
                            try:
                                import json
                                data = json.loads(data_str)
                                
                                # Anthropic流式格式
                                if data.get("type") == "content_block_delta":
                                    delta = data.get("delta", {})
                                    if delta.get("type") == "text_delta":
                                        content = delta.get("text", "")
                                        if content:
                                            yield content
                                        
                            except json.JSONDecodeError as e:
                                logger.warning(f"JSON解析失败: {e}")
                                continue
                                
        except Exception as e:
            logger.error(f"流式调用失败: {str(e)}", exc_info=True)
            raise
    
    def _estimate_tokens(self, messages: List[Dict[str, str]]) -> int:
        """
        估算Token数量
        
        **简化算法**：
        - 中文: 1个字符 ≈ 1个token
        - 英文: 4个字符 ≈ 1个token
        """
        total_chars = 0
        for msg in messages:
            content = msg.get("content", "")
            # 简单估算：中英文混合，平均2字符/token
            total_chars += len(content)
        
        return total_chars // 2
    
    def build_system_prompt(
        self,
        context: Optional[str] = None,
        custom_instructions: Optional[str] = None
    ) -> Message:
        """构建系统提示"""
        system_content = "你是一个智能助手，基于提供的上下文信息来回答用户问题。"
        
        if context:
            system_content += f"\n\n参考信息：\n{context}"
        
        if custom_instructions:
            system_content += f"\n\n{custom_instructions}"
        
        return Message(role=MessageRole.SYSTEM, content=system_content)


# 创建全局实例
llm_service = LLMService()
