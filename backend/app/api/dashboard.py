"""
Dashboard statistics API endpoints.
"""
from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.employee import Employee
from app.models.attendance import Attendance, AttendanceStatus
from app.models.task import Task, TaskStatus

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get dashboard overview statistics."""
    today = date.today()

    # Attendance statistics
    total_employees = db.query(Employee).filter(Employee.is_active == True).count()

    attendance_today = db.query(Attendance).filter(Attendance.date == today).all()

    today_present = sum(1 for a in attendance_today if a.status == AttendanceStatus.PRESENT)
    today_absent = sum(1 for a in attendance_today if a.status == AttendanceStatus.ABSENT)
    not_marked = total_employees - len(attendance_today)

    # Task statistics
    all_tasks = db.query(Task).filter(Task.is_subtask == False).all()

    pending = sum(1 for t in all_tasks if t.status == TaskStatus.PENDING)
    in_progress = sum(1 for t in all_tasks if t.status == TaskStatus.IN_PROGRESS)
    completed = sum(1 for t in all_tasks if t.status == TaskStatus.COMPLETED)

    overdue = sum(
        1 for t in all_tasks
        if t.due_date < today and t.status not in [TaskStatus.COMPLETED]
    )

    # Recent tasks (last 10)
    recent_tasks = (
        db.query(Task)
        .filter(Task.is_subtask == False)
        .order_by(Task.created_at.desc())
        .limit(10)
        .all()
    )

    return {
        "attendance": {
            "today_present": today_present,
            "today_absent": today_absent,
            "total_employees": total_employees,
            "not_marked": not_marked,
        },
        "tasks": {
            "pending": pending,
            "in_progress": in_progress,
            "completed": completed,
            "overdue": overdue,
        },
        "recent_tasks": recent_tasks,
    }
