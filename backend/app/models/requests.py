"""Request models for API endpoints.

This module defines Pydantic models for validating incoming API requests.
All request models include field validation to ensure data integrity.
"""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, constr


class ChatRequest(BaseModel):
    """Request model for sending a chat message.

    This model validates incoming chat requests, ensuring the message
    is within acceptable length limits and the conversation_id (if provided)
    is a valid UUID.

    Attributes:
        message: User's message text (1-2000 characters)
        conversation_id: Optional UUID to continue an existing conversation.
                        If omitted, a new conversation will be created.

    Examples:
        >>> # New conversation
        >>> ChatRequest(message="Add buy milk to my tasks")
        ChatRequest(message='Add buy milk to my tasks', conversation_id=None)

        >>> # Continue existing conversation
        >>> ChatRequest(
        ...     message="Show me my tasks",
        ...     conversation_id="550e8400-e29b-41d4-a716-446655440000"
        ... )
        ChatRequest(message='Show me my tasks', conversation_id=UUID('550e8400-e29b-41d4-a716-446655440000'))

    Validation:
        - message: Must be 1-2000 characters (enforced by constr)
        - conversation_id: Must be valid UUID format if provided
    """

    message: constr(min_length=1, max_length=2000) = Field(
        ...,
        description="User's message in English or Urdu",
        example="Add buy milk to my tasks"
    )

    conversation_id: Optional[UUID] = Field(
        default=None,
        description="Optional conversation ID to continue existing conversation. "
                   "If omitted, a new conversation is created.",
        example="550e8400-e29b-41d4-a716-446655440000"
    )

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "examples": [
                {
                    "message": "Add buy milk to my tasks"
                },
                {
                    "message": "Show me my tasks",
                    "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
                },
                {
                    "message": "میرے کام دکھاؤ"
                }
            ]
        }
