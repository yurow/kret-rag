"""
任务管理API路由
"""
from fastapi import APIRouter, HTTPException
from typing import Optional

from app.models.schemas import TaskStatusResponse
from app.services.background_task_service import background_task_service

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={404: {"description": "Not found"}},
)


@router.get("/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """
    获取后台任务状态
    
    - **task_id**: 任务ID
    """
    task_status = background_task_service.get_task_status(task_id)
    
    if not task_status:
        raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")
    
    return TaskStatusResponse(
        task_id=task_status.task_id,
        status=task_status.status,
        progress=task_status.progress,
        message=task_status.message,
        created_at=task_status.created_at,
        updated_at=task_status.updated_at,
        error=task_status.error
    )


@router.get("/")
async def list_tasks(status_filter: Optional[str] = None):
    """
    列出所有后台任务
    
    - **status_filter**: 状态过滤器（pending/running/completed/failed）
    """
    tasks = background_task_service.list_tasks(status_filter=status_filter)
    
    return {
        "tasks": [
            {
                "task_id": t.task_id,
                "status": t.status,
                "progress": t.progress,
                "message": t.message,
                "created_at": t.created_at.isoformat(),
                "updated_at": t.updated_at.isoformat()
            }
            for t in tasks
        ],
        "total": len(tasks)
    }
