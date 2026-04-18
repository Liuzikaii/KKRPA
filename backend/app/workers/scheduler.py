"""
APScheduler-based cron scheduler (replaces Celery Beat).
"""
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select
from app.database import async_session
from app.models.schedule import Schedule
from app.models.task import TaskExecution, TaskStatus, TriggerType
from app.workers.workflow_tasks import execute_workflow_task
from croniter import croniter

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")


async def check_cron_schedules():
    """Check and trigger due cron schedules (runs every 60s)."""
    async with async_session() as db:
        now = datetime.utcnow()
        result = await db.execute(
            select(Schedule).where(
                Schedule.is_enabled == True,
                Schedule.next_run_at <= now,
            )
        )
        schedules = result.scalars().all()

        for schedule in schedules:
            logger.info(f"Triggering scheduled workflow {schedule.workflow_id} (schedule {schedule.id})")

            # Create task execution
            task_exec = TaskExecution(
                workflow_id=schedule.workflow_id,
                triggered_by=schedule.created_by,
                trigger_type=TriggerType.CRON,
                status=TaskStatus.PENDING,
            )
            db.add(task_exec)
            await db.flush()

            # Submit to thread pool
            execute_workflow_task(task_exec.id, schedule.workflow_id)

            # Update schedule
            schedule.last_run_at = now
            cron = croniter(schedule.cron_expression, now)
            schedule.next_run_at = cron.get_next(datetime)

        await db.commit()

        if schedules:
            logger.info(f"Triggered {len(schedules)} scheduled workflows")


def start_scheduler():
    """Start the APScheduler with the cron check job."""
    scheduler.add_job(
        check_cron_schedules,
        trigger=IntervalTrigger(seconds=60),
        id="check_cron_schedules",
        name="Check Cron Schedules",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("APScheduler started - checking cron schedules every 60s")


def stop_scheduler():
    """Shutdown the scheduler."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("APScheduler stopped")
