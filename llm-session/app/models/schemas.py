"""
数据模型定义
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    """消息角色"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class SessionStatus(str, Enum):
    """会话状态"""
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"


# ========== 请求模型 ==========

class CreateSessionRequest(BaseModel):
    """创建会话请求"""
    user_id: Optional[str] = None
    session_name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class SendMessageRequest(BaseModel):
    """发送消息请求"""
    message: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    query: Optional[str] = Field(default=None, description="原始查询（来自RAG检索）")
    rag_context: Optional[str] = Field(default=None, description="RAG检索的上下文内容")


class StreamMessageRequest(BaseModel):
    """流式消息请求"""
    message: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    query: Optional[str] = Field(default=None, description="原始查询（来自RAG检索）")
    rag_context: Optional[str] = Field(default=None, description="RAG检索的上下文内容")


# ========== 响应模型 ==========

class Message(BaseModel):
    """消息模型"""
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None


class SessionInfo(BaseModel):
    """会话信息"""
    session_id: str
    user_id: Optional[str] = None
    session_name: Optional[str] = None
    status: SessionStatus
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    metadata: Optional[Dict[str, Any]] = None


class CreateSessionResponse(BaseModel):
    """创建会话响应"""
    session_id: str
    message: str


class SendMessageResponse(BaseModel):
    """发送消息响应"""
    session_id: str
    message_id: str
    response: str
    conversation_history: Optional[List[Message]] = None


class StreamChunk(BaseModel):
    """流式响应块"""
    session_id: str
    chunk_id: str
    content: str
    is_last: bool = False


class ListSessionsResponse(BaseModel):
    """列出会话响应"""
    sessions: List[SessionInfo]
    total: int


# ========== 内部模型 ==========

class ConversationContext(BaseModel):
    """对话上下文"""
    session_id: str
    messages: List[Message] = []
    metadata: Dict[str, Any] = {}
    
    def add_message(self, message: Message):
        """添加消息到上下文"""
        self.messages.append(message)
    
    def get_recent_messages(self, n: int) -> List[Message]:
        """获取最近n条消息"""
        return self.messages[-n:]
    
    def clear(self):
        """清空上下文"""
        self.messages.clear()
