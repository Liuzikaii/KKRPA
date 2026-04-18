"""
Workflow CRUD API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.user import User
from app.models.workflow import Workflow
from app.models.task import TaskExecution, TaskStatus as TS, TriggerType
from app.core.auth import get_current_user
from app.core.edition import check_feature_access, Feature, get_edition_limits
from app.schemas.schemas import (
    WorkflowCreate, WorkflowUpdate, WorkflowResponse,
    WorkflowListResponse, TaskExecutionListResponse, MessageResponse,
)

router = APIRouter(prefix="/api/workflows", tags=["Workflows"])


@router.get("", response_model=list[WorkflowListResponse])
async def list_workflows(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all workflows owned by the current user."""
    result = await db.execute(
        select(Workflow)
        .where(Workflow.owner_id == current_user.id)
        .order_by(Workflow.updated_at.desc())
    )
    workflows = result.scalars().all()
    return [WorkflowListResponse.model_validate(w) for w in workflows]


@router.post("", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    data: WorkflowCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new workflow. Community edition checks workflow count limit."""
    # Check community limit
    if current_user.edition == "community":
        limits = get_edition_limits(current_user.edition)
        count_result = await db.execute(
            select(func.count(Workflow.id)).where(Workflow.owner_id == current_user.id)
        )
        count = count_result.scalar()
        if count >= limits["max_workflows"]:
            raise HTTPException(
                status_code=403,
                detail=f"Community edition is limited to {limits['max_workflows']} workflows. Upgrade to Enterprise for unlimited.",
            )

    workflow = Workflow(
        name=data.name,
        description=data.description,
        owner_id=current_user.id,
        graph_data=data.graph_data,
    )
    db.add(workflow)
    await db.flush()
    await db.refresh(workflow)
    return WorkflowResponse.model_validate(workflow)


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get workflow details."""
    workflow = await _get_user_workflow(db, workflow_id, current_user)
    return WorkflowResponse.model_validate(workflow)


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: int,
    data: WorkflowUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a workflow."""
    workflow = await _get_user_workflow(db, workflow_id, current_user)

    if data.name is not None:
        workflow.name = data.name
    if data.description is not None:
        workflow.description = data.description
    if data.graph_data is not None:
        workflow.graph_data = data.graph_data
        workflow.version += 1
    if data.is_active is not None:
        workflow.is_active = data.is_active

    await db.flush()
    await db.refresh(workflow)
    return WorkflowResponse.model_validate(workflow)


@router.delete("/{workflow_id}", response_model=MessageResponse)
async def delete_workflow(
    workflow_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a workflow."""
    workflow = await _get_user_workflow(db, workflow_id, current_user)
    await db.delete(workflow)
    return MessageResponse(message="Workflow deleted successfully")


@router.post("/{workflow_id}/execute", response_model=TaskExecutionListResponse)
async def execute_workflow(
    workflow_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Manually execute a workflow."""
    workflow = await _get_user_workflow(db, workflow_id, current_user)
    if not workflow.is_active:
        raise HTTPException(status_code=400, detail="Workflow is not active")

    # Create task execution record
    task = TaskExecution(
        workflow_id=workflow.id,
        triggered_by=current_user.id,
        trigger_type=TriggerType.MANUAL,
        status=TS.PENDING,
    )
    db.add(task)
    await db.flush()
    await db.refresh(task)

    # Dispatch to thread pool executor
    from app.workers.workflow_tasks import execute_workflow_task
    execute_workflow_task(task.id, workflow.id)

    return TaskExecutionListResponse.model_validate(task)


async def _get_user_workflow(db: AsyncSession, workflow_id: int, user: User) -> Workflow:
    """Helper to get a workflow owned by the current user."""
    result = await db.execute(
        select(Workflow).where(Workflow.id == workflow_id, Workflow.owner_id == user.id)
    )
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow
