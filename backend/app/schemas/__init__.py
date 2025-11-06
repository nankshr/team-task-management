"""
Pydantic schemas package.
Exports all schemas for easy importing.
"""
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserLogin,
    Token,
    TokenData,
)
from app.schemas.employee import (
    EmployeeLabelBase,
    EmployeeLabelCreate,
    EmployeeLabelUpdate,
    EmployeeLabelResponse,
    EmployeeBase,
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
    EmployeeTelegramRegister,
)
from app.schemas.task import (
    TaskCommentBase,
    TaskCommentCreate,
    TaskCommentResponse,
    TaskBase,
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskDetailResponse,
    TaskComplete,
    TaskAssign,
    TaskCreateSubtask,
)
from app.schemas.attendance import (
    AttendanceBase,
    AttendanceCreate,
    AttendanceUpdate,
    AttendanceResponse,
    AttendanceMark,
    AttendanceSummary,
)
from app.schemas.routine import (
    RoutineBase,
    RoutineCreate,
    RoutineUpdate,
    RoutineResponse,
)

__all__ = [
    # User
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserLogin",
    "Token",
    "TokenData",
    # Employee
    "EmployeeLabelBase",
    "EmployeeLabelCreate",
    "EmployeeLabelUpdate",
    "EmployeeLabelResponse",
    "EmployeeBase",
    "EmployeeCreate",
    "EmployeeUpdate",
    "EmployeeResponse",
    "EmployeeTelegramRegister",
    # Task
    "TaskCommentBase",
    "TaskCommentCreate",
    "TaskCommentResponse",
    "TaskBase",
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "TaskDetailResponse",
    "TaskComplete",
    "TaskAssign",
    "TaskCreateSubtask",
    # Attendance
    "AttendanceBase",
    "AttendanceCreate",
    "AttendanceUpdate",
    "AttendanceResponse",
    "AttendanceMark",
    "AttendanceSummary",
    # Routine
    "RoutineBase",
    "RoutineCreate",
    "RoutineUpdate",
    "RoutineResponse",
]
