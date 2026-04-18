"""
Schedule model (Enterprise only)
"""
from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.core.snowflake import get_snowflake_id


class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(BigInteger, primary_key=True, default=get_snowflake_id)
    workflow_id = Column(BigInteger, ForeignKey("workflows.id"), nullable=False, index=True)
    created_by = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    cron_expression = Column(String(100), nullable=False)  # e.g., "0 9 * * 1-5"
    timezone = Column(String(50), default="Asia/Shanghai", nullable=False)
    is_enabled = Column(Boolean, default=True, nullable=False)
    next_run_at = Column(DateTime, nullable=True)
    last_run_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    workflow = relationship("Workflow", backref="schedules", lazy="selectin")
    creator = relationship("User", backref="schedules", lazy="selectin")

    def __repr__(self):
        return f"<Schedule {self.id} - {self.cron_expression}>"
