"""
Attendance management API endpoints.
"""
from typing import List
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.attendance import Attendance, AttendanceStatus
from app.models.employee import Employee
from app.schemas.attendance import (
    AttendanceResponse,
    AttendanceCreate,
    AttendanceUpdate,
    AttendanceSummary,
)

router = APIRouter()


@router.get("/today", response_model=AttendanceSummary)
async def get_today_attendance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get today's attendance summary."""
    today = date.today()

    # Get total active employees
    total_employees = db.query(Employee).filter(Employee.is_active == True).count()

    # Get attendance records for today
    attendance_records = db.query(Attendance).filter(
        Attendance.date == today
    ).all()

    # Count by status
    present = sum(1 for a in attendance_records if a.status == AttendanceStatus.PRESENT)
    absent = sum(1 for a in attendance_records if a.status == AttendanceStatus.ABSENT)
    half_day = sum(1 for a in attendance_records if a.status == AttendanceStatus.HALF_DAY)
    on_leave = sum(1 for a in attendance_records if a.status == AttendanceStatus.ON_LEAVE)

    not_marked = total_employees - len(attendance_records)

    return AttendanceSummary(
        date=today,
        total_employees=total_employees,
        present=present,
        absent=absent,
        half_day=half_day,
        on_leave=on_leave,
        not_marked=not_marked,
    )


@router.get("/", response_model=List[AttendanceResponse])
async def get_attendance_history(
    start_date: date | None = None,
    end_date: date | None = None,
    employee_id: UUID | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get attendance history with optional filtering."""
    query = db.query(Attendance)

    if start_date:
        query = query.filter(Attendance.date >= start_date)

    if end_date:
        query = query.filter(Attendance.date <= end_date)

    if employee_id:
        query = query.filter(Attendance.employee_id == employee_id)

    attendance = query.order_by(Attendance.date.desc()).all()
    return attendance


@router.post("/mark", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED)
async def mark_attendance(
    attendance_data: AttendanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark attendance for an employee."""
    # Check if employee exists
    employee = db.query(Employee).filter(Employee.id == attendance_data.employee_id).first()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    # Use today if no date provided
    attendance_date = attendance_data.date if attendance_data.date else date.today()

    # Check if attendance already exists for this employee and date
    existing = db.query(Attendance).filter(
        Attendance.employee_id == attendance_data.employee_id,
        Attendance.date == attendance_date
    ).first()

    if existing:
        # Update existing attendance
        existing.status = attendance_data.status
        existing.marked_at = datetime.utcnow()
        existing.auto_marked = False
        db.commit()
        db.refresh(existing)
        return existing

    # Create new attendance record
    attendance = Attendance(
        employee_id=attendance_data.employee_id,
        date=attendance_date,
        status=attendance_data.status,
        marked_at=datetime.utcnow(),
        auto_marked=False,
    )

    db.add(attendance)
    db.commit()
    db.refresh(attendance)

    return attendance


@router.put("/{attendance_id}", response_model=AttendanceResponse)
async def update_attendance(
    attendance_id: UUID,
    attendance_data: AttendanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an attendance record."""
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()

    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance record not found"
        )

    # Update fields
    update_data = attendance_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(attendance, field, value)

    attendance.marked_at = datetime.utcnow()
    attendance.auto_marked = False

    db.commit()
    db.refresh(attendance)

    return attendance


@router.get("/report")
async def get_attendance_report(
    start_date: date = Query(...),
    end_date: date = Query(...),
    employee_id: UUID | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate attendance report for a date range."""
    query = db.query(Attendance).filter(
        Attendance.date >= start_date,
        Attendance.date <= end_date
    )

    if employee_id:
        query = query.filter(Attendance.employee_id == employee_id)

    attendance_records = query.all()

    # Calculate statistics
    total_days = (end_date - start_date).days + 1

    report = {
        "start_date": start_date,
        "end_date": end_date,
        "total_days": total_days,
        "total_records": len(attendance_records),
        "status_breakdown": {
            "present": sum(1 for a in attendance_records if a.status == AttendanceStatus.PRESENT),
            "absent": sum(1 for a in attendance_records if a.status == AttendanceStatus.ABSENT),
            "half_day": sum(1 for a in attendance_records if a.status == AttendanceStatus.HALF_DAY),
            "on_leave": sum(1 for a in attendance_records if a.status == AttendanceStatus.ON_LEAVE),
        },
        "auto_marked_count": sum(1 for a in attendance_records if a.auto_marked),
        "records": attendance_records,
    }

    return report
