"""Conversation model for storing chat sessions.

This module defines the Conversation SQLModel which groups related messages
into conversation sessions. Each user can have multiple conversations.
"""

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID, uuid4

from sqlalchemy import Index
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .message import Message


class Conversation(SQLModel, table=True):
    """Conversation entity representing a chat session owned by a user.

    Each conversation belongs to exactly one user and contains multiple messages.
    Conversations are automatically timestamped on creation and update.

    Attributes:
        id: Unique conversation identifier (UUID)
        user_id: Foreign key to users.id (Better Auth user ID)
        created_at: Timestamp when conversation was created
        updated_at: Timestamp when conversation was last updated
        messages: List of messages in this conversation
    """

    __tablename__ = "conversations"

    # Primary Key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        description="Unique conversation identifier"
    )

    # Foreign Keys
    user_id: str = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
        description="User who owns this conversation (Better Auth user ID)"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="When the conversation was created"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        description="When the conversation was last updated"
    )

    # Relationships
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    class Config:
        """SQLModel configuration for indexes."""
        indexes = [
            Index("idx_conversations_user_created", "user_id", "created_at")
        ]
