"""
会话管理API路由
"""
from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    CreateSessionRequest,
    CreateSessionResponse,
    SessionInfo,
    ListSessionsResponse
)
from app.services.session_service import session_service

router = APIRouter(
    prefix="/sessions",
    tags=["sessions"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=CreateSessionResponse)
async def create_session(request: CreateSessionRequest):
    """创建新会话"""
    try:
        session_info = await session_service.create_session(request)
        return CreateSessionResponse(
            session_id=session_info.session_id,
            message="Session created successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")


@router.get("/{session_id}", response_model=SessionInfo)
async def get_session(session_id: str):
    """获取会话信息"""
    session = await session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.get("/", response_model=ListSessionsResponse)
async def list_sessions(
    user_id: str = None,
    page: int = 1,
    page_size: int = 10
):
    """列出所有会话"""
    sessions = await session_service.list_sessions(
        user_id=user_id,
        page=page,
        page_size=page_size
    )
    
    return ListSessionsResponse(
        sessions=sessions,
        total=len(sessions)
    )


@router.delete("/{session_id}")
async def delete_session(session_id: str):
    """删除会话"""
    success = await session_service.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session deleted successfully"}


@router.post("/{session_id}/close")
async def close_session(session_id: str):
    """关闭会话"""
    success = await session_service.close_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session closed successfully"}
