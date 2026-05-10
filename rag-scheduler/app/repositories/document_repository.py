"""
文档元数据仓储层
实现数据访问逻辑，支持数据库扩展
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.db_models import DocumentMetadata


class DocumentRepository:
    """文档元数据仓储"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def create(self, document_id: str, file_name: str, file_type: str, 
               file_size: int, storage_path: str, text_length: int = None,
               text_file_path: str = None, metadata: Dict[str, Any] = None) -> DocumentMetadata:
        """
        创建文档元数据记录
        
        Args:
            document_id: 文档UUID
            file_name: 文件名
            file_type: 文件类型
            file_size: 文件大小
            storage_path: 原始文件存储路径
            text_length: 文本长度
            text_file_path: 清洗后文本文件路径
            metadata: 额外元数据
            
        Returns:
            DocumentMetadata: 创建的文档记录
        """
        doc_metadata = DocumentMetadata(
            document_id=document_id,
            file_name=file_name,
            file_type=file_type,
            file_size=file_size,
            text_length=text_length,
            storage_path=storage_path,
            text_file_path=text_file_path,
            extra_metadata=metadata or {},
            status="completed"
        )
        
        self.db.add(doc_metadata)
        self.db.commit()
        self.db.refresh(doc_metadata)
        
        return doc_metadata
    
    def get_by_id(self, document_id: str) -> Optional[DocumentMetadata]:
        """
        根据文档ID获取元数据
        
        Args:
            document_id: 文档UUID
            
        Returns:
            Optional[DocumentMetadata]: 文档元数据，不存在返回None
        """
        return self.db.query(DocumentMetadata).filter(
            DocumentMetadata.document_id == document_id
        ).first()
    
    def get_by_internal_id(self, internal_id: int) -> Optional[DocumentMetadata]:
        """
        根据内部ID获取元数据
        
        Args:
            internal_id: 自增ID
            
        Returns:
            Optional[DocumentMetadata]: 文档元数据
        """
        return self.db.query(DocumentMetadata).filter(
            DocumentMetadata.id == internal_id
        ).first()
    
    def list_all(self, page: int = 1, page_size: int = 10, 
                 file_type: str = None, status: str = None) -> List[DocumentMetadata]:
        """
        分页查询文档列表
        
        Args:
            page: 页码（从1开始）
            page_size: 每页数量
            file_type: 文件类型过滤
            status: 状态过滤
            
        Returns:
            List[DocumentMetadata]: 文档列表
        """
        query = self.db.query(DocumentMetadata)
        
        # 添加过滤条件
        if file_type:
            query = query.filter(DocumentMetadata.file_type == file_type)
        if status:
            query = query.filter(DocumentMetadata.status == status)
        
        # 按创建时间倒序排序
        query = query.order_by(DocumentMetadata.created_at.desc())
        
        # 分页
        offset = (page - 1) * page_size
        docs = query.offset(offset).limit(page_size).all()
        
        return docs
    
    def count(self, file_type: str = None, status: str = None) -> int:
        """
        统计文档数量
        
        Args:
            file_type: 文件类型过滤
            status: 状态过滤
            
        Returns:
            int: 文档总数
        """
        query = self.db.query(DocumentMetadata)
        
        if file_type:
            query = query.filter(DocumentMetadata.file_type == file_type)
        if status:
            query = query.filter(DocumentMetadata.status == status)
        
        return query.count()
    
    def update_status(self, document_id: str, status: str) -> bool:
        """
        更新文档状态
        
        Args:
            document_id: 文档UUID
            status: 新状态
            
        Returns:
            bool: 是否更新成功
        """
        doc = self.get_by_id(document_id)
        if not doc:
            return False
        
        doc.status = status
        self.db.commit()
        return True
    
    def update_metadata(self, document_id: str, metadata: Dict[str, Any]) -> bool:
        """
        更新文档元数据
        
        Args:
            document_id: 文档UUID
            metadata: 新的元数据字典
            
        Returns:
            bool: 是否更新成功
        """
        doc = self.get_by_id(document_id)
        if not doc:
            return False
        
        # 合并元数据
        if doc.extra_metadata:
            doc.extra_metadata.update(metadata)
        else:
            doc.extra_metadata = metadata
        
        self.db.commit()
        return True
    
    def delete(self, document_id: str) -> bool:
        """
        删除文档元数据
        
        Args:
            document_id: 文档UUID
            
        Returns:
            bool: 是否删除成功
        """
        doc = self.get_by_id(document_id)
        if not doc:
            return False
        
        self.db.delete(doc)
        self.db.commit()
        return True
    
    def search(self, keyword: str, page: int = 1, page_size: int = 10) -> List[DocumentMetadata]:
        """
        搜索文档（基于文件名）
        
        Args:
            keyword: 搜索关键词
            page: 页码
            page_size: 每页数量
            
        Returns:
            List[DocumentMetadata]: 匹配的文档列表
        """
        query = self.db.query(DocumentMetadata).filter(
            DocumentMetadata.file_name.like(f"%{keyword}%")
        ).order_by(
            DocumentMetadata.created_at.desc()
        )
        
        offset = (page - 1) * page_size
        docs = query.offset(offset).limit(page_size).all()
        
        return docs
    
    def find_duplicate(self, file_name: str, file_size: int) -> Optional[DocumentMetadata]:
        """
        根据文件名和文件大小查找重复文档
        
        Args:
            file_name: 文件名
            file_size: 文件大小（字节）
            
        Returns:
            Optional[DocumentMetadata]: 如果存在重复文档则返回，否则返回None
        """
        return self.db.query(DocumentMetadata).filter(
            DocumentMetadata.file_name == file_name,
            DocumentMetadata.file_size == file_size
        ).first()
