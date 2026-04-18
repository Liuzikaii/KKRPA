"""
User model
"""
import enum
from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Boolean, DateTime
from app.database import Base
from app.core.snowflake import get_snowflake_id


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


class Edition(str, enum.Enum):
    COMMUNITY = "community"
    ENTERPRISE = "enterprise"


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, default=get_snowflake_id)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default=UserRole.EDITOR.value, nullable=False)
    edition = Column(String(20), default=Edition.COMMUNITY.value, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"
