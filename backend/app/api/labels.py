"""
Employee label management API endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.employee import EmployeeLabel
from app.schemas.employee import (
    EmployeeLabelResponse,
    EmployeeLabelCreate,
    EmployeeLabelUpdate,
)

router = APIRouter()


@router.get("/", response_model=List[EmployeeLabelResponse])
async def get_labels(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all employee labels."""
    labels = db.query(EmployeeLabel).all()
    return labels


@router.get("/{label_id}", response_model=EmployeeLabelResponse)
async def get_label(
    label_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific label by ID."""
    label = db.query(EmployeeLabel).filter(EmployeeLabel.id == label_id).first()

    if not label:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Label not found"
        )

    return label


@router.post("/", response_model=EmployeeLabelResponse, status_code=status.HTTP_201_CREATED)
async def create_label(
    label_data: EmployeeLabelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new employee label."""
    # Check if label with this name already exists
    existing = db.query(EmployeeLabel).filter(
        EmployeeLabel.name == label_data.name
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Label with this name already exists"
        )

    label = EmployeeLabel(
        name=label_data.name,
        color=label_data.color,
    )

    db.add(label)
    db.commit()
    db.refresh(label)

    return label


@router.put("/{label_id}", response_model=EmployeeLabelResponse)
async def update_label(
    label_id: UUID,
    label_data: EmployeeLabelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an existing label."""
    label = db.query(EmployeeLabel).filter(EmployeeLabel.id == label_id).first()

    if not label:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Label not found"
        )

    # Check name uniqueness if being updated
    if label_data.name and label_data.name != label.name:
        existing = db.query(EmployeeLabel).filter(
            EmployeeLabel.name == label_data.name,
            EmployeeLabel.id != label_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Label with this name already exists"
            )

    # Update fields
    update_data = label_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(label, field, value)

    db.commit()
    db.refresh(label)

    return label


@router.delete("/{label_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_label(
    label_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a label."""
    label = db.query(EmployeeLabel).filter(EmployeeLabel.id == label_id).first()

    if not label:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Label not found"
        )

    db.delete(label)
    db.commit()

    return None
