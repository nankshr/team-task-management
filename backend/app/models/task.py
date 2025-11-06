"""
Task model for managing individual tasks and subtasks.
"""
import uuid
from datetime import datetime, date, time
from sqlalchemy import Column, String, Text, DateTime, Date, Time, Boolean, ForeignKey, BigInteger, Enum as SQLEnum, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class TaskType(str, enum.Enum):
    """Task type enumeration."""
    ROUTINE = "routine"
    ONE_TIME = "one_time"


class TaskPriority(str, enum.Enum):
    """Task priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(str, enum.Enum):
    """Task status enumeration."""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    OVERDUE = "overdue"


# Association table for task-label many-to-many relationship
task_labels = Table(
    'task_labels',
    Base.metadata,
    Column('task_id', UUID(as_uuid=True), ForeignKey('tasks.id'), primary_key=True),
    Column('label_id', UUID(as_uuid=True), ForeignKey('employee_labels.id'), primary_key=True)
)


class Task(Base):
    """
    Task model for tracking work assignments.
    Supports both routine and one-time tasks, with subtask capability.
    """
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    task_number = Column(String(20), unique=True, nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    task_type = Column(SQLEnum(TaskType), nullable=False, default=TaskType.ONE_TIME)
    priority = Column(SQLEnum(TaskPriority), nullable=False, default=TaskPriority.MEDIUM)
    status = Column(SQLEnum(TaskStatus), nullable=False, default=TaskStatus.PENDING, index=True)
    due_date = Column(Date, nullable=False, index=True)
    due_time = Column(Time, nullable=True)

    # Assignment tracking
    assigned_to = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True, index=True)
    assigned_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)

    # Subtask support
    parent_task_id = Column(UUID(as_uuid=True), ForeignKey('tasks.id'), nullable=True, index=True)
    is_subtask = Column(Boolean, default=False, nullable=False)

    # Telegram tracking
    telegram_message_id = Column(BigInteger, nullable=True)

    # Timestamps
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    assigned_employee = relationship("Employee", back_populates="tasks", foreign_keys=[assigned_to])
    assigner = relationship("User", foreign_keys=[assigned_by])
    creator = relationship("User", foreign_keys=[created_by])

    # Self-referential relationship for subtasks
    parent_task = relationship("Task", remote_side=[id], backref="subtasks")

    # Comments
    comments = relationship("TaskComment", back_populates="task", cascade="all, delete-orphan")

    # Labels
    labels = relationship(
        "EmployeeLabel",
        secondary=task_labels,
        backref="tasks"
    )

    def __repr__(self) -> str:
        return f"<Task(task_number='{self.task_number}', title='{self.title}', status='{self.status}')>"


class CommentType(str, enum.Enum):
    """Comment type enumeration."""
    GENERAL = "general"
    ISSUE_REPORT = "issue_report"
    CLARIFICATION = "clarification"


class TaskComment(Base):
    """
    Comments on tasks from employees or users.
    """
    __tablename__ = "task_comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    task_id = Column(UUID(as_uuid=True), ForeignKey('tasks.id'), nullable=False, index=True)
    comment_by_employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)
    comment_by_user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    comment_text = Column(Text, nullable=False)
    comment_type = Column(SQLEnum(CommentType), nullable=False, default=CommentType.GENERAL)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    task = relationship("Task", back_populates="comments")
    employee = relationship("Employee")
    user = relationship("User")

    def __repr__(self) -> str:
        return f"<TaskComment(task_id={self.task_id}, type='{self.comment_type}')>"
