"""SQLModel database models for User and Task entities."""

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, String, Text, Boolean, DateTime, Index
from typing import Optional
from datetime import datetime
import uuid


class User(SQLModel, table=True):
    """User table managed by Better Auth."""

    __tablename__ = "users"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    password_hash: str = Field(max_length=255)
    name: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to tasks
    tasks: list["Task"] = Relationship(back_populates="user")


class Task(SQLModel, table=True):
    """Task entity representing a todo item owned by a user."""

    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=200, nullable=False)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    completed: bool = Field(default=False, sa_column=Column(Boolean, default=False))
    due_date: Optional[datetime] = Field(default=None, sa_column=Column(DateTime, nullable=True))
    priority: Optional[str] = Field(default="medium", max_length=20)  # high, medium, low
    category: Optional[str] = Field(default=None, max_length=50)  # personal, work, shopping, etc.
    completed_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime, nullable=True))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to user
    user: Optional["User"] = Relationship(back_populates="tasks")

    class Config:
        indexes = [
            Index("idx_tasks_user_id", "user_id"),
            Index("idx_tasks_completed", "completed"),
        ]
