"""
Pydantic schemas for API request/response validation
"""
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, EmailStr, Field


# ==================== Auth ====================

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    edition: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ==================== Workflow ====================

class WorkflowCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = ""
    graph_data: dict = Field(default_factory=lambda: {"nodes": [], "edges": []})


class WorkflowUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    graph_data: Optional[dict] = None
    is_active: Optional[bool] = None


class WorkflowResponse(BaseModel):
    id: int
    name: str
    description: str
    owner_id: int
    graph_data: dict
    version: int
    is_active: bool
    edition_required: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WorkflowListResponse(BaseModel):
    id: int
    name: str
    description: str
    version: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== Task Execution ====================

class TaskExecutionResponse(BaseModel):
    id: int
    workflow_id: int
    triggered_by: Optional[int]
    trigger_type: str
    status: str
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    result: dict
    logs: str
    error: str
    created_at: datetime

    class Config:
        from_attributes = True


class TaskExecutionListResponse(BaseModel):
    id: int
    workflow_id: int
    trigger_type: str
    status: str
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Schedule (Enterprise) ====================

class ScheduleCreate(BaseModel):
    workflow_id: int
    cron_expression: str = Field(..., min_length=9, max_length=100)
    timezone: str = "Asia/Shanghai"
    is_enabled: bool = True


class ScheduleUpdate(BaseModel):
    cron_expression: Optional[str] = None
    timezone: Optional[str] = None
    is_enabled: Optional[bool] = None


class ScheduleResponse(BaseModel):
    id: int
    workflow_id: int
    created_by: int
    cron_expression: str
    timezone: str
    is_enabled: bool
    next_run_at: Optional[datetime]
    last_run_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== Common ====================

class PaginatedResponse(BaseModel):
    items: list[Any]
    total: int
    page: int
    page_size: int
    total_pages: int


class MessageResponse(BaseModel):
    message: str


class EditionInfoResponse(BaseModel):
    edition: str
    features: list[str]
    limits: dict
