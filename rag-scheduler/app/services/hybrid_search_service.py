"""
混合检索服务
整合 BM25 关键词检索和向量语义检索
注意：Rerank 重排序功能已暂时禁用，用于调试基础流程
"""
from typing import List, Dict, Any, Optional, Tuple
import logging
import jieba
from rank_bm25 import BM25Okapi
import numpy as np

from app.models.schemas import VectorSearchResult
from app.core.config import settings

logger = logging.getLogger(__name__)


class HybridRetrievalService:
    """混合检索服务（BM25 + 向量）"""
    
    def __init__(self):
        self.bm25_index = None
        self.documents = []
        self.document_ids = []
        self.is_initialized = False
    
    def initialize(self, documents: List[str], document_ids: List[str]):
        """
        初始化 BM25 索引
        
        Args:
            documents: 文档列表
            document_ids: 文档ID列表
        """
        try:
            logger.info(f"初始化 BM25 索引，共 {len(documents)} 个文档")
            
            # 对中文文档进行分词
            tokenized_docs = []
            for doc in documents:
                # 使用 jieba 进行中文分词
                tokens = list(jieba.cut(doc))
                # 过滤掉停用词和单字符
                tokens = [t for t in tokens if len(t.strip()) > 1]
                tokenized_docs.append(tokens)
            
            # 创建 BM25 索引
            self.bm25_index = BM25Okapi(tokenized_docs)
            self.documents = documents
            self.document_ids = document_ids
            self.is_initialized = True
            
            logger.info("BM25 索引初始化成功")
            
        except Exception as e:
            logger.error(f"BM25 索引初始化失败: {str(e)}", exc_info=True)
            raise
    
    def bm25_search(
        self, 
        query: str, 
        top_k: int = 20
    ) -> List[Tuple[str, float]]:
        """
        BM25 关键词搜索
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            
        Returns:
            List[Tuple[str, float]]: (document_id, score) 列表
        """
        if not self.is_initialized:
            raise RuntimeError("BM25 索引未初始化")
        
        try:
            # 对查询进行分词
            query_tokens = list(jieba.cut(query))
            query_tokens = [t for t in query_tokens if len(t.strip()) > 1]
            
            # 执行 BM25 搜索
            scores = self.bm25_index.get_scores(query_tokens)
            
            # 获取 Top-K 结果
            top_indices = np.argsort(scores)[-top_k:][::-1]
            
            results = []
            for idx in top_indices:
                if scores[idx] > 0:  # 只返回有分数的结果
                    results.append((self.document_ids[idx], float(scores[idx])))
            
            logger.debug(f"BM25 搜索完成，找到 {len(results)} 个结果")
            return results
            
        except Exception as e:
            logger.error(f"BM25 搜索失败: {str(e)}", exc_info=True)
            return []
    
    @staticmethod
    def normalize_scores(scores: List[float]) -> List[float]:
        """
        归一化分数到 0-1 范围
        
        Args:
            scores: 原始分数列表
            
        Returns:
            List[float]: 归一化后的分数
        """
        if not scores:
            return []
        
        min_score = min(scores)
        max_score = max(scores)
        
        if max_score == min_score:
            return [0.5] * len(scores)
        
        return [(s - min_score) / (max_score - min_score) for s in scores]


