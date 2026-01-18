"""Chat API routes for AI-powered conversational task management.

This module implements the chat endpoint that allows users to interact with
their tasks through natural language conversations in English and Urdu.

Reference: T028-T030 from specs/003-ai-todo-chatbot/tasks.md
"""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from db import get_session
from middleware.jwt_auth import get_current_user_id
from app.models.requests import ChatRequest
from app.models.responses import ChatResponse
from app.services.chat_service import chat_service

router = APIRouter(prefix="/api", tags=["Chat"])


@router.post("/{user_id}/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def send_chat_message(
    user_id: str,
    request: ChatRequest,
    session: AsyncSession = Depends(get_session),
    authenticated_user_id: str = Depends(get_current_user_id)
):
    """Send a chat message to the AI assistant.

    This endpoint processes natural language messages and performs task operations
    through conversational AI. It supports both English and Urdu languages with
    automatic language detection.

    The endpoint:
    1. Verifies JWT token authentication
    2. Validates user ID matches authenticated user
    3. Creates or retrieves conversation
    4. Processes message through OpenRouter API
    5. Executes MCP tool calls if needed
    6. Returns AI response with metadata

    Args:
        user_id: User ID from URL path (must match JWT token)
        request: ChatRequest with message and optional conversation_id
        session: Database session (injected)
        authenticated_user_id: User ID from JWT token (injected)

    Returns:
        ChatResponse with conversation_id, message_id, response, and metadata

    Raises:
        HTTPException 400: Invalid request (empty message, message too long)
        HTTPException 401: Missing or invalid JWT token
        HTTPException 403: User ID mismatch (URL user_id != JWT user_id)
        HTTPException 404: Conversation not found
        HTTPException 500: OpenRouter API failure or internal error

    Examples:
        >>> # New conversation
        >>> POST /api/user123/chat
        >>> {
        ...     "message": "Add buy milk to my tasks"
        ... }
        >>> Response: {
        ...     "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
        ...     "message_id": "660e8400-e29b-41d4-a716-446655440001",
        ...     "response": "Task created: buy milk",
        ...     "metadata": {
        ...         "tool_calls": [{"tool": "add_task", "success": true}],
        ...         "language": "english"
        ...     }
        ... }

        >>> # Continue conversation
        >>> POST /api/user123/chat
        >>> {
        ...     "message": "Show me my tasks",
        ...     "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
        ... }

    Reference:
        - T028: POST /api/{user_id}/chat endpoint with JWT verification
        - T029: User ID validation (JWT user_id must match URL user_id)
        - T030: Error handling for OpenRouter API failures
        - API Spec: /specs/003-ai-todo-chatbot/contracts/chat-api.yaml
    """
    # T029: Validate user ID matches authenticated user
    if user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized: User ID mismatch"
        )

    # T030: Error handling for OpenRouter API failures
    # The ChatService already handles OpenRouter errors and raises HTTPException
    # Additional validation for request
    try:
        # Validate message is not empty (Pydantic already validates length)
        if not request.message or not request.message.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message cannot be empty"
            )

        # Call chat service to process message
        response = await chat_service.send_message(
            user_id=authenticated_user_id,
            request=request,
            session=session
        )

        return response

    except HTTPException:
        # Re-raise HTTP exceptions from service layer
        raise

    except ValueError as e:
        # Handle validation errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        # T030: Catch any unexpected errors and return 500
        # Log error (in production, use proper logging)
        print(f"Unexpected error in chat endpoint: {str(e)}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error. Please try again later."
        )
