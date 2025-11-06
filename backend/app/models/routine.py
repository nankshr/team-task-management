"""
Routine model for recurring task templates.
"""
import uuid
from datetime import datetime, time
from sqlalchemy import Column, String, Text, DateTime, Time, Integer, Boolean, ForeignKey, Enum as SQLEnum, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class RecurrenceType(str, enum.Enum):
    """Recurrence type enumeration."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


# Association table for routine-label many-to-many relationship
routine_labels = Table(
    'routine_labels',
    Base.metadata,
    Column('routine_id', UUID(as_uuid=True), ForeignKey('routines.id'), primary_key=True),
    Column('label_id', UUID(as_uuid=True), ForeignKey('employee_labels.id'), primary_key=True)
)


class Routine(Base):
    """
    Routine task template for automated task generation.
    Defines recurring patterns (daily/weekly/monthly).
    """
    __tablename__ = "routines"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # Recurrence settings
    recurrence_type = Column(SQLEnum(RecurrenceType), nullable=False)
    recurrence_time = Column(Time, nullable=False)  # Time when task should be due
    recurrence_day = Column(Integer, nullable=True)  # For weekly: 1-7 (Mon-Sun), monthly: 1-31

    is_active = Column(Boolean, default=True, nullable=False)

    # Creation tracking
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    creator = relationship("User")
    labels = relationship(
        "EmployeeLabel",
        secondary=routine_labels,
        backref="routines"
    )

    def __repr__(self) -> str:
        return f"<Routine(title='{self.title}', type='{self.recurrence_type}', active={self.is_active})>"
