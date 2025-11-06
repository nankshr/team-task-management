"""
Pydantic schemas for Task and TaskComment models.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, date, time
from uuid import UUID

from app.models.task import TaskType, TaskPriority, TaskStatus, CommentType


# Task Comment Schemas
class TaskCommentBase(BaseModel):
    """Base task comment schema."""
    comment_text: str = Field(..., min_length=1)
    comment_type: CommentType = CommentType.GENERAL


class TaskCommentCreate(TaskCommentBase):
    """Schema for creating a task comment."""
    task_id: UUID
    comment_by_employee_id: Optional[UUID] = None
    comment_by_user_id: Optional[UUID] = None


class TaskCommentResponse(TaskCommentBase):
    """Schema for task comment response."""
    id: UUID
    task_id: UUID
    comment_by_employee_id: Optional[UUID] = None
    comment_by_user_id: Optional[UUID] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Task Schemas
class TaskBase(BaseModel):
    """Base task schema."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    task_type: TaskType = TaskType.ONE_TIME
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: date
    due_time: Optional[time] = None


class TaskCreate(TaskBase):
    """Schema for creating a task."""
    assigned_to: Optional[UUID] = None
    label_ids: Optional[List[UUID]] = []
    parent_task_id: Optional[UUID] = None


class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    due_date: Optional[date] = None
    due_time: Optional[time] = None
    assigned_to: Optional[UUID] = None
    label_ids: Optional[List[UUID]] = None


class TaskResponse(TaskBase):
    """Schema for task response."""
    id: UUID
    task_number: str
    status: TaskStatus
    assigned_to: Optional[UUID] = None
    assigned_by: Optional[UUID] = None
    created_by: Optional[UUID] = None
    parent_task_id: Optional[UUID] = None
    is_subtask: bool
    telegram_message_id: Optional[int] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskDetailResponse(TaskResponse):
    """Schema for detailed task response with comments and subtasks."""
    comments: List[TaskCommentResponse] = []
    subtasks: List[TaskResponse] = []


class TaskComplete(BaseModel):
    """Schema for marking a task as complete."""
    task_id: UUID


class TaskAssign(BaseModel):
    """Schema for assigning a task to an employee."""
    employee_id: UUID


class TaskCreateSubtask(TaskBase):
    """Schema for creating a subtask."""
    parent_task_id: UUID
