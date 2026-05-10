"""
查询API路由 - RAG检索服务

职责：
- 文档检索（向量搜索、混合检索）
- 上下文构建
- 返回检索结果和上下文给调用方
- 传递 session_id 给 llm-session 进行对话管理
"""
from fastapi import APIRouter, HTTPException
import time
import logging

from app.models.schemas import (
    DocumentQueryRequest,
    DocumentQueryResponse,
    QueryResultItem,
    VectorSearchResult
)
from app.services.rag_service import rag_service

# 配置日志
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/query",
    tags=["query"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=DocumentQueryResponse)
async def query_documents(request: DocumentQueryRequest):
    """
    RAG检索服务 - 检索相关文档并构建上下文
    
    **职责**：
    - 执行向量检索（支持混合检索、Rerank）
    - 查询重写优化
    - 构建带引用标记的上下文
    - 返回检索结果和上下文
    
    **不负责的**：
    - ❌ Prompt模板管理（由llm-session负责）
    - ❌ 多轮对话历史（由llm-session负责）
    - ❌ LLM调用生成回答（由llm-session负责）
    - ❌ 流式输出（由llm-session负责）
    
    **使用场景**：
    1. 前端直接调用获取相关文档片段
    2. llm-session调用此接口获取上下文后再生成回答
    3. 测试检索效果
    
    **参数说明**：
    - **query**: 用户问题
    - **top_k**: 返回结果数量（默认5，范围1-20）
    - **score_threshold**: 相似度阈值（默认0.7，范围0.0-1.0）
    - **filters**: 元数据过滤条件（可选）
    - **use_hybrid**: 是否启用混合检索（BM25+向量，默认True）
    - **use_rerank**: 是否启用Rerank重排序（默认True）
    - **use_query_rewrite**: 是否启用查询重写（默认True）
    - **session_id**: 会话ID（可选，传递给llm-session用于多轮对话）
    
    **返回字段**：
    - **results**: 检索结果列表（包含chunk_id, document_id, content, score, metadata）
    - **total**: 结果总数
    - **context**: 构建的上下文字符串（带[引用1]标记）
    - **original_query**: 原始查询
    - **rewritten_query**: 重写后的查询（如果有）
    - **query_time**: 查询耗时（秒）
    """
    try:
        logger.info(f"收到查询请求: query='{request.query[:50]}...', top_k={request.top_k}")
        
        # 执行检索和上下文构建
        result = await rag_service.retrieve_and_build_context(request)
        
        logger.info(f"查询完成: 找到{result.total}个结果, 耗时{result.query_time:.3f}秒")
        
        return result
        
    except Exception as e:
        logger.error(f"查询失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@router.post("/search")
async def search_documents(request: DocumentQueryRequest):
    """
    纯向量搜索 - 仅执行检索，不构建上下文
    
    **用途**：
    - 测试检索效果
    - 获取原始搜索结果
    - 调试向量数据库
    
    **返回**：原始搜索结果列表（不含上下文）
    """
    try:
        from app.services.vector_service import vector_store_service
        
        logger.info(f"执行纯向量搜索: query='{request.query[:50]}...'")
        
        search_results = await vector_store_service.similarity_search(
            query=request.query,
            top_k=request.top_k,
            score_threshold=request.score_threshold,
            filters=request.filters,
            use_hybrid=request.use_hybrid,
            use_rerank=request.use_rerank
        )
        
        return {
            "results": [
                {
                    "chunk_id": r.chunk_id,
                    "document_id": r.document_id,
                    "content": r.content,
                    "score": r.score,  # 使用 score 字段
                    "metadata": r.metadata
                }
                for r in search_results
            ],
            "total": len(search_results),
            "query": request.query
        }
        
    except Exception as e:
        logger.error(f"搜索失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/context")
async def build_context_only(request: DocumentQueryRequest):
    """
    仅构建上下文 - 检索 + 上下文拼接
    
    **用途**：
    - 快速获取格式化的上下文
    - 用于外部LLM服务调用
    - 测试上下文构建效果
    
    **返回**：
    - context: 带引用标记的上下文字符串
    - results: 检索结果列表
    - metadata: 元数据信息
    """
    try:
        logger.info(f"构建上下文: query='{request.query[:50]}...'")
        
        # 执行检索和上下文构建
        result = await rag_service.retrieve_and_build_context(request)
        
        return {
            "context": result.context,
            "results": [
                {
                    "chunk_id": r.chunk_id,
                    "document_id": r.document_id,
                    "content": r.content,
                    "score": r.score,
                    "metadata": r.metadata
                }
                for r in result.results
            ],
            "total": result.total,
            "original_query": result.original_query,
            "rewritten_query": result.rewritten_query,
            "query_time": result.query_time
        }
        
    except Exception as e:
        logger.error(f"上下文构建失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Context building failed: {str(e)}")


@router.post("/generate")
async def generate_answer(request: DocumentQueryRequest):
    """
    生成回答 - 将请求转发给 llm-session 服务
    
    **职责**：
    - 执行检索和上下文构建
    - 将上下文传递给 llm-session 服务
    - 返回 llm-session 的生成结果
    
    **参数说明**：
    - **query**: 用户问题
    - **session_id**: 会话ID（可选，用于多轮对话）
    - **其他参数**: 用于检索优化
    """
    try:
        logger.info(f"开始生成回答: query='{request.query[:50]}...', session_id={getattr(request, 'session_id', 'None')}")
        
        # 先执行检索和上下文构建
        rag_result = await rag_service.retrieve_and_build_context(request)
        
        # 调用 llm-session 服务生成回答
        import httpx
        from app.core.config import settings
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{settings.LLM_SESSION_URL}/chat/message",
                json={
                    "message": request.query,  # 用户问题作为消息
                    "session_id": getattr(request, 'session_id', None),
                    "query": request.query,  # 原始查询
                    "rag_context": rag_result.context if rag_result.context else None  # ⭐ RAG检索的上下文
                }
            )
            
            if response.status_code == 200:
                llm_response = response.json()
                
                # 获取会话历史以提取系统提示词
                session_id = llm_response.get("session_id", getattr(request, 'session_id', None))
                system_prompt = None
                
                # 尝试从llm-session获取会话历史（包含系统提示）
                if session_id:
                    try:
                        async with httpx.AsyncClient(timeout=5.0) as history_client:
                            history_response = await history_client.get(
                                f"{settings.LLM_SESSION_URL}/sessions/{session_id}/history"
                            )
                            if history_response.status_code == 200:
                                history_data = history_response.json()
                                conversation_history = history_data.get("conversation_history", [])
                                # 提取系统提示词（第一条消息且role为system）
                                for msg in conversation_history:
                                    if msg.get("role") == "system":
                                        system_prompt = msg.get("content")
                                        break
                    except Exception as e:
                        logger.warning(f"获取会话历史失败: {e}")
                
                # 返回完整的RAG结果
                return {
                    "query": request.query,
                    "answer": llm_response.get("response", ""),
                    "sources": [
                        {
                            "chunk_id": r.chunk_id,
                            "document_id": r.document_id,
                            "content": r.content[:200] + "..." if len(r.content) > 200 else r.content,
                            "score": r.score
                        }
                        for r in rag_result.results
                    ],
                    "context_used": rag_result.context,
                    "system_prompt": system_prompt,  # ⭐ 添加系统提示词
                    "query_time": rag_result.query_time,
                    "session_id": session_id
                }
            else:
                logger.error(f"LLM服务调用失败: {response.status_code}, {response.text}")
                raise HTTPException(status_code=500, detail="Failed to generate answer with LLM service")
                
    except Exception as e:
        logger.error(f"生成回答失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Generate answer failed: {str(e)}")


