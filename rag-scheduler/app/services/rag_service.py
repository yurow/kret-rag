"""
RAG检索增强服务 - 仅负责检索和上下文构建

职责边界：
✅ 负责：
- 查询重写优化
- 向量检索（支持混合检索、Rerank）
- 上下文构建（带引用标记）
- 返回检索结果

❌ 不负责：
- Prompt模板管理（由llm-session负责）
- 多轮对话历史管理（由llm-session负责）
- LLM调用生成回答（由llm-session负责）
- 流式输出（由llm-session负责）
"""
from typing import List, Dict, Any, Optional
import time
import logging

from app.models.schemas import (
    DocumentQueryRequest,
    DocumentQueryResponse,
    QueryResultItem,
    VectorSearchResult
)
from app.services.vector_service import vector_store_service
from app.core.config import settings

# 配置日志
logger = logging.getLogger(__name__)


class RAGService:
    """RAG检索服务 - 仅负责检索和上下文构建"""
    
    async def retrieve_and_build_context(
        self,
        query_request: DocumentQueryRequest
    ) -> DocumentQueryResponse:
        """
        检索相关文档并构建上下文
        
        **流程**：
        1. 查询重写（优化检索效果）
        2. 向量检索（支持混合检索、Rerank）
        3. 构建带引用标记的上下文
        4. 返回检索结果和上下文
        
        **注意**：
        - 不调用LLM生成回答
        - 不管理对话历史
        - session_id 由调用方传递给 llm-session
        
        Args:
            query_request: 查询请求
            
        Returns:
            DocumentQueryResponse: 包含检索结果和上下文
        """
        start_time = time.time()
        
        try:
            # ⭐ 0. 查询重写（如果启用）
            original_query = query_request.query
            rewritten_query = original_query
            
            if getattr(query_request, 'use_query_rewrite', True):
                from app.services.query_rewrite_service import query_rewrite_service
                
                logger.info(f"原始查询: '{original_query}'")
                
                # 检测查询类型
                query_type = query_rewrite_service.detect_query_type(original_query)
                logger.info(f"查询类型: {query_type}")
                
                # 执行查询重写
                rewritten_query = query_rewrite_service.rewrite_query(original_query)
                
                if rewritten_query != original_query:
                    logger.info(f"重写后查询: '{rewritten_query}'")
                else:
                    logger.info("查询无需重写")
            
            # 1. 向量检索（使用重写后的查询）
            logger.info(
                f"开始检索: query='{rewritten_query[:50]}...', "
                f"top_k={query_request.top_k}, "
                f"use_hybrid={query_request.use_hybrid}, "
                f"use_rerank={query_request.use_rerank}"
            )
            
            search_results = await vector_store_service.similarity_search(
                query=rewritten_query,  # 使用重写后的查询
                top_k=query_request.top_k,
                score_threshold=query_request.score_threshold,
                filters=query_request.filters,
                use_hybrid=query_request.use_hybrid,
                use_rerank=query_request.use_rerank
            )
            
            logger.info(f"检索完成，找到 {len(search_results)} 个相关结果")
            
            # 2. 构建上下文
            context = self.build_context(
                search_results=search_results,
                max_tokens=2000
            )
            
            logger.info(f"上下文构建完成，长度: {len(context)} 字符")
            
            # 3. 构建结果
            results = []
            for result in search_results:
                results.append(QueryResultItem(
                    chunk_id=result.chunk_id,
                    document_id=result.document_id,
                    content=result.content,
                    score=result.score,  # 使用 score 字段
                    metadata=result.metadata
                ))
            
            # 4. 计算查询时间
            query_time = time.time() - start_time
            
            logger.info(f"查询完成，耗时: {query_time:.3f}秒")
            
            return DocumentQueryResponse(
                results=results,
                total=len(results),
                query_time=query_time,
                context=context,
                original_query=original_query,
                rewritten_query=rewritten_query if rewritten_query != original_query else None
            )
            
        except Exception as e:
            logger.error(f"检索失败: {str(e)}", exc_info=True)
            raise
    
    def build_context(
        self, 
        search_results: List[VectorSearchResult],
        max_tokens: int = 2000
    ) -> str:
        """
        根据检索结果构建上下文
        
        **格式**：
        ```
        [引用1] 第一段内容...
        
        [引用2] 第二段内容...
        
        ...
        ```
        
        Args:
            search_results: 搜索结果列表
            max_tokens: 最大字符数（默认2000）
            
        Returns:
            str: 带引用标记的上下文字符串
        """
        if not search_results:
            return ""
        
        context_parts = []
        current_length = 0
        
        for i, result in enumerate(search_results, 1):
            content = result.content
            
            # 添加引用标记
            marked_content = f"[引用{i}] {content}"
            
            # 检查是否超过最大长度
            if current_length + len(marked_content) > max_tokens:
                # 截断过长的内容
                remaining = max_tokens - current_length
                if remaining > 100:  # 至少保留100个字符
                    context_parts.append(marked_content[:remaining] + "...")
                break
            
            context_parts.append(marked_content)
            current_length += len(marked_content) + 2  # +2 for \n\n
        
        # 用双换行符连接
        context = "\n\n".join(context_parts)
        
        return context


# 创建全局实例
rag_service = RAGService()
