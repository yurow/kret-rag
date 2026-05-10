"""
向量检索服务
负责文本向量化、存储和相似度搜索
"""
from typing import List, Dict, Any, Optional
import numpy as np
from datetime import datetime
import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
import logging

from app.models.schemas import (
    DocumentChunk, 
    VectorSearchResult,
    QueryResultItem
)
from app.core.config import settings

# 配置日志
logger = logging.getLogger(__name__)


class VectorStoreService:
    """向量存储服务"""
    
    def __init__(self):
        self.vector_db = None
        self.embedding_model = None
        self.collection = None
    
    async def initialize(self):
        """初始化向量数据库和embedding模型"""
        try:
            # 初始化 ChromaDB（使用持久化存储）
            logger.info(f"初始化 ChromaDB，路径: {settings.CHROMA_HOST}")
            self.vector_db = chromadb.PersistentClient(path=settings.CHROMA_HOST)
            
            # 获取或创建集合（使用余弦相似度）
            self.collection = self.vector_db.get_or_create_collection(
                name=settings.CHROMA_COLLECTION_NAME,
                metadata={
                    "description": "RAG文档向量集合",
                    "hnsw:space": "cosine"  # 使用余弦相似度
                }
            )
            
            logger.info(f"ChromaDB 集合 '{settings.CHROMA_COLLECTION_NAME}' 初始化成功（余弦相似度）")
            
            # 加载 Embedding 模型
            logger.info(f"加载 Embedding 模型: {settings.EMBEDDING_MODEL}")
            self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
            logger.info("Embedding 模型加载成功")
            
            # 初始化混合检索服务（BM25 + Rerank）
            await self._initialize_hybrid_search()
            
        except Exception as e:
            logger.error(f"向量服务初始化失败: {str(e)}", exc_info=True)
            raise
    
    async def _initialize_hybrid_search(self):
        """
        初始化混合检索服务
        从 ChromaDB 中获取所有文档构建 BM25 索引
        """
        try:
            from app.services.hybrid_search_service import hybrid_search_service
            
            logger.info("开始初始化混合检索服务...")
            
            # 检查 collection 状态
            logger.info(f"Collection 名称: {self.collection.name}")
            doc_count = self.collection.count()
            logger.info(f"Collection 中文档总数: {doc_count}")
            
            # 从 ChromaDB 获取所有文档
            all_docs = self.collection.get(
                include=["documents"]
            )
            
            logger.info(f"get() 返回的 documents 数量: {len(all_docs['documents']) if all_docs['documents'] else 0}")
            logger.info(f"get() 返回的 ids 数量: {len(all_docs['ids']) if all_docs['ids'] else 0}")
            
            if all_docs['documents']:
                documents = all_docs['documents']
                document_ids = all_docs['ids']
                
                logger.info(f"找到 {len(documents)} 个文档用于 BM25 索引")
                
                # 初始化混合搜索服务
                await hybrid_search_service.initialize(documents, document_ids)
                
                logger.info("混合检索服务初始化成功")
            else:
                logger.warning("ChromaDB 中没有文档，跳过 BM25 索引初始化")
                logger.warning(f"可能的原因：")
                logger.warning(f"  1. Collection 确实是空的（count={doc_count}）")
                logger.warning(f"  2. get() 调用失败但未抛出异常")
                logger.warning(f"  3. ChromaDB 路径配置错误，读取了不同的数据库")
            
        except Exception as e:
            logger.warning(f"混合检索服务初始化失败（可选功能）: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        生成文本向量
        
        Args:
            text: 输入文本
            
        Returns:
            List[float]: 向量表示
        """
        if not self.embedding_model:
            raise RuntimeError("Embedding 模型未初始化，请先调用 initialize()")
        
        try:
            # 使用 Sentence Transformers 生成向量
            embedding = self.embedding_model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"生成向量失败: {str(e)}", exc_info=True)
            raise
    
    async def store_chunks(
        self, 
        document_id: str,
        chunks: List[str],
        file_name: str
    ) -> bool:
        """
        存储文档块向量到 ChromaDB
        
        Args:
            document_id: 文档ID
            chunks: 文本块列表
            file_name: 文件名
            
        Returns:
            bool: 是否成功
        """
        if not self.collection:
            raise RuntimeError("向量数据库未初始化，请先调用 initialize()")
        
        if not chunks:
            logger.warning("没有文本块需要存储")
            return False
        
        try:
            logger.info(f"开始存储 {len(chunks)} 个文本块...")
            
            # 为每个 chunk 生成 ID
            ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]
            
            # 生成所有 chunk 的向量（批量处理更高效）
            logger.info("正在生成向量...")
            embeddings = self.embedding_model.encode(chunks).tolist()
            
            # 准备元数据
            metadatas = [
                {
                    "document_id": document_id,
                    "file_name": file_name,
                    "chunk_index": i,
                    "chunk_length": len(chunk),
                    "timestamp": datetime.now().isoformat()
                }
                for i, chunk in enumerate(chunks)
            ]
            
            # 存储到 ChromaDB
            logger.info("正在写入 ChromaDB...")
            self.collection.add(
                ids=ids,
                documents=chunks,
                embeddings=embeddings,
                metadatas=metadatas
            )
            
            logger.info(f"成功存储 {len(chunks)} 个文本块到向量数据库")
            return True
            
        except Exception as e:
            logger.error(f"存储文本块失败: {str(e)}", exc_info=True)
            raise
    
    async def similarity_search(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.7,
        filters: Optional[Dict[str, Any]] = None,
        use_hybrid: bool = True,  # ⭐ 新增参数：是否使用混合检索
        use_rerank: bool = False   # ⭐ 暂时禁用Rerank（性能优化）
    ) -> List[VectorSearchResult]:
        """
        相似度搜索（支持混合检索）
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            score_threshold: 相似度阈值
            filters: 过滤条件
            use_hybrid: 是否使用混合检索（BM25 + 向量）
            use_rerank: 是否使用 Rerank 重排序
            
        Returns:
            List[VectorSearchResult]: 搜索结果列表
        """
        if not self.collection:
            raise RuntimeError("向量数据库未初始化")
        
        try:
            # 1. 执行向量检索
            logger.info(f"开始向量检索: query='{query[:50]}...'")
            vector_results = await self._vector_search(
                query=query,
                top_k=top_k * 2 if use_hybrid else top_k,  # 混合检索时获取更多候选
                score_threshold=score_threshold,
                filters=filters
            )
            
            logger.info(f"向量检索完成，找到 {len(vector_results)} 个结果")
            
            # 2. 如果不使用混合检索，直接返回向量结果
            if not use_hybrid:
                return vector_results[:top_k]
            
            # 3. 执行混合检索（BM25 + Rerank）
            from app.services.hybrid_search_service import hybrid_search_service
            
            if not hybrid_search_service.bm25_service.is_initialized:
                logger.warning("BM25 索引未初始化，降级为纯向量检索")
                return vector_results[:top_k]
            
            logger.info("执行混合检索（BM25 + Rerank）...")
            
            # 调用混合搜索服务
            final_results = await hybrid_search_service.hybrid_search(
                query=query,
                vector_results=vector_results,
                top_k=top_k,
                use_rerank=use_rerank
            )
            
            logger.info(f"混合检索完成，返回 {len(final_results)} 个结果")
            return final_results
            
        except Exception as e:
            logger.error(f"相似度搜索失败: {str(e)}", exc_info=True)
            raise
    
    async def _vector_search(
        self,
        query: str,
        top_k: int = 10,
        score_threshold: float = 0.7,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[VectorSearchResult]:
        """
        纯向量检索（内部方法）
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            score_threshold: 相似度阈值（设置为 -1 可禁用过滤）
            filters: 过滤条件
            
        Returns:
            List[VectorSearchResult]: 搜索结果列表
        """
        try:
            # 生成查询向量
            query_embedding = self.generate_embedding(query)
            
            # 构建过滤条件
            where_filter = {}
            if filters:
                for key, value in filters.items():
                    where_filter[key] = {"$eq": value}
            
            # 执行相似度搜索
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_filter if where_filter else None,
                include=["documents", "distances", "metadatas"]
            )
            
            # 转换结果格式
            search_results = []
            if results['ids'] and results['ids'][0]:
                for i, doc_id in enumerate(results['ids'][0]):
                    distance = results['distances'][0][i]
                    # ChromaDB 使用余弦距离，转换为相似度分数（-1到1）
                    similarity_score = 1.0 - distance
                    
                    # 过滤低于阈值的結果（如果 threshold < 0 则不过滤）
                    if score_threshold < 0 or similarity_score >= score_threshold:
                        metadata = results['metadatas'][0][i]
                        search_results.append(VectorSearchResult(
                            chunk_id=doc_id,
                            content=results['documents'][0][i],
                            score=similarity_score,  # 使用 score 字段名
                            document_id=metadata.get('document_id', ''),
                            file_name=metadata.get('file_name', ''),
                            chunk_index=metadata.get('chunk_index', 0),
                            metadata=metadata
                        ))
            
            logger.debug(f"向量检索完成，找到 {len(search_results)} 个相关结果")
            return search_results
            
        except Exception as e:
            logger.error(f"向量检索失败: {str(e)}", exc_info=True)
            raise
    
    async def delete_document_vectors(self, document_id: str) -> bool:
        """
        删除文档的所有向量
        
        Args:
            document_id: 文档ID
            
        Returns:
            bool: 是否成功
        """
        if not self.collection:
            raise RuntimeError("向量数据库未初始化")
        
        try:
            # 查找该文档的所有 chunk
            results = self.collection.get(
                where={"document_id": {"$eq": document_id}}
            )
            
            if results['ids']:
                # 删除所有相关的 chunk
                self.collection.delete(ids=results['ids'])
                logger.info(f"已删除文档 {document_id} 的 {len(results['ids'])} 个向量")
            
            return True
            
        except Exception as e:
            logger.error(f"删除向量失败: {str(e)}", exc_info=True)
            raise
    
    async def get_document_chunk_count(self, document_id: str) -> int:
        """
        获取文档的 chunk 数量
        
        Args:
            document_id: 文档ID
            
        Returns:
            int: chunk 数量
        """
        if not self.collection:
            raise RuntimeError("向量数据库未初始化")
        
        try:
            results = self.collection.get(
                where={"document_id": {"$eq": document_id}}
            )
            return len(results['ids']) if results['ids'] else 0
        except Exception as e:
            logger.error(f"获取 chunk 数量失败: {str(e)}", exc_info=True)
            return 0


# 创建全局实例
vector_store_service = VectorStoreService()
