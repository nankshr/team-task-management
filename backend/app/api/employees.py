"""
Employee management API endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.employee import Employee, EmployeeLabel
from app.schemas.employee import (
    EmployeeResponse,
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeLabelResponse,
    EmployeeLabelCreate,
    EmployeeLabelUpdate,
)

router = APIRouter()


# Employee endpoints
@router.get("/", response_model=List[EmployeeResponse])
async def get_employees(
    is_active: bool | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all employees with optional filtering."""
    query = db.query(Employee)

    if is_active is not None:
        query = query.filter(Employee.is_active == is_active)

    employees = query.all()
    return employees


@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific employee by ID."""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    return employee


@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    employee_data: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new employee."""
    # Check if telegram_user_id already exists
    if employee_data.telegram_user_id:
        existing = db.query(Employee).filter(
            Employee.telegram_user_id == employee_data.telegram_user_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee with this Telegram ID already exists"
            )

    # Create employee
    employee = Employee(
        name=employee_data.name,
        phone=employee_data.phone,
        telegram_user_id=employee_data.telegram_user_id,
        telegram_username=employee_data.telegram_username,
        is_active=employee_data.is_active if employee_data.is_active is not None else True,
    )

    # Add labels if provided
    if employee_data.label_ids:
        labels = db.query(EmployeeLabel).filter(
            EmployeeLabel.id.in_(employee_data.label_ids)
        ).all()
        employee.labels = labels

    db.add(employee)
    db.commit()
    db.refresh(employee)

    return employee


@router.put("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: UUID,
    employee_data: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an existing employee."""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    # Check telegram_user_id uniqueness if being updated
    if employee_data.telegram_user_id and employee_data.telegram_user_id != employee.telegram_user_id:
        existing = db.query(Employee).filter(
            Employee.telegram_user_id == employee_data.telegram_user_id,
            Employee.id != employee_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee with this Telegram ID already exists"
            )

    # Update fields
    update_data = employee_data.model_dump(exclude_unset=True, exclude={"label_ids"})
    for field, value in update_data.items():
        setattr(employee, field, value)

    # Update labels if provided
    if employee_data.label_ids is not None:
        labels = db.query(EmployeeLabel).filter(
            EmployeeLabel.id.in_(employee_data.label_ids)
        ).all()
        employee.labels = labels

    db.commit()
    db.refresh(employee)

    return employee


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(
    employee_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Deactivate an employee (soft delete)."""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    employee.is_active = False
    db.commit()

    return None


@router.get("/{employee_id}/tasks")
async def get_employee_tasks(
    employee_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all tasks assigned to a specific employee."""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    return employee.tasks