# ============================================================================
# ⚠️ RerankerService 类已注释 - 用于调试基础检索流程
# ============================================================================
# class RerankerService:
#     """重排序服务（使用 Cross-Encoder）"""
#     
#     def __init__(self):
#         self.model = None
#         self.is_initialized = False
#     
#     async def initialize(self, model_name: str = None):
#         """
#         初始化 Reranker 模型
#         
#         Args:
#             model_name: 模型名称，默认从配置文件读取
#         """
#         try:
#             # 从配置文件获取模型路径
#             if model_name is None:
#                 from app.core.config import settings
#                 model_name = settings.RERANKER_MODEL
#             
#             logger.info(f"加载 Reranker 模型: {model_name}")
#             
#             # 检查是否为本地路径
#             if os.path.exists(model_name):
#                 logger.info(f"使用本地模型: {os.path.abspath(model_name)}")
#             else:
#                 logger.warning(f"本地模型不存在: {model_name}，将尝试从网络下载")
#                 # 设置 HuggingFace 国内镜像（如果环境变量中已配置）
#                 if not os.environ.get('HF_ENDPOINT'):
#                     os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
#                     logger.info("已设置 HuggingFace 国内镜像: https://hf-mirror.com")
#             
#             from FlagEmbedding import FlagReranker
#             
#             self.model = FlagReranker(model_name, use_fp16=True)
#             self.is_initialized = True
#             logger.info("Reranker 模型加载成功")
#             
#         except ImportError:
#             logger.warning("FlagEmbedding 未安装，Rerank 功能不可用")
#             logger.info("如需启用 Rerank，请安装: pip install FlagEmbedding")
#         except Exception as e:
#             logger.error(f"Reranker 模型加载失败: {str(e)}", exc_info=True)
#     
#     async def rerank(
#         self,
#         query: str,
#         passages: List[str],
#         top_k: int = 5
#     ) -> List[Tuple[int, float]]:
#         """
#         对候选段落进行重排序
#         
#         Args:
#             query: 查询文本
#             passages: 候选段落列表
#             top_k: 返回结果数量
#             
#         Returns:
#             List[Tuple[int, float]]: (原始索引, 重排分数) 列表
#         """
#         if not self.is_initialized or not self.model:
#             logger.warning("Reranker 未初始化，跳过重排序")
#             # 返回原始顺序
#             return [(i, 1.0 - i * 0.1) for i in range(min(top_k, len(passages)))]
#         
#         try:
#             # 构建查询-段落对
#             pairs = [[query, passage] for passage in passages]
#             
#             # 计算相关性分数
#             scores = self.model.compute_score(pairs, normalize=True)
#             
#             # 获取 Top-K 结果的索引和分数
#             indexed_scores = list(enumerate(scores))
#             sorted_results = sorted(indexed_scores, key=lambda x: x[1], reverse=True)
#             
#             return sorted_results[:top_k]
#             
#         except Exception as e:
#             logger.error(f"Rerank 失败: {str(e)}", exc_info=True)
#             # 降级：返回原始顺序
#             return [(i, 1.0 - i * 0.1) for i in range(min(top_k, len(passages)))]


class HybridSearchService:
    """混合搜索服务（BM25 + 向量，Rerank 已禁用）"""
    
    def __init__(self):
        self.bm25_service = HybridRetrievalService()
        # ⚠️ Reranker 服务已禁用
        # self.reranker_service = RerankerService()
    
    async def initialize(self, documents: List[str], document_ids: List[str]):
        """
        初始化混合搜索服务
        
        Args:
            documents: 所有文档内容列表
            document_ids: 对应的文档ID列表
        """
        # 初始化 BM25
        self.bm25_service.initialize(documents, document_ids)
        
        # ⚠️ Reranker 初始化已禁用
        # await self.reranker_service.initialize()
        logger.info("混合搜索服务初始化完成（BM25 + 向量，Rerank 已禁用）")
    
    async def hybrid_search(
        self,
        query: str,
        vector_results: List[VectorSearchResult],
        top_k: int = 5,
        bm25_weight: float = 0.3,
        vector_weight: float = 0.7,
        use_rerank: bool = False  # ⚠️ 参数保留但始终为False
    ) -> List[VectorSearchResult]:
        """
        混合搜索：结合 BM25 和向量检索
        注意：Rerank 重排序已禁用，仅用于调试基础流程
        
        Args:
            query: 查询文本
            vector_results: 向量检索结果
            top_k: 最终返回结果数量
            bm25_weight: BM25 权重（预留，暂未实现融合）
            vector_weight: 向量检索权重（预留，暂未实现融合）
            use_rerank: 是否使用 Rerank 重排（已禁用，忽略此参数）
            
        Returns:
            List[VectorSearchResult]: 搜索结果
        """
        try:
            logger.info(f"开始混合搜索: query='{query[:50]}...', 向量结果数={len(vector_results)}")
            
            if not vector_results:
                logger.warning("向量检索结果为空，返回空列表")
                return []
            
            # ⚠️ Rerank 已禁用，直接返回向量检索结果
            logger.info("Rerank 已禁用，直接返回向量检索结果")
            return vector_results[:top_k]
            
        except Exception as e:
            logger.error(f"混合搜索失败: {str(e)}", exc_info=True)
            # 降级：返回原始向量结果
            return vector_results[:top_k]


# 创建全局实例
hybrid_search_service = HybridSearchService()
