"""
数据库连接和会话管理
支持 SQLite（默认）和可扩展到其他数据库
"""
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import os
from pathlib import Path


class DatabaseManager:
    """数据库管理器 - 支持多种数据库后端"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.Base = declarative_base()
        self._initialize_database()
    
    def _initialize_database(self):
        """初始化数据库连接"""
        db_type = settings.DATABASE_TYPE.lower()
        
        if db_type == "sqlite":
            self._setup_sqlite()
        elif db_type == "postgresql":
            self._setup_postgresql()
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    def _setup_sqlite(self):
        """配置 SQLite 数据库"""
        # 确保数据库目录存在
        db_path = Path(settings.SQLITE_DATABASE_PATH)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # SQLite 连接字符串
        database_url = f"sqlite:///{db_path}"
        
        # 创建引擎（SQLite 不需要连接池）
        self.engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False},  # 允许多线程访问
            echo=settings.DEBUG  # 调试模式显示 SQL
        )
        
        # 启用外键支持
        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
        
        # 创建会话工厂
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
    
    def _setup_postgresql(self):
        """配置 PostgreSQL 数据库"""
        from sqlalchemy import pool
        
        database_url = settings.DATABASE_URL
        
        # 创建引擎（带连接池）
        self.engine = create_engine(
            database_url,
            poolclass=pool.QueuePool,
            pool_size=10,
            max_overflow=20,
            pool_timeout=30,
            pool_recycle=1800,
            pool_pre_ping=True,
            echo=settings.DEBUG
        )
        
        # 创建会话工厂
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
    
    def get_db(self):
        """获取数据库会话依赖（用于 FastAPI Depends）"""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    def create_tables(self):
        """创建所有表"""
        self.Base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self):
        """删除所有表（谨慎使用）"""
        self.Base.metadata.drop_all(bind=self.engine)


# 创建全局实例
db_manager = DatabaseManager()
