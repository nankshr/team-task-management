"""
Seed data script for development and testing.
Creates sample employees, labels, tasks, and routines.
"""
import sys
from pathlib import Path
from datetime import date, time, datetime, timedelta

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.database import SessionLocal
from app.models import (
    EmployeeLabel, Employee, User, Task, Routine,
    TaskType, TaskPriority, TaskStatus, RecurrenceType,
    UserRole, Attendance, AttendanceStatus
)


def seed_labels(db):
    """Create employee labels."""
    print("Creating employee labels...")
    labels = [
        EmployeeLabel(name="Janitor", color="#FF5733"),
        EmployeeLabel(name="Security", color="#3498DB"),
        EmployeeLabel(name="Sales", color="#2ECC71"),
        EmployeeLabel(name="Cashier", color="#F39C12"),
        EmployeeLabel(name="Manager", color="#9B59B6"),
    ]

    for label in labels:
        existing = db.query(EmployeeLabel).filter(EmployeeLabel.name == label.name).first()
        if not existing:
            db.add(label)

    db.commit()
    print(f"✓ Created {len(labels)} labels")
    return {label.name: label for label in db.query(EmployeeLabel).all()}


def seed_employees(db, labels):
    """Create sample employees."""
    print("Creating employees...")

    employees_data = [
        {"name": "Raj Kumar", "phone": "+91-9876543210", "labels": ["Janitor"]},
        {"name": "Priya Sharma", "phone": "+91-9876543211", "labels": ["Sales"]},
        {"name": "Arun Singh", "phone": "+91-9876543212", "labels": ["Security"]},
        {"name": "Meena Patel", "phone": "+91-9876543213", "labels": ["Sales"]},
        {"name": "Kumar Reddy", "phone": "+91-9876543214", "labels": ["Cashier"]},
        {"name": "Lakshmi Iyer", "phone": "+91-9876543215", "labels": ["Sales"]},
        {"name": "Senthil Kumar", "phone": "+91-9876543216", "labels": ["Janitor"]},
        {"name": "Divya Menon", "phone": "+91-9876543217", "labels": ["Manager", "Sales"]},
    ]

    employees = []
    for emp_data in employees_data:
        existing = db.query(Employee).filter(Employee.name == emp_data["name"]).first()
        if not existing:
            employee = Employee(
                name=emp_data["name"],
                phone=emp_data["phone"],
                is_active=True
            )
            # Add labels
            for label_name in emp_data["labels"]:
                if label_name in labels:
                    employee.labels.append(labels[label_name])

            db.add(employee)
            employees.append(employee)

    db.commit()
    print(f"✓ Created {len(employees_data)} employees")
    return db.query(Employee).all()


def seed_routines(db, owner, labels):
    """Create sample routines."""
    print("Creating routines...")

    routines_data = [
        {
            "title": "Turn on lights and open shop",
            "description": "Open all shutters, turn on lights, and prepare shop for customers",
            "recurrence_type": RecurrenceType.DAILY,
            "recurrence_time": time(9, 0),
            "labels": ["Security", "Janitor"]
        },
        {
            "title": "Clean display shelves",
            "description": "Clean and polish all jewelry display cases",
            "recurrence_type": RecurrenceType.DAILY,
            "recurrence_time": time(18, 0),
            "labels": ["Janitor"]
        },
        {
            "title": "Update gold rate board",
            "description": "Update today's gold and silver rates on display board",
            "recurrence_type": RecurrenceType.DAILY,
            "recurrence_time": time(10, 0),
            "labels": ["Manager", "Sales"]
        },
        {
            "title": "Stock inventory count",
            "description": "Complete inventory count of all jewelry items",
            "recurrence_type": RecurrenceType.WEEKLY,
            "recurrence_time": time(17, 0),
            "recurrence_day": 6,  # Saturday
            "labels": ["Manager", "Cashier"]
        },
        {
            "title": "Deep cleaning",
            "description": "Complete deep cleaning of entire shop including storage areas",
            "recurrence_type": RecurrenceType.WEEKLY,
            "recurrence_time": time(19, 0),
            "recurrence_day": 7,  # Sunday
            "labels": ["Janitor"]
        },
        {
            "title": "GST documentation review",
            "description": "Review and organize GST documents for the month",
            "recurrence_type": RecurrenceType.MONTHLY,
            "recurrence_time": time(15, 0),
            "recurrence_day": 28,
            "labels": ["Manager", "Cashier"]
        },
    ]

    routines = []
    for routine_data in routines_data:
        existing = db.query(Routine).filter(Routine.title == routine_data["title"]).first()
        if not existing:
            label_names = routine_data.pop("labels", [])
            routine = Routine(
                **routine_data,
                created_by=owner.id,
                is_active=True
            )
            # Add labels
            for label_name in label_names:
                if label_name in labels:
                    routine.labels.append(labels[label_name])

            db.add(routine)
            routines.append(routine)

    db.commit()
    print(f"✓ Created {len(routines_data)} routines")


