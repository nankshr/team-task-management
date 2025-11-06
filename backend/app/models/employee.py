"""
Employee model for shop workers who use the Telegram bot.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, BigInteger, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


# Association table for employee-label many-to-many relationship
employee_label_assignments = Table(
    'employee_label_assignments',
    Base.metadata,
    Column('employee_id', UUID(as_uuid=True), ForeignKey('employees.id'), primary_key=True),
    Column('label_id', UUID(as_uuid=True), ForeignKey('employee_labels.id'), primary_key=True)
)


class EmployeeLabel(Base):
    """
    Labels for categorizing employees (e.g., janitor, security, sales, cashier).
    """
    __tablename__ = "employee_labels"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(50), nullable=False, unique=True, index=True)
    color = Column(String(7), nullable=True)  # Hex color for UI (e.g., #FF5733)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    employees = relationship(
        "Employee",
        secondary=employee_label_assignments,
        back_populates="labels"
    )

    def __repr__(self) -> str:
        return f"<EmployeeLabel(name='{self.name}')>"


class Employee(Base):
    """
    Employee model for shop workers.
    Links to Telegram for bot communication.
    """
    __tablename__ = "employees"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)  # For future app login
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    telegram_user_id = Column(BigInteger, unique=True, nullable=True, index=True)
    telegram_username = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    labels = relationship(
        "EmployeeLabel",
        secondary=employee_label_assignments,
        back_populates="employees"
    )
    attendance_records = relationship("Attendance", back_populates="employee", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="assigned_employee", foreign_keys="Task.assigned_to")

    def __repr__(self) -> str:
        return f"<Employee(name='{self.name}', telegram_id={self.telegram_user_id})>"
