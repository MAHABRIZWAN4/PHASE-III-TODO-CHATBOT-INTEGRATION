"""Response models for API endpoints.

This module defines Pydantic models for API responses, ensuring consistent
response structure across all endpoints.
"""

from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ChatResponse(BaseModel):
    """Response model for chat message endpoint.

    This model defines the structure of responses returned by the chat API.
    It includes the conversation context, message identifiers, and optional
    metadata about tool calls and language detection.

    Attributes:
        conversation_id: UUID of the conversation (new or existing)
        message_id: UUID of the assistant's response message
        response: Assistant's response text in the same language as input
        metadata: Optional metadata including tool calls, language, model info

    Examples:
        >>> # Simple task creation response
        >>> ChatResponse(
        ...     conversation_id=UUID("550e8400-e29b-41d4-a716-446655440000"),
        ...     message_id=UUID("660e8400-e29b-41d4-a716-446655440001"),
        ...     response="Task created: buy milk",
        ...     metadata={
        ...         "tool_calls": [{"tool": "add_task", "success": True}],
        ...         "language": "english"
        ...     }
        ... )

        >>> # Task list response
        >>> ChatResponse(
        ...     conversation_id=UUID("550e8400-e29b-41d4-a716-446655440000"),
        ...     message_id=UUID("660e8400-e29b-41d4-a716-446655440002"),
        ...     response="You have 3 active tasks:\\n1. Buy milk\\n2. Finish report\\n3. Call dentist",
        ...     metadata={
        ...         "tool_calls": [{"tool": "list_tasks", "success": True}],
        ...         "language": "english"
        ...     }
        ... )
    """

    conversation_id: UUID = Field(
        ...,
        description="ID of the conversation (new or existing)",
        example="550e8400-e29b-41d4-a716-446655440000"
    )

    message_id: UUID = Field(
        ...,
        description="ID of the assistant's response message",
        example="660e8400-e29b-41d4-a716-446655440001"
    )

    response: str = Field(
        ...,
        description="Assistant's response in the same language as input",
        example="Task created: buy milk"
    )

    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional metadata about the response (tool calls, language, model)",
        example={
            "tool_calls": [
                {
                    "tool": "add_task",
                    "success": True,
                    "result": {"id": 1, "title": "buy milk"}
                }
            ],
            "language": "english",
            "model": "xiaomi/mimo-v2-flash:free"
        }
    )

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "examples": [
                {
                    "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                    "message_id": "660e8400-e29b-41d4-a716-446655440001",
                    "response": "Task created: buy milk",
                    "metadata": {
                        "tool_calls": [
                            {
                                "tool": "add_task",
                                "success": True
                            }
                        ],
                        "language": "english"
                    }
                },
                {
                    "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                    "message_id": "660e8400-e29b-41d4-a716-446655440002",
                    "response": "You have 3 active tasks:\n1. Buy groceries\n2. Finish report\n3. Call dentist",
                    "metadata": {
                        "tool_calls": [
                            {
                                "tool": "list_tasks",
                                "success": True
                            }
                        ],
                        "language": "english"
                    }
                }
            ]
        }
