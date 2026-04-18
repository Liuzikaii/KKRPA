"""
Workflow model
"""
from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Text, Boolean, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base
from app.core.snowflake import get_snowflake_id


class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(BigInteger, primary_key=True, default=get_snowflake_id)
    name = Column(String(200), nullable=False)
    description = Column(Text, default="")
    owner_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    graph_data = Column(JSON, default=dict)  # React Flow nodes + edges
    version = Column(Integer, default=1, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    edition_required = Column(String(20), default="community", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    owner = relationship("User", backref="workflows", lazy="selectin")

    def __repr__(self):
        return f"<Workflow {self.name}>"
