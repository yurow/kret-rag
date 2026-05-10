"""
KRET-RAG 系统 - LLM会话管理服务
负责对话管理、上下文维护、模型调用
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(
    title="KRET-RAG LLM Session Manager",
    description="LLM会话管理服务 - 对话历史、上下文维护、模型调用",
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
from app.routes import chat, sessions, llm_config

app.include_router(chat.router)
app.include_router(sessions.router)
app.include_router(llm_config.router)

@app.get("/")
async def root():
    return {
        "service": "LLM Session Manager",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
