"""
Attendance model for tracking employee daily attendance.
"""
import uuid
from datetime import datetime, date
from sqlalchemy import Column, DateTime, Date, Boolean, ForeignKey, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class AttendanceStatus(str, enum.Enum):
    """Attendance status enumeration."""
    PRESENT = "present"
    ABSENT = "absent"
    HALF_DAY = "half_day"
    LEAVE = "leave"


class Attendance(Base):
    """
    Attendance records for employees.
    Tracks daily attendance with auto-marking capability.
    """
    __tablename__ = "attendance"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False, index=True)
    date = Column(Date, nullable=False, default=date.today, index=True)
    status = Column(SQLEnum(AttendanceStatus), nullable=False, default=AttendanceStatus.ABSENT)
    marked_at = Column(DateTime, nullable=True)
    auto_marked = Column(Boolean, default=False, nullable=False)

    # Relationships
    employee = relationship("Employee", back_populates="attendance_records")

    # Unique constraint: one attendance record per employee per day
    __table_args__ = (
        UniqueConstraint('employee_id', 'date', name='unique_employee_date'),
    )

    def __repr__(self) -> str:
        return f"<Attendance(employee_id={self.employee_id}, date={self.date}, status='{self.status}')>"
