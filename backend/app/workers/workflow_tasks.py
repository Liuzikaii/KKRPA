"""
Workflow execution tasks using ThreadPoolExecutor (replaces Celery).
"""
import asyncio
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session
from app.engine.executor import WorkflowExecutor
from app.models.task import TaskExecution, TaskStatus
from app.models.workflow import Workflow

logger = logging.getLogger(__name__)

# Thread pool for background workflow execution
_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="kkrpa-worker")


def _run_async(coro):
    """Run async coroutine in a new event loop (for thread pool)."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def _execute_workflow_async(task_execution_id: int, workflow_id: int):
    """Execute a workflow and update task status (async)."""
    async with async_session() as db:
        # Get task execution
        result = await db.execute(
            select(TaskExecution).where(TaskExecution.id == task_execution_id)
        )
        task_exec = result.scalar_one_or_none()
        if not task_exec:
            logger.error(f"TaskExecution {task_execution_id} not found")
            return

        # Get workflow
        result = await db.execute(
            select(Workflow).where(Workflow.id == workflow_id)
        )
        workflow = result.scalar_one_or_none()
        if not workflow:
            task_exec.status = TaskStatus.FAILED
            task_exec.error = "Workflow not found"
            await db.commit()
            return

        # Mark as running
        task_exec.status = TaskStatus.RUNNING
        task_exec.started_at = datetime.utcnow()
        await db.commit()

        try:
            # Execute
            executor = WorkflowExecutor(workflow.graph_data or {"nodes": [], "edges": []})
            exec_result = await executor.execute()

            # Update results
            task_exec.result = exec_result.get("results", {})
            task_exec.logs = exec_result.get("logs", "")
            task_exec.finished_at = datetime.utcnow()

            if exec_result["success"]:
                task_exec.status = TaskStatus.SUCCESS
            else:
                task_exec.status = TaskStatus.FAILED
                task_exec.error = "\n".join(exec_result.get("errors", []))

            await db.commit()
            logger.info(f"Workflow {workflow_id} execution {'succeeded' if exec_result['success'] else 'failed'}")

        except Exception as e:
            task_exec.status = TaskStatus.FAILED
            task_exec.error = str(e)
            task_exec.finished_at = datetime.utcnow()
            await db.commit()
            logger.error(f"Workflow {workflow_id} execution error: {e}")


def execute_workflow_task(task_execution_id: int, workflow_id: int):
    """Submit workflow execution to thread pool."""
    _executor.submit(_run_async, _execute_workflow_async(task_execution_id, workflow_id))
    logger.info(f"Submitted workflow {workflow_id} (task {task_execution_id}) to thread pool")
