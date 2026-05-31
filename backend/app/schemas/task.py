from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.enums import Category, Priority, Status


class TaskBase(BaseModel):
    task_name: str = Field(..., min_length=1, max_length=200)
    deadline: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    priority: Priority = Priority.medium
    category: Category = Category.general
    status: Status = Status.pending


class TaskCreate(TaskBase):
    """手动创建任务，不关联邮件"""
    pass


class TaskUpdate(BaseModel):
    task_name: Optional[str] = Field(None, min_length=1, max_length=200)
    deadline: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    priority: Optional[Priority] = None
    category: Optional[Category] = None
    status: Optional[Status] = None


class TaskStatusUpdate(BaseModel):
    status: Status


class TaskOut(BaseModel):
    id: int
    email_id: Optional[int] = None
    task_name: str
    deadline: str
    priority: Priority
    status: Status
    category: Category
    confidence: float
    confidence_source: str
    created_at: datetime
    email_subject: Optional[str] = None
    email_sender: Optional[str] = None

    model_config = {"from_attributes": True}
