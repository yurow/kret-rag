"""
数据库模型定义
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, JSON, Index
from sqlalchemy.sql import func
from app.db.database import db_manager


class DocumentMetadata(db_manager.Base):
    """文档元数据表"""
    
    __tablename__ = "document_metadata"
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增ID")
    
    # 文档标识
    document_id = Column(String(100), unique=True, nullable=False, index=True, comment="文档UUID")
    file_name = Column(String(500), nullable=False, comment="原始文件名")
    file_type = Column(String(50), nullable=False, comment="文件类型扩展名")
    
    # 文件信息
    file_size = Column(Integer, nullable=False, comment="文件大小（字节）")
    text_length = Column(Integer, nullable=True, comment="提取的文本长度")
    storage_path = Column(String(1000), nullable=False, comment="原始文件存储路径")
    text_file_path = Column(String(1000), nullable=True, comment="清洗后文本文件路径")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="上传时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")
    
    # 状态
    status = Column(String(20), default="completed", comment="处理状态：pending/processing/completed/failed")
    
    # 额外元数据（JSON格式）- 使用 extra_metadata 避免与 SQLAlchemy 保留字冲突
    extra_metadata = Column("metadata", JSON, nullable=True, comment="额外元数据")
    
    # 索引
    __table_args__ = (
        Index('idx_document_id', 'document_id'),
        Index('idx_file_type', 'file_type'),
        Index('idx_created_at', 'created_at'),
        Index('idx_status', 'status'),
    )
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "document_id": self.document_id,
            "file_name": self.file_name,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "text_length": self.text_length,
            "storage_path": self.storage_path,
            "text_file_path": self.text_file_path,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "status": self.status,
            "metadata": self.extra_metadata  # 对外仍使用 metadata 名称
        }
    
    def __repr__(self):
        return f"<DocumentMetadata(document_id='{self.document_id}', file_name='{self.file_name}')>"
