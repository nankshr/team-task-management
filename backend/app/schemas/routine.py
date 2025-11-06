"""
Pydantic schemas for Routine model.
"""
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime, time
from uuid import UUID

from app.models.routine import RecurrenceType


class RoutineBase(BaseModel):
    """Base routine schema."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    recurrence_type: RecurrenceType
    recurrence_time: time
    recurrence_day: Optional[int] = None

    @field_validator('recurrence_day')
    @classmethod
    def validate_recurrence_day(cls, v, info):
        """Validate recurrence_day based on recurrence_type."""
        if v is not None:
            recurrence_type = info.data.get('recurrence_type')
            if recurrence_type == RecurrenceType.WEEKLY:
                if not 1 <= v <= 7:
                    raise ValueError('For weekly routines, recurrence_day must be 1-7 (Monday-Sunday)')
            elif recurrence_type == RecurrenceType.MONTHLY:
                if not 1 <= v <= 31:
                    raise ValueError('For monthly routines, recurrence_day must be 1-31')
        return v


class RoutineCreate(RoutineBase):
    """Schema for creating a routine."""
    label_ids: Optional[List[UUID]] = []


class RoutineUpdate(BaseModel):
    """Schema for updating a routine."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    recurrence_type: Optional[RecurrenceType] = None
    recurrence_time: Optional[time] = None
    recurrence_day: Optional[int] = None
    is_active: Optional[bool] = None
    label_ids: Optional[List[UUID]] = None


class RoutineResponse(RoutineBase):
    """Schema for routine response."""
    id: UUID
    is_active: bool
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
