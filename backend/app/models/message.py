"""Message model for storing individual chat messages.

This module defines the Message SQLModel and MessageRole enum for storing
messages within conversations. Messages can be from users, assistants, or system.
"""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, Index, JSON
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .conversation import Conversation


class MessageRole(str, Enum):
    """Enum for message sender roles.

    Attributes:
        USER: Message sent by the user
        ASSISTANT: Message sent by the AI assistant
        SYSTEM: Internal system message (e.g., errors, notifications)
    """
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(SQLModel, table=True):
    """Message entity representing a single message in a conversation.

    Messages are immutable once created and belong to exactly one conversation.
    They can be from users, AI assistants, or system-generated.

    Attributes:
        id: Unique message identifier (UUID)
        conversation_id: Foreign key to conversations.id
        role: Who sent the message (user, assistant, or system)
        content: Message text content (max 10,000 characters)
        metadata: Optional JSON metadata (tool calls, language, errors, etc.)
        timestamp: When the message was sent
        conversation: Relationship to parent conversation
    """

    __tablename__ = "messages"

    # Primary Key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        description="Unique message identifier"
    )

    # Foreign Keys
    conversation_id: UUID = Field(
        foreign_key="conversations.id",
        nullable=False,
        index=True,
        description="Conversation this message belongs to"
    )

    # Message Content
    role: MessageRole = Field(
        nullable=False,
        description="Who sent the message: user, assistant, or system"
    )

    content: str = Field(
        nullable=False,
        max_length=10000,
        description="Message text content"
    )

    # Metadata (JSON field for extensible data)
    # Note: Field name is 'meta_data' to avoid conflict with SQLAlchemy's reserved 'metadata' attribute
    meta_data: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON),
        description="Optional metadata (tool calls, errors, language, etc.)"
    )

    # Timestamps
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="When the message was sent"
    )

    # Relationships
    conversation: "Conversation" = Relationship(back_populates="messages")

    class Config:
        """SQLModel configuration for indexes."""
        indexes = [
            Index("idx_messages_conversation_time", "conversation_id", "timestamp")
        ]
