"""
后台任务服务
用于处理耗时的异步任务，如向量化、OCR等
"""
import asyncio
import logging
from typing import Callable, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


@dataclass
class TaskStatus:
    """任务状态"""
    task_id: str
    status: str  # 'pending', 'running', 'completed', 'failed'
    progress: float = 0.0  # 0-100
    message: str = ""
    result: Any = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class BackgroundTaskService:
    """后台任务服务"""
    
    def __init__(self):
        self.tasks: dict[str, TaskStatus] = {}
    
    async def submit_task(
        self,
        task_func: Callable,
        *args,
        **kwargs
    ) -> str:
        """
        提交后台任务
        
        Args:
            task_func: 要执行的异步函数
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            str: 任务ID
        """
        task_id = str(uuid.uuid4())
        
        # 创建任务状态
        task_status = TaskStatus(
            task_id=task_id,
            status='pending',
            message='任务已提交，等待执行'
        )
        self.tasks[task_id] = task_status
        
        logger.info(f"后台任务已提交: {task_id}")
        
        # 异步执行任务
        asyncio.create_task(self._execute_task(task_id, task_func, *args, **kwargs))
        
        return task_id
    
    async def _execute_task(
        self,
        task_id: str,
        task_func: Callable,
        *args,
        **kwargs
    ):
        """
        执行后台任务
        
        Args:
            task_id: 任务ID
            task_func: 要执行的函数
            *args: 位置参数
            **kwargs: 关键字参数
        """
        task_status = self.tasks[task_id]
        
        try:
            # 更新状态为运行中
            task_status.status = 'running'
            task_status.progress = 0.0
            task_status.message = '任务正在执行'
            task_status.updated_at = datetime.now()
            
            logger.info(f"开始执行后台任务: {task_id}")
            
            # 执行任务
            result = await task_func(*args, **kwargs)
            
            # 更新状态为完成
            task_status.status = 'completed'
            task_status.progress = 100.0
            task_status.message = '任务执行成功'
            task_status.result = result
            task_status.updated_at = datetime.now()
            
            logger.info(f"后台任务执行完成: {task_id}")
            
        except Exception as e:
            # 更新状态为失败
            task_status.status = 'failed'
            task_status.message = f'任务执行失败: {str(e)}'
            task_status.error = str(e)
            task_status.updated_at = datetime.now()
            
            logger.error(f"后台任务执行失败: {task_id}, 错误: {str(e)}", exc_info=True)
    
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """
        获取任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            TaskStatus: 任务状态，如果不存在则返回 None
        """
        return self.tasks.get(task_id)
    
    def list_tasks(self, status_filter: Optional[str] = None) -> list[TaskStatus]:
        """
        列出所有任务
        
        Args:
            status_filter: 状态过滤器（可选）
            
        Returns:
            list[TaskStatus]: 任务列表
        """
        tasks = list(self.tasks.values())
        
        if status_filter:
            tasks = [t for t in tasks if t.status == status_filter]
        
        # 按创建时间倒序排列
        tasks.sort(key=lambda x: x.created_at, reverse=True)
        
        return tasks


# 创建全局实例
background_task_service = BackgroundTaskService()
