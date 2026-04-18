"""
Schedule API routes (Enterprise only)
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from croniter import croniter
from app.database import get_db
from app.models.user import User
from app.models.workflow import Workflow
from app.models.schedule import Schedule
from app.core.auth import get_current_user, require_edition
from app.schemas.schemas import (
    ScheduleCreate, ScheduleUpdate, ScheduleResponse, MessageResponse,
)

router = APIRouter(prefix="/api/schedules", tags=["Schedules (Enterprise)"])


@router.get("", response_model=list[ScheduleResponse])
async def list_schedules(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_edition("enterprise")),
):
    """List all schedules (Enterprise only)."""
    result = await db.execute(
        select(Schedule).where(Schedule.created_by == current_user.id)
        .order_by(Schedule.created_at.desc())
    )
    schedules = result.scalars().all()
    return [ScheduleResponse.model_validate(s) for s in schedules]


@router.post("", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    data: ScheduleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_edition("enterprise")),
):
    """Create a new cron schedule (Enterprise only)."""
    if not croniter.is_valid(data.cron_expression):
        raise HTTPException(status_code=400, detail="Invalid cron expression")

    result = await db.execute(
        select(Workflow).where(Workflow.id == data.workflow_id, Workflow.owner_id == current_user.id)
    )
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    cron = croniter(data.cron_expression, datetime.utcnow())
    next_run = cron.get_next(datetime)

    schedule = Schedule(
        workflow_id=data.workflow_id,
        created_by=current_user.id,
        cron_expression=data.cron_expression,
        timezone=data.timezone,
        is_enabled=data.is_enabled,
        next_run_at=next_run,
    )
    db.add(schedule)
    await db.flush()
    await db.refresh(schedule)
    return ScheduleResponse.model_validate(schedule)


@router.put("/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: int,
    data: ScheduleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_edition("enterprise")),
):
    """Update a schedule (Enterprise only)."""
    result = await db.execute(
        select(Schedule).where(Schedule.id == schedule_id, Schedule.created_by == current_user.id)
    )
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    if data.cron_expression is not None:
        if not croniter.is_valid(data.cron_expression):
            raise HTTPException(status_code=400, detail="Invalid cron expression")
        schedule.cron_expression = data.cron_expression
        cron = croniter(data.cron_expression, datetime.utcnow())
        schedule.next_run_at = cron.get_next(datetime)

    if data.timezone is not None:
        schedule.timezone = data.timezone
    if data.is_enabled is not None:
        schedule.is_enabled = data.is_enabled

    await db.flush()
    await db.refresh(schedule)
    return ScheduleResponse.model_validate(schedule)


@router.delete("/{schedule_id}", response_model=MessageResponse)
async def delete_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_edition("enterprise")),
):
    """Delete a schedule (Enterprise only)."""
    result = await db.execute(
        select(Schedule).where(Schedule.id == schedule_id, Schedule.created_by == current_user.id)
    )
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    await db.delete(schedule)
    return MessageResponse(message="Schedule deleted successfully")
