"""
聊天API路由
"""
from fastapi import APIRouter, HTTPException
from typing import Optional

from app.models.schemas import (
    SendMessageRequest,
    SendMessageResponse,
    StreamChunk
)
from app.services.chat_service import chat_service

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
    responses={404: {"description": "Not found"}},
)


@router.post("/message", response_model=SendMessageResponse)
async def send_message(request: SendMessageRequest):
    """
    发送消息并获取完整响应
    """
    try:
        result = await chat_service.send_message(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")


@router.post("/stream")
async def stream_message(request: SendMessageRequest):
    """
    发送消息并获取流式响应
    使用Server-Sent Events (SSE)
    """
    from fastapi.responses import StreamingResponse
    
    async def generate_stream():
        try:
            async for chunk in chat_service.stream_message(request):
                yield f"data: {chunk.json()}\n\n"
        except Exception as e:
            yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream"
    )
