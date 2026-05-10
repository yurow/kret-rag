"""
查询重写服务
用于优化用户查询，提升检索效果
"""
from typing import Optional, List
import logging
import re

logger = logging.getLogger(__name__)


class QueryRewriteService:
    """查询重写服务"""
    
    def __init__(self):
        self.stopwords = self._load_stopwords()
    
    def _load_stopwords(self) -> set:
        """加载中文停用词表"""
        # 常用中文停用词
        return {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个',
            '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好',
            '自己', '这', '他', '她', '它', '们', '那', '些', '什么', '怎么', '如何', '为什么',
            '吗', '呢', '吧', '啊', '哦', '嗯', '呀', '哇', '哈', '嘿'
        }
    
    def rewrite_query(self, query: str) -> str:
        """
        重写查询，优化检索效果
        
        策略：
        1. 去除停用词和标点符号
        2. 提取关键词
        3. 扩展同义词（可选）
        4. 规范化格式
        
        Args:
            query: 原始查询
            
        Returns:
            str: 重写后的查询
        """
        try:
            logger.debug(f"原始查询: {query}")
            
            # 1. 清理特殊字符，保留中文、英文、数字
            cleaned = re.sub(r'[^\w\s\u4e00-\u9fff]', ' ', query)
            
            # 2. 分词（简单按空格和中文边界）
            import jieba
            words = list(jieba.cut(cleaned))
            
            # 3. 过滤停用词和单字符
            keywords = [
                w.strip() for w in words 
                if w.strip() and len(w.strip()) > 1 and w.strip() not in self.stopwords
            ]
            
            if not keywords:
                # 如果过滤后没有关键词，返回原始查询
                logger.warning("查询过滤后无关键词，使用原始查询")
                return query
            
            # 4. 重新组合
            rewritten = ' '.join(keywords)
            
            logger.debug(f"重写后查询: {rewritten}")
            return rewritten
            
        except Exception as e:
            logger.error(f"查询重写失败: {str(e)}", exc_info=True)
            # 降级：返回原始查询
            return query
    
    def expand_query_with_synonyms(self, query: str) -> List[str]:
        """
        扩展查询，添加同义词变体
        
        Args:
            query: 原始查询
            
        Returns:
            List[str]: 查询变体列表
        """
        variants = [query]
        
        # 简单的同义词映射（可以扩展到更大的词库）
        synonym_map = {
            '机器学习': ['ML', 'machine learning'],
            '深度学习': ['DL', 'deep learning'],
            '人工智能': ['AI', 'artificial intelligence'],
            '神经网络': ['NN', 'neural network'],
            '自然语言处理': ['NLP', 'natural language processing'],
        }
        
        for term, synonyms in synonym_map.items():
            if term in query:
                for synonym in synonyms:
                    variant = query.replace(term, synonym)
                    if variant != query:
                        variants.append(variant)
        
        logger.debug(f"查询扩展: {query} -> {variants}")
        return variants
    
    def detect_query_type(self, query: str) -> str:
        """
        检测查询类型
        
        Args:
            query: 用户查询
            
        Returns:
            str: 查询类型 ('definition', 'comparison', 'howto', 'fact', 'other')
        """
        query_lower = query.lower()
        
        # 定义类问题
        if any(word in query_lower for word in ['什么是', '定义', '含义', '意思']):
            return 'definition'
        
        # 比较类问题
        if any(word in query_lower for word in ['区别', '对比', 'vs', 'versus', '哪个更好']):
            return 'comparison'
        
        # 方法类问题
        if any(word in query_lower for word in ['如何', '怎么', '怎样', '步骤', '方法']):
            return 'howto'
        
        # 事实类问题
        if any(word in query_lower for word in ['谁', '哪里', '什么时候', '多少', '几']):
            return 'fact'
        
        return 'other'


# 创建全局实例
query_rewrite_service = QueryRewriteService()
