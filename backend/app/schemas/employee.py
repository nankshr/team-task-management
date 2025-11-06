"""
Pydantic schemas for Employee and EmployeeLabel models.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# EmployeeLabel Schemas
class EmployeeLabelBase(BaseModel):
    """Base employee label schema."""
    name: str = Field(..., min_length=1, max_length=50)
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")  # Hex color validation


class EmployeeLabelCreate(EmployeeLabelBase):
    """Schema for creating an employee label."""
    pass


class EmployeeLabelUpdate(BaseModel):
    """Schema for updating an employee label."""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")


class EmployeeLabelResponse(EmployeeLabelBase):
    """Schema for employee label response."""
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Employee Schemas
class EmployeeBase(BaseModel):
    """Base employee schema."""
    name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    is_active: bool = True


class EmployeeCreate(EmployeeBase):
    """Schema for creating an employee."""
    label_ids: Optional[List[UUID]] = []


class EmployeeUpdate(BaseModel):
    """Schema for updating an employee."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None
    label_ids: Optional[List[UUID]] = None


class EmployeeResponse(EmployeeBase):
    """Schema for employee response."""
    id: UUID
    telegram_user_id: Optional[int] = None
    telegram_username: Optional[str] = None
    labels: List[EmployeeLabelResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EmployeeTelegramRegister(BaseModel):
    """Schema for registering employee's Telegram ID."""
    employee_id: UUID
    telegram_user_id: int
    telegram_username: Optional[str] = None
