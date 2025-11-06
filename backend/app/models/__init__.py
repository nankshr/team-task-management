"""
Database models package.
Exports all models for easy importing.
"""
from app.models.user import User, UserRole
from app.models.employee import Employee, EmployeeLabel, employee_label_assignments
from app.models.attendance import Attendance, AttendanceStatus
from app.models.task import Task, TaskComment, TaskType, TaskPriority, TaskStatus, CommentType, task_labels
from app.models.routine import Routine, RecurrenceType, routine_labels
from app.models.notification import Notification, NotificationType

__all__ = [
    # User
    "User",
    "UserRole",
    # Employee
    "Employee",
    "EmployeeLabel",
    "employee_label_assignments",
    # Attendance
    "Attendance",
    "AttendanceStatus",
    # Task
    "Task",
    "TaskComment",
    "TaskType",
    "TaskPriority",
    "TaskStatus",
    "CommentType",
    "task_labels",
    # Routine
    "Routine",
    "RecurrenceType",
    "routine_labels",
    # Notification
    "Notification",
    "NotificationType",
]
