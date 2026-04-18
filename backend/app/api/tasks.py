"""
Task Execution API routes
"""
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.models.task import TaskExecution, TaskStatus
from app.core.auth import get_current_user
from app.schemas.schemas import TaskExecutionResponse, TaskExecutionListResponse, MessageResponse
import asyncio
import json

router = APIRouter(prefix="/api/tasks", tags=["Task Executions"])


@router.get("", response_model=list[TaskExecutionListResponse])
async def list_tasks(
    workflow_id: int = None,
    status: str = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List task executions, optionally filtered by workflow and status."""
    query = select(TaskExecution).where(TaskExecution.triggered_by == current_user.id)

    if workflow_id:
        query = query.where(TaskExecution.workflow_id == workflow_id)
    if status:
        query = query.where(TaskExecution.status == status)

    query = query.order_by(TaskExecution.created_at.desc()).limit(limit)
    result = await db.execute(query)
    tasks = result.scalars().all()
    return [TaskExecutionListResponse.model_validate(t) for t in tasks]


@router.get("/{task_id}", response_model=TaskExecutionResponse)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get task execution details including logs."""
    result = await db.execute(
        select(TaskExecution).where(
            TaskExecution.id == task_id,
            TaskExecution.triggered_by == current_user.id,
        )
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskExecutionResponse.model_validate(task)


@router.post("/{task_id}/cancel", response_model=MessageResponse)
async def cancel_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cancel a running task."""
    result = await db.execute(
        select(TaskExecution).where(
            TaskExecution.id == task_id,
            TaskExecution.triggered_by == current_user.id,
        )
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.status not in [TaskStatus.PENDING, TaskStatus.RUNNING]:
        raise HTTPException(status_code=400, detail="Task is not in a cancellable state")

    task.status = TaskStatus.CANCELLED
    await db.flush()
    return MessageResponse(message="Task cancelled successfully")
