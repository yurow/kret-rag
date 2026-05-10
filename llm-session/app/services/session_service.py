"""
会话管理服务
负责会话的创建、查询、更新和删除
"""
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

from app.models.schemas import (
    SessionInfo,
    Message,
    MessageRole,
    SessionStatus,
    CreateSessionRequest,
    ConversationContext
)
from app.core.config import settings


class SessionService:
    """会话管理服务"""
    
    def __init__(self):
        # 内存存储示例（实际应使用Redis或数据库）
        self.sessions: Dict[str, SessionInfo] = {}
        self.contexts: Dict[str, ConversationContext] = {}
    
    async def create_session(
        self, 
        request: CreateSessionRequest
    ) -> SessionInfo:
        """创建新会话"""
        session_id = str(uuid.uuid4())
        
        session_info = SessionInfo(
            session_id=session_id,
            user_id=request.user_id,
            session_name=request.session_name or f"Session {session_id[:8]}",
            status=SessionStatus.ACTIVE,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            message_count=0,
            metadata=request.metadata
        )
        
        # 创建会话上下文
        context = ConversationContext(session_id=session_id)
        
        # 存储会话和上下文
        self.sessions[session_id] = session_info
        self.contexts[session_id] = context
        
        return session_info
    
    async def get_session(self, session_id: str) -> Optional[SessionInfo]:
        """获取会话信息"""
        return self.sessions.get(session_id)
    
    async def list_sessions(
        self, 
        user_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> List[SessionInfo]:
        """列出会话"""
        sessions = list(self.sessions.values())
        
        # 按用户过滤
        if user_id:
            sessions = [s for s in sessions if s.user_id == user_id]
        
        # 分页
        start = (page - 1) * page_size
        end = start + page_size
        
        return sessions[start:end]
    
    async def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        if session_id not in self.sessions:
            return False
        
        # 删除会话和上下文
        del self.sessions[session_id]
        if session_id in self.contexts:
            del self.contexts[session_id]
        
        return True
    
    async def close_session(self, session_id: str) -> bool:
        """关闭会话"""
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        session.status = SessionStatus.CLOSED
        session.updated_at = datetime.now()
        
        return True
    
    def get_context(self, session_id: str) -> Optional[ConversationContext]:
        """获取会话上下文"""
        return self.contexts.get(session_id)
    
    def add_message_to_context(
        self, 
        session_id: str, 
        role: MessageRole, 
        content: str
    ) -> bool:
        """添加消息到会话上下文"""
        context = self.contexts.get(session_id)
        if not context:
            return False
        
        message = Message(role=role, content=content)
        context.add_message(message)
        
        # 更新会话信息
        session = self.sessions.get(session_id)
        if session:
            session.message_count += 1
            session.updated_at = datetime.now()
        
        return True
    
    def get_conversation_history(
        self, 
        session_id: str,
        recent_n: Optional[int] = None
    ) -> List[Message]:
        """获取对话历史"""
        context = self.contexts.get(session_id)
        if not context:
            return []
        
        if recent_n:
            return context.get_recent_messages(recent_n)
        
        return context.messages
    
    def clear_context(self, session_id: str) -> bool:
        """清空会话上下文"""
        context = self.contexts.get(session_id)
        if not context:
            return False
        
        context.clear()
        return True


# 创建全局实例
session_service = SessionService()