def seed_tasks(db, owner, employees):
    """Create sample tasks."""
    print("Creating sample tasks...")

    if not employees:
        print("  No employees found, skipping tasks")
        return

    today = date.today()

    tasks_data = [
        {
            "task_number": "T2024-001",
            "title": "Pick up jewelry from Vendor X",
            "description": "Collect the custom order from Vendor X by 3 PM",
            "task_type": TaskType.ONE_TIME,
            "priority": TaskPriority.HIGH,
            "status": TaskStatus.ASSIGNED,
            "due_date": today,
            "due_time": time(15, 0),
            "assigned_to": employees[0].id if len(employees) > 0 else None,
        },
        {
            "task_number": "T2024-002",
            "title": "Repair broken display lock",
            "description": "Fix the lock on display case #3",
            "task_type": TaskType.ONE_TIME,
            "priority": TaskPriority.URGENT,
            "status": TaskStatus.PENDING,
            "due_date": today,
            "due_time": time(12, 0),
        },
        {
            "task_number": "T2024-003",
            "title": "Call customer about order delivery",
            "description": "Contact Mrs. Sharma about her custom necklace delivery",
            "task_type": TaskType.ONE_TIME,
            "priority": TaskPriority.MEDIUM,
            "status": TaskStatus.ASSIGNED,
            "due_date": today,
            "due_time": time(11, 0),
            "assigned_to": employees[1].id if len(employees) > 1 else None,
        },
        {
            "task_number": "T2024-004",
            "title": "Organize storage room",
            "description": "Sort and organize jewelry boxes in storage",
            "task_type": TaskType.ONE_TIME,
            "priority": TaskPriority.LOW,
            "status": TaskStatus.COMPLETED,
            "due_date": today - timedelta(days=1),
            "due_time": time(16, 0),
            "assigned_to": employees[0].id if len(employees) > 0 else None,
            "completed_at": datetime.utcnow() - timedelta(days=1),
        },
    ]

    for task_data in tasks_data:
        existing = db.query(Task).filter(Task.task_number == task_data["task_number"]).first()
        if not existing:
            task = Task(
                **task_data,
                created_by=owner.id,
                assigned_by=owner.id if task_data.get("assigned_to") else None,
            )
            db.add(task)

    db.commit()
    print(f"✓ Created {len(tasks_data)} sample tasks")


def main():
    """Main seed function."""
    print("=" * 60)
    print("Seed Data Script")
    print("=" * 60)
    print()

    db = SessionLocal()
    try:
        # Get owner user
        owner = db.query(User).filter(User.role == UserRole.OWNER).first()
        if not owner:
            print("✗ No owner user found. Run init_db.py first!")
            return

        print(f"Using owner: {owner.username}")
        print()

        # Seed data
        labels = seed_labels(db)
        employees = seed_employees(db, labels)
        seed_routines(db, owner, labels)
        seed_tasks(db, owner, employees)

        print()
        print("=" * 60)
        print("Seed data created successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"✗ Error: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
