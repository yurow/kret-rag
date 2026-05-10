"""
RAG调度器配置模块
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional


# 设置 HuggingFace 国内镜像（必须在导入任何 huggingface 相关库之前设置）
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"


class Settings(BaseSettings):
    """应用配置"""
    
    # 服务配置
    APP_NAME: str = "KRET-RAG Scheduler"
    APP_VERSION: str = "1.0.0"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 数据库配置
    DATABASE_TYPE: str = "sqlite"  # sqlite, postgresql
    DATABASE_URL: str = "sqlite:///./data/documents.db"
    SQLITE_DATABASE_PATH: str = "./data/documents.db"
    
    # 向量数据库配置
    VECTOR_DB_TYPE: str = "chromadb"  # chromadb, milvus, qdrant
    CHROMA_HOST: str = "./data/chromadb"  # ChromaDB 持久化存储路径
    CHROMA_PORT: int = 8001
    CHROMA_COLLECTION_NAME: str = "rag_collection"
    
    # Embedding配置
    # 推荐使用本地模型路径（需先运行 download_embedding_model.py 下载）
    # 优势：启动快、离线可用、版本稳定
    EMBEDDING_MODEL: str = "./models/all-MiniLM-L6-v2"
    
    # 备选：使用在线模型（自动从 HuggingFace 下载）
    # EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    EMBEDDING_DIMENSION: int = 384
    
    # ⚠️ Reranker 模型配置已注释 - 调试基础流程时不需要
    # RERANKER_MODEL: str = "./models/bge-reranker-base"
    # RERANKER_MODEL: str = "BAAI/bge-reranker-base"
    
    # HuggingFace 配置
    HF_ENDPOINT: str = "https://hf-mirror.com"  # HuggingFace 镜像地址
    
    # LLM服务配置（调用llm-session服务）
    LLM_SESSION_URL: str = "http://localhost:9000"
    
    # 文档处理配置
    MAX_DOCUMENT_SIZE: int = 10485760  # 10MB
    SUPPORTED_FORMATS: list = ["pdf", "docx", "doc", "pptx", "ppt", "xlsx", "xls", "txt", "md", "csv"]
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    
    # 文件存储配置
    UPLOAD_DIR: str = "./uploads"
    ALLOWED_EXTENSIONS: set = {"pdf", "docx", "doc", "pptx", "ppt", "xlsx", "xls", "txt", "md", "csv"}
    
    # Redis配置（用于缓存）
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # 调试模式
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
