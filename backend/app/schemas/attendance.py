"""
Pydantic schemas for Attendance model.
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime, date
from uuid import UUID

from app.models.attendance import AttendanceStatus


class AttendanceBase(BaseModel):
    """Base attendance schema."""
    employee_id: UUID
    date: date
    status: AttendanceStatus


class AttendanceCreate(AttendanceBase):
    """Schema for creating an attendance record."""
    auto_marked: bool = False


class AttendanceUpdate(BaseModel):
    """Schema for updating an attendance record."""
    status: AttendanceStatus


class AttendanceResponse(AttendanceBase):
    """Schema for attendance response."""
    id: UUID
    marked_at: Optional[datetime] = None
    auto_marked: bool

    model_config = ConfigDict(from_attributes=True)


class AttendanceMark(BaseModel):
    """Schema for marking attendance via Telegram."""
    employee_id: UUID
    status: AttendanceStatus


class AttendanceSummary(BaseModel):
    """Schema for daily attendance summary."""
    date: date
    total_employees: int
    present: int
    absent: int
    half_day: int
    leave: int
    present_employees: list[str] = []
    absent_employees: list[str] = []
