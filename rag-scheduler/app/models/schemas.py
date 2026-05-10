"""
数据模型定义
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class DocumentStatus(str, Enum):
    """文档状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ChunkStrategy(str, Enum):
    """分块策略"""
    FIXED_SIZE = "fixed_size"
    PARAGRAPH = "paragraph"
    SENTENCE = "sentence"


# ========== 请求模型 ==========

class DocumentUploadRequest(BaseModel):
    """文档上传请求"""
    file_name: str
    file_size: int
    content_type: str
    metadata: Optional[Dict[str, Any]] = None


class DocumentQueryRequest(BaseModel):
    """文档查询请求"""
    query: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(default=5, ge=1, le=20)
    score_threshold: Optional[float] = Field(default=0.7, ge=0.0, le=1.0)
    filters: Optional[Dict[str, Any]] = None
    use_hybrid: bool = Field(default=True, description="是否使用混合检索（BM25 + 向量）")
    use_rerank: bool = Field(default=False, description="是否使用 Rerank 重排序（已禁用，调试基础流程）")
    use_query_rewrite: bool = Field(default=True, description="是否启用查询重写")
    session_id: Optional[str] = Field(default=None, description="会话ID，用于多轮对话上下文管理")


class DocumentChunkRequest(BaseModel):
    """文档分块请求"""
    document_id: str
    chunk_strategy: ChunkStrategy = ChunkStrategy.FIXED_SIZE
    chunk_size: int = Field(default=500, ge=100, le=2000)
    chunk_overlap: int = Field(default=50, ge=0, le=200)


# ========== 响应模型 ==========

class DocumentResponse(BaseModel):
    """文档响应"""
    document_id: str
    file_name: str
    status: DocumentStatus
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class ChunkResponse(BaseModel):
    """文本块响应"""
    chunk_id: str
    document_id: str
    content: str
    index: int
    metadata: Optional[Dict[str, Any]] = None


class QueryResultItem(BaseModel):
    """查询结果项"""
    chunk_id: str
    document_id: str
    content: str
    score: float
    metadata: Optional[Dict[str, Any]] = None


class DocumentQueryResponse(BaseModel):
    """文档查询响应"""
    results: List[QueryResultItem]
    total: int
    query_time: float
    context: Optional[str] = Field(default=None, description="构建的上下文字符串")
    original_query: Optional[str] = Field(default=None, description="原始查询")
    rewritten_query: Optional[str] = Field(default=None, description="重写后的查询")


class UploadResponse(BaseModel):
    """上传响应"""
    document_id: str
    message: str
    is_duplicate: bool = Field(default=False, description="是否为重复文件")


class DocumentUploadResult(BaseModel):
    """文档上传结果（内部使用）"""
    document_response: DocumentResponse
    is_duplicate: bool = False


# ========== 内部模型 ==========

class DocumentChunk(BaseModel):
    """文档分块内部模型"""
    chunk_id: str
    document_id: str
    content: str
    embedding: Optional[List[float]] = None
    index: int
    metadata: Dict[str, Any] = {}


class VectorSearchResult(BaseModel):
    """向量搜索结果"""
    chunk_id: str
    document_id: str
    content: str
    score: float
    metadata: Dict[str, Any] = {}


class TaskStatusResponse(BaseModel):
    """任务状态响应"""
    task_id: str
    status: str
    progress: float
    message: str
    created_at: datetime
    updated_at: datetime
    error: Optional[str] = None
