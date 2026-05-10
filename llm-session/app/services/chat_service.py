"""
聊天服务 - 统一管理对话和LLM调用

职责：
- Prompt模板管理
- 多轮对话历史管理
- 模型参数配置
- LLM调用与响应生成
- 流式输出
- RAG上下文整合（可选）
"""
from typing import List, Dict, Any, Optional, AsyncGenerator
import logging

from app.models.schemas import (
    Message,
    MessageRole,
    SendMessageRequest,
    SendMessageResponse,
    StreamChunk,
    ConversationContext
)
from app.services.session_service import session_service
from app.services.llm_service import llm_service
from app.core.config import settings

# 配置日志
logger = logging.getLogger(__name__)


class ChatService:
    """聊天服务 - 负责对话管理和LLM调用"""
    
    async def send_message(
        self,
        request: SendMessageRequest
    ) -> SendMessageResponse:
        """
        发送消息并获取响应
        
        **流程**：
        1. 获取或创建会话
        2. 添加用户消息到上下文
        3. 构建完整的对话历史
        4. 处理RAG上下文（如果有）
        5. 调用LLM生成响应
        6. 保存助手响应到上下文
        
        **支持RAG**：
        - 如果提供 rag_context，会将其作为系统提示的一部分
        - 如果提供 query，会在Prompt中明确标注原始问题
        """
        try:
            # 1. 如果没有会话ID，创建新会话
            if not request.session_id:
                from app.models.schemas import CreateSessionRequest
                session_info = await session_service.create_session(
                    CreateSessionRequest(user_id="default_user")
                )
                session_id = session_info.session_id
            else:
                session_id = request.session_id
            
            logger.info(f"处理消息: session_id={session_id}, has_rag_context={request.rag_context is not None}")
            
            # 2. 添加用户消息到上下文
            user_message = request.query if request.query else request.message
            session_service.add_message_to_context(
                session_id=session_id,
                role=MessageRole.USER,
                content=user_message
            )
            
            # 3. 获取对话历史（最近N轮）
            conversation_history = session_service.get_conversation_history(
                session_id=session_id,
                recent_n=settings.MAX_CONTEXT_LENGTH * 2  # 每轮包含用户和助手消息
            )
            
            # 4. 构建系统提示（支持RAG上下文）
            system_message = self._build_system_prompt(
                rag_context=request.rag_context,
                query=request.query
            )
            
            if system_message:
                conversation_history = [system_message] + conversation_history
            
            # 5. 调用LLM生成响应
            response_text = await llm_service.generate_response(
                messages=conversation_history
            )
            
            logger.info(f"LLM响应生成完成，长度: {len(response_text)} 字符")
            
            # 6. 添加助手响应到上下文
            session_service.add_message_to_context(
                session_id=session_id,
                role=MessageRole.ASSISTANT,
                content=response_text
            )
            
            # 7. 获取更新后的对话历史
            updated_history = session_service.get_conversation_history(
                session_id=session_id,
                recent_n=settings.MAX_CONTEXT_LENGTH * 2
            )
            
            return SendMessageResponse(
                session_id=session_id,
                message_id=str(len(updated_history)),
                response=response_text,
                conversation_history=updated_history
            )
            
        except Exception as e:
            logger.error(f"发送消息失败: {str(e)}", exc_info=True)
            raise
    
    def _build_system_prompt(
        self,
        rag_context: Optional[str] = None,
        query: Optional[str] = None
    ) -> Optional[Message]:
        """
        构建系统提示词
        
        **支持RAG**：
        - 如果有rag_context，构建RAG专用的系统提示
        - 否则使用默认的系统提示
        
        Args:
            rag_context: RAG检索的上下文内容
            query: 原始查询问题
            
        Returns:
            Optional[Message]: 系统提示消息（如果需要）
        """
        if not rag_context:
            return None
        
        # 构建RAG专用的系统提示（防幻觉版本）
        system_content = f"""你是一个智能问答助手。请基于以下参考信息回答问题。

**核心原则**：
1. **严格基于参考信息回答**：你的所有回答必须完全基于提供的参考信息
2. **禁止编造答案**：如果参考信息中没有相关信息，必须如实回答「知识库暂无相关配置信息」
3. **禁止自行发挥**：不要使用参考信息之外的知识来回答问题
4. **引用来源**：回答时要明确标注信息来源（如：[引用1]、[引用2]）
5. **保持准确**：确保回答与参考信息一致，不夸大、不臆测

**判断流程**：
- 第一步：仔细阅读参考信息
- 第二步：判断参考信息是否足以回答用户问题
- 第三步：如果足够 → 给出详细准确的回答，并标注引用
- 第四步：如果不足 → 直接回复「知识库暂无相关配置信息」

**参考信息**：
{rag_context}

**重要提醒**：
- 如果参考信息与问题无关，不要强行回答
- 如果参考信息不完整，不要补充缺失的信息
- 宁可说不知道，也不要编造答案
"""
        
        return Message(
            role=MessageRole.SYSTEM,
            content=system_content
        )
    
    async def stream_message(
        self,
        request: SendMessageRequest
    ) -> AsyncGenerator[StreamChunk, None]:
        """
        流式发送消息
        
        **支持RAG**：
        - 与send_message类似，但使用流式响应
        """
        try:
            # 类似send_message，但使用流式响应
            if not request.session_id:
                from app.models.schemas import CreateSessionRequest
                session_info = await session_service.create_session(
                    CreateSessionRequest(user_id="default_user")
                )
                session_id = session_info.session_id
            else:
                session_id = request.session_id
            
            logger.info(f"开始流式响应: session_id={session_id}")
            
            # 添加用户消息
            user_message = request.query if request.query else request.message
            session_service.add_message_to_context(
                session_id=session_id,
                role=MessageRole.USER,
                content=user_message
            )
            
            # 获取对话历史
            conversation_history = session_service.get_conversation_history(
                session_id=session_id,
                recent_n=settings.MAX_CONTEXT_LENGTH * 2
            )
            
            # 构建系统提示（支持RAG）
            system_message = self._build_system_prompt(
                rag_context=request.rag_context,
                query=request.query
            )
            
            if system_message:
                conversation_history = [system_message] + conversation_history
            
            # 流式调用LLM
            chunk_id = 0
            full_response = ""
            
            async for chunk in llm_service.stream_response(conversation_history):
                chunk_id += 1
                full_response += chunk
                
                yield StreamChunk(
                    session_id=session_id,
                    chunk_id=str(chunk_id),
                    content=chunk,
                    is_last=False
                )
            
            # 保存完整响应到上下文
            session_service.add_message_to_context(
                session_id=session_id,
                role=MessageRole.ASSISTANT,
                content=full_response
            )
            
            # 发送最后一个块
            yield StreamChunk(
                session_id=session_id,
                chunk_id=str(chunk_id + 1),
                content="",
                is_last=True
            )
            
            logger.info(f"流式响应完成: session_id={session_id}, total_chunks={chunk_id}")
            
        except Exception as e:
            logger.error(f"流式响应失败: {str(e)}", exc_info=True)
            raise


# 创建全局实例
chat_service = ChatService()