@router.post("/generate/stream")
async def generate_answer_stream(request: DocumentQueryRequest):
    """
    流式生成回答 - 实时返回LLM生成的内容
    
    **功能**：
    - 执行检索和上下文构建
    - 流式调用 llm-session 服务
    - Server-Sent Events (SSE) 格式返回
    """
    from fastapi.responses import StreamingResponse
    import json
    
    async def event_generator():
        try:
            logger.info(f"开始流式生成回答: query='{request.query[:50]}...'")
            
            # 先执行检索和上下文构建
            rag_result = await rag_service.retrieve_and_build_context(request)
            
            # 获取会话历史以提取系统提示词
            session_id = None
            system_prompt = None
            
            # 发送检索结果（包含查询重写信息）
            yield f"data: {json.dumps({
                'type': 'retrieval', 
                'data': {
                    'results_count': len(rag_result.results),
                    'query_time': rag_result.query_time,
                    'original_query': getattr(rag_result, 'original_query', request.query),
                    'rewritten_query': getattr(rag_result, 'rewritten_query', request.query),
                    'context': rag_result.context
                }
            }, ensure_ascii=False)}\n\n"
            
            # 流式调用 llm-session 服务
            import httpx
            from app.core.config import settings
            
            full_answer = ""
            sources_data = []
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream(
                    "POST",
                    f"{settings.LLM_SESSION_URL}/chat/stream",
                    json={
                        "message": request.query,
                        "session_id": getattr(request, 'session_id', None),
                        "query": request.query,
                        "rag_context": rag_result.context if rag_result.context else None
                    }
                ) as stream_response:
                    async for chunk in stream_response.aiter_text():
                        # 直接转发SSE数据
                        yield chunk
                        
                        # 累积完整回答（用于最后的complete事件）
                        if chunk.startswith('data: '):
                            try:
                                chunk_data = json.loads(chunk[6:])  # 移除 "data: " 前缀
                                
                                # 检查是否为llm-session的StreamChunk格式
                                if 'content' in chunk_data and 'is_last' in chunk_data:
                                    # 这是llm-session返回的StreamChunk对象
                                    content = chunk_data.get('content', '')
                                    if content:  # 只累加有内容的块
                                        full_answer += content
                                        
                                    # 当遇到最后一个块时，获取session_id
                                    if chunk_data.get('is_last'):
                                        session_id = chunk_data.get('session_id')
                                        
                            except json.JSONDecodeError:
                                logger.warning(f"无法解析SSE数据: {chunk[:100]}...")
                                continue
                            except Exception as e:
                                logger.error(f"处理SSE数据时出错: {str(e)}")
                                continue
            
            # 尝试获取系统提示词
            if session_id:
                try:
                    async with httpx.AsyncClient(timeout=5.0) as history_client:
                        history_response = await history_client.get(
                            f"{settings.LLM_SESSION_URL}/sessions/{session_id}/history"
                        )
                        if history_response.status_code == 200:
                            history_data = history_response.json()
                            conversation_history = history_data.get("conversation_history", [])
                            for msg in conversation_history:
                                if msg.get("role") == "system":
                                    system_prompt = msg.get("content")
                                    break
                except Exception as e:
                    logger.warning(f"获取会话历史失败: {e}")
            
            # 发送完成事件
            complete_event = {
                'type': 'complete',
                'data': {
                    'answer': full_answer,
                    'sources': [
                        {
                            "chunk_id": r.chunk_id,
                            "document_id": r.document_id,
                            "content": r.content[:200] + "..." if len(r.content) > 200 else r.content,
                            "score": r.score
                        }
                        for r in rag_result.results
                    ],
                    'context_used': rag_result.context,
                    'system_prompt': system_prompt,
                    'query_time': rag_result.query_time,
                    'session_id': session_id,
                    'original_query': getattr(rag_result, 'original_query', request.query),
                    'rewritten_query': getattr(rag_result, 'rewritten_query', request.query)
                }
            }
            yield f"data: {json.dumps(complete_event, ensure_ascii=False)}\n\n"
                        
        except Exception as e:
            logger.error(f"流式生成失败: {str(e)}", exc_info=True)
            error_data = json.dumps({'type': 'error', 'data': {'message': str(e)}}, ensure_ascii=False)
            yield f"data: {error_data}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
