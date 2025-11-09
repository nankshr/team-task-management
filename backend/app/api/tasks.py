"""
Task management API endpoints.
"""
from typing import List
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.task import Task, TaskStatus, TaskComment, CommentType
from app.models.employee import Employee, EmployeeLabel
from app.schemas.task import (
    TaskResponse,
    TaskCreate,
    TaskUpdate,
    TaskCommentResponse,
    TaskCommentCreate,
)

router = APIRouter()


def generate_task_number(db: Session, parent_task: Task | None = None) -> str:
    """Generate a unique task number."""
    year = datetime.now().year

    if parent_task:
        # For subtasks: T2024-001-S1, T2024-001-S2, etc.
        subtask_count = db.query(Task).filter(
            Task.parent_task_id == parent_task.id
        ).count()
        return f"{parent_task.task_number}-S{subtask_count + 1}"
    else:
        # For main tasks: T2024-001, T2024-002, etc.
        task_count = db.query(Task).filter(
            Task.is_subtask == False,
            Task.task_number.like(f"T{year}-%")
        ).count()
        return f"T{year}-{task_count + 1:03d}"


@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    status: TaskStatus | None = None,
    employee_id: UUID | None = None,
    priority: str | None = None,
    date: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all tasks with optional filtering."""
    query = db.query(Task).filter(Task.is_subtask == False)

    if status:
        query = query.filter(Task.status == status)

    if employee_id:
        query = query.filter(Task.assigned_to == employee_id)

    if priority:
        query = query.filter(Task.priority == priority)

    if date:
        query = query.filter(Task.due_date == date)

    tasks = query.order_by(Task.created_at.desc()).all()
    return tasks


@router.get("/overdue", response_model=List[TaskResponse])
async def get_overdue_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all overdue tasks."""
    today = date.today()
    tasks = db.query(Task).filter(
        Task.due_date < today,
        Task.status.notin_([TaskStatus.COMPLETED])
    ).all()

    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific task by ID."""
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new task."""
    # Generate task number
    task_number = generate_task_number(db)

    # Create task
    task = Task(
        task_number=task_number,
        title=task_data.title,
        description=task_data.description,
        task_type=task_data.task_type,
        priority=task_data.priority,
        status=TaskStatus.PENDING if not task_data.assigned_to else TaskStatus.ASSIGNED,
        due_date=task_data.due_date,
        due_time=task_data.due_time,
        assigned_to=task_data.assigned_to,
        assigned_by=current_user.id if task_data.assigned_to else None,
        created_by=current_user.id,
        is_subtask=False,
    )

    # Add labels if provided
    if task_data.label_ids:
        labels = db.query(EmployeeLabel).filter(
            EmployeeLabel.id.in_(task_data.label_ids)
        ).all()
        task.labels = labels

    db.add(task)
    db.commit()
    db.refresh(task)

    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an existing task."""
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Update fields
    update_data = task_data.model_dump(exclude_unset=True, exclude={"label_ids"})
    for field, value in update_data.items():
        setattr(task, field, value)

    # Update labels if provided
    if task_data.label_ids is not None:
        labels = db.query(EmployeeLabel).filter(
            EmployeeLabel.id.in_(task_data.label_ids)
        ).all()
        task.labels = labels

    # Update status based on assignment
    if task_data.assigned_to and task.status == TaskStatus.PENDING:
        task.status = TaskStatus.ASSIGNED
        task.assigned_by = current_user.id

    db.commit()
    db.refresh(task)

    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a task."""
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    db.delete(task)
    db.commit()

    return None


@router.post("/{task_id}/assign", response_model=TaskResponse)
async def assign_task(
    task_id: UUID,
    employee_id: UUID = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Assign a task to an employee."""
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    employee = db.query(Employee).filter(Employee.id == employee_id).first()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    task.assigned_to = employee_id
    task.assigned_by = current_user.id
    task.status = TaskStatus.ASSIGNED

    db.commit()
    db.refresh(task)

    return task


@router.post("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a task as completed."""
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    task.status = TaskStatus.COMPLETED
    task.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(task)

    return task


@router.post("/{task_id}/subtask", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_subtask(
    task_id: UUID,
    subtask_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a subtask for a parent task."""
    parent_task = db.query(Task).filter(Task.id == task_id).first()

    if not parent_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent task not found"
        )

    # Generate subtask number
    task_number = generate_task_number(db, parent_task)

    # Create subtask
    subtask = Task(
        task_number=task_number,
        title=subtask_data.title,
        description=subtask_data.description,
        task_type=subtask_data.task_type,
        priority=subtask_data.priority,
        status=TaskStatus.PENDING,
        due_date=subtask_data.due_date,
        due_time=subtask_data.due_time,
        assigned_to=subtask_data.assigned_to or current_user.id,  # Assign to owner by default
        assigned_by=current_user.id,
        created_by=current_user.id,
        parent_task_id=parent_task.id,
        is_subtask=True,
    )

    # Mark parent task as blocked
    parent_task.status = TaskStatus.BLOCKED

    db.add(subtask)
    db.commit()
    db.refresh(subtask)

    return subtask


# Task Comments
@router.get("/{task_id}/comments", response_model=List[TaskCommentResponse])
async def get_task_comments(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all comments for a task."""
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    comments = db.query(TaskComment).filter(
        TaskComment.task_id == task_id
    ).order_by(TaskComment.created_at.desc()).all()

    return comments


@router.post("/{task_id}/comments", response_model=TaskCommentResponse, status_code=status.HTTP_201_CREATED)
async def add_task_comment(
    task_id: UUID,
    comment_data: TaskCommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a comment to a task."""
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    comment = TaskComment(
        task_id=task_id,
        comment_by_user_id=current_user.id,
        comment_text=comment_data.comment_text,
        comment_type=comment_data.comment_type,
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return comment
