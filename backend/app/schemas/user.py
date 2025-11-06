"""
Pydantic schemas for User model.
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID

from app.models.user import UserRole


class UserBase(BaseModel):
    """Base user schema with common fields."""
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    role: UserRole = UserRole.EMPLOYEE


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8, max_length=100)
    role: Optional[UserRole] = None


class UserResponse(UserBase):
    """Schema for user response."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    """Schema for user login."""
    username: str
    password: str


class Token(BaseModel):
    """Schema for authentication token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token payload data."""
    user_id: Optional[UUID] = None
    username: Optional[str] = None
    role: Optional[str] = None
