"""
Notification model for tracking sent messages.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class NotificationType(str, enum.Enum):
    """Notification type enumeration."""
    TASK_ASSIGNED = "task_assigned"
    TASK_COMPLETED = "task_completed"
    ATTENDANCE_REMINDER = "attendance_reminder"
    TASK_OVERDUE = "task_overdue"
    DAILY_REPORT = "daily_report"
    SUBTASK_CREATED = "subtask_created"
    BLOCKER_RESOLVED = "blocker_resolved"


class Notification(Base):
    """
    Notification log for tracking sent messages to employees and owner.
    """
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    notification_type = Column(SQLEnum(NotificationType), nullable=False, index=True)
    recipient_employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True, index=True)
    recipient_user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True, index=True)
    message = Column(Text, nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    read_at = Column(DateTime, nullable=True)

    # Relationships
    recipient_employee = relationship("Employee")
    recipient_user = relationship("User")

    def __repr__(self) -> str:
        return f"<Notification(type='{self.notification_type}', sent_at={self.sent_at})>"
