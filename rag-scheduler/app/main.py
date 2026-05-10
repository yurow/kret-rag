"""
KRET-RAG 系统 - RAG调度器
负责文档处理、向量检索、知识库管理
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
from pathlib import Path
import logging

# 配置日志
logger = logging.getLogger(__name__)

app = FastAPI(
    title="KRET-RAG Scheduler",
    description="RAG调度服务 - 文档处理、向量检索、知识库管理",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
from app.routes import documents, query, tasks

app.include_router(documents.router)
app.include_router(query.router)
app.include_router(tasks.router)


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化服务"""
    print("\n" + "=" * 80)
    print("开始初始化 RAG Scheduler 服务...")
    print("=" * 80)
    
    try:
        # 初始化向量服务（包括 ChromaDB 和 Embedding 模型）
        from app.services.vector_service import vector_store_service
        print("正在初始化向量服务...")
        await vector_store_service.initialize()
        print("✅ 向量服务初始化成功")
        
    except Exception as e:
        print(f"❌ 向量服务初始化失败: {e}")
        import traceback
        traceback.print_exc()
        raise
    
    print("=" * 80)
    print("RAG Scheduler 服务初始化完成！")
    print("=" * 80 + "\n")


@app.get("/")
async def root():
    """根路径 - 重定向到上传测试页面"""
    return FileResponse("upload_test.html")

@app.get("/test-query")
async def test_query_page():
    """RAG查询测试页面"""
    return FileResponse("test_query.html")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
