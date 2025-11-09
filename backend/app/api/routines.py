"""
Routine management API endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.routine import Routine
from app.models.employee import EmployeeLabel
from app.schemas.routine import (
    RoutineResponse,
    RoutineCreate,
    RoutineUpdate,
)

router = APIRouter()


@router.get("/", response_model=List[RoutineResponse])
async def get_routines(
    is_active: bool | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all routines with optional filtering."""
    query = db.query(Routine)

    if is_active is not None:
        query = query.filter(Routine.is_active == is_active)

    routines = query.order_by(Routine.created_at.desc()).all()
    return routines


@router.get("/{routine_id}", response_model=RoutineResponse)
async def get_routine(
    routine_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific routine by ID."""
    routine = db.query(Routine).filter(Routine.id == routine_id).first()

    if not routine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Routine not found"
        )

    return routine


@router.post("/", response_model=RoutineResponse, status_code=status.HTTP_201_CREATED)
async def create_routine(
    routine_data: RoutineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new routine."""
    routine = Routine(
        title=routine_data.title,
        description=routine_data.description,
        recurrence_type=routine_data.recurrence_type,
        recurrence_time=routine_data.recurrence_time,
        recurrence_day=routine_data.recurrence_day,
        is_active=routine_data.is_active if routine_data.is_active is not None else True,
        created_by=current_user.id,
    )

    # Add labels if provided
    if routine_data.label_ids:
        labels = db.query(EmployeeLabel).filter(
            EmployeeLabel.id.in_(routine_data.label_ids)
        ).all()
        routine.labels = labels

    db.add(routine)
    db.commit()
    db.refresh(routine)

    return routine


@router.put("/{routine_id}", response_model=RoutineResponse)
async def update_routine(
    routine_id: UUID,
    routine_data: RoutineUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an existing routine."""
    routine = db.query(Routine).filter(Routine.id == routine_id).first()

    if not routine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Routine not found"
        )

    # Update fields
    update_data = routine_data.model_dump(exclude_unset=True, exclude={"label_ids"})
    for field, value in update_data.items():
        setattr(routine, field, value)

    # Update labels if provided
    if routine_data.label_ids is not None:
        labels = db.query(EmployeeLabel).filter(
            EmployeeLabel.id.in_(routine_data.label_ids)
        ).all()
        routine.labels = labels

    db.commit()
    db.refresh(routine)

    return routine


@router.delete("/{routine_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_routine(
    routine_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Deactivate a routine (soft delete)."""
    routine = db.query(Routine).filter(Routine.id == routine_id).first()

    if not routine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Routine not found"
        )

    routine.is_active = False
    db.commit()

    return None


@router.post("/{routine_id}/generate", status_code=status.HTTP_200_OK)
async def generate_routine_tasks(
    routine_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Manually trigger task generation for a routine."""
    routine = db.query(Routine).filter(Routine.id == routine_id).first()

    if not routine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Routine not found"
        )

    if not routine.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot generate tasks from inactive routine"
        )

    # TODO: Implement actual task generation logic
    # This will be handled by the scheduler service in the future
    # For now, just return a success message

    return {
        "message": "Task generation triggered successfully",
        "routine_id": str(routine_id),
        "routine_title": routine.title
    }
