"""
Task Execution model
"""
import enum
from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base
from app.core.snowflake import get_snowflake_id


class TriggerType(str, enum.Enum):
    MANUAL = "manual"
    CRON = "cron"
    API = "api"


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskExecution(Base):
    __tablename__ = "task_executions"

    id = Column(BigInteger, primary_key=True, default=get_snowflake_id)
    workflow_id = Column(BigInteger, ForeignKey("workflows.id"), nullable=False, index=True)
    triggered_by = Column(BigInteger, ForeignKey("users.id"), nullable=True, index=True)
    trigger_type = Column(String(20), default=TriggerType.MANUAL.value, nullable=False)
    status = Column(String(20), default=TaskStatus.PENDING.value, nullable=False, index=True)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    result = Column(JSON, default=dict)
    logs = Column(Text, default="")
    error = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    workflow = relationship("Workflow", backref="executions", lazy="selectin")
    user = relationship("User", backref="task_executions", lazy="selectin")

    def __repr__(self):
        return f"<TaskExecution {self.id} - {self.status}>"
