"""Unit tests for ChatService.send_message() method.

This module tests the ChatService's core functionality including:
- Conversation creation
- Message persistence
- OpenRouter API integration
- MCP tool calling
- Error handling

Reference: T018 - Unit test for ChatService.send_message()
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.services.chat_service import ChatService
from app.models.conversation import Conversation
from app.models.message import Message, MessageRole


# ============================================================================
# ChatService.send_message() Tests
# ============================================================================

@pytest.mark.asyncio
async def test_send_message_creates_new_conversation(test_session, test_user_id):
    """Test that send_message creates a new conversation if none exists."""
    # Arrange
    chat_service = ChatService(session=test_session)
    user_message = "Add buy milk to my tasks"

    with patch('app.services.chat_service.OpenAI') as mock_openai:
        # Mock OpenRouter API response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Task created successfully"
        mock_response.choices[0].message.tool_calls = None
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai.return_value = mock_client

        # Act
        result = await chat_service.send_message(
            user_id=test_user_id,
            message=user_message,
            conversation_id=None
        )

        # Assert
        assert result is not None
        assert "conversation_id" in result
        assert result["conversation_id"] is not None

        # Verify conversation was created in database
        from sqlmodel import select
        statement = select(Conversation).where(Conversation.user_id == test_user_id)
        conversations = await test_session.exec(statement)
        conversation = conversations.first()
        assert conversation is not None
        assert str(conversation.id) == result["conversation_id"]


@pytest.mark.asyncio
async def test_send_message_persists_user_message(test_session, test_user_id, test_conversation):
    """Test that send_message persists the user's message to the database."""
    # Arrange
    chat_service = ChatService(session=test_session)
    user_message = "Show me my tasks"

    with patch('app.services.chat_service.OpenAI') as mock_openai:
        # Mock OpenRouter API response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Here are your tasks"
        mock_response.choices[0].message.tool_calls = None
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai.return_value = mock_client

        # Act
        result = await chat_service.send_message(
            user_id=test_user_id,
            message=user_message,
            conversation_id=str(test_conversation.id)
        )

        # Assert
        from sqlmodel import select
        statement = select(Message).where(
            Message.conversation_id == test_conversation.id,
            Message.role == MessageRole.USER
        )
        messages = await test_session.exec(statement)
        user_messages = messages.all()

        assert len(user_messages) >= 1
        assert any(msg.content == user_message for msg in user_messages)


@pytest.mark.asyncio
async def test_send_message_persists_assistant_response(test_session, test_user_id, test_conversation):
    """Test that send_message persists the assistant's response to the database."""
    # Arrange
    chat_service = ChatService(session=test_session)
    user_message = "Hello"
    assistant_response = "Hi! How can I help you with your tasks today?"

    with patch('app.services.chat_service.OpenAI') as mock_openai:
        # Mock OpenRouter API response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = assistant_response
        mock_response.choices[0].message.tool_calls = None
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai.return_value = mock_client

        # Act
        result = await chat_service.send_message(
            user_id=test_user_id,
            message=user_message,
            conversation_id=str(test_conversation.id)
        )

        # Assert
        from sqlmodel import select
        statement = select(Message).where(
            Message.conversation_id == test_conversation.id,
            Message.role == MessageRole.ASSISTANT
        )
        messages = await test_session.exec(statement)
        assistant_messages = messages.all()

        assert len(assistant_messages) >= 1
        assert any(msg.content == assistant_response for msg in assistant_messages)


@pytest.mark.asyncio
async def test_send_message_calls_openrouter_api(test_session, test_user_id, test_conversation):
    """Test that send_message calls the OpenRouter API with correct parameters."""
    # Arrange
    chat_service = ChatService(session=test_session)
    user_message = "Add task: buy groceries"

    with patch('app.services.chat_service.OpenAI') as mock_openai:
        # Mock OpenRouter API
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Task created"
        mock_response.choices[0].message.tool_calls = None
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai.return_value = mock_client

        # Act
        await chat_service.send_message(
            user_id=test_user_id,
            message=user_message,
            conversation_id=str(test_conversation.id)
        )

        # Assert
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args

        # Verify messages parameter includes user message
        assert "messages" in call_args.kwargs
        messages = call_args.kwargs["messages"]
        assert any(msg["role"] == "user" and msg["content"] == user_message for msg in messages)


@pytest.mark.asyncio
async def test_send_message_handles_mcp_tool_call(test_session, test_user_id, test_conversation):
    """Test that send_message correctly handles MCP tool calls from the AI."""
    # Arrange
    chat_service = ChatService(session=test_session)
    user_message = "Add buy milk to my tasks"

    with patch('app.services.chat_service.OpenAI') as mock_openai, \
         patch('app.services.chat_service.call_tool') as mock_call_tool:

        # Mock OpenRouter API response with tool call
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = None
        mock_response.choices[0].message.tool_calls = [
            MagicMock(
                id="call_123",
                type="function",
                function=MagicMock(
                    name="add_task",
                    arguments='{"user_id": "' + test_user_id + '", "title": "buy milk"}'
                )
            )
        ]
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai.return_value = mock_client

        # Mock MCP tool response
        mock_call_tool.return_value = {
            "success": True,
            "task": {"id": "1", "title": "buy milk"},
            "message": "Task created successfully"
        }

        # Act
        result = await chat_service.send_message(
            user_id=test_user_id,
            message=user_message,
            conversation_id=str(test_conversation.id)
        )

        # Assert
        mock_call_tool.assert_called_once()
        call_args = mock_call_tool.call_args
        assert call_args.args[0] == "add_task"  # Tool name
        assert "user_id" in call_args.args[1]  # Arguments
        assert call_args.args[1]["user_id"] == test_user_id


@pytest.mark.asyncio
async def test_send_message_handles_openrouter_api_error(test_session, test_user_id, test_conversation):
    """Test that send_message handles OpenRouter API errors gracefully."""
    # Arrange
    chat_service = ChatService(session=test_session)
    user_message = "Hello"

    with patch('app.services.chat_service.OpenAI') as mock_openai:
        # Mock OpenRouter API to raise an exception
        mock_client = MagicMock()
        mock_client.chat.completions.create = AsyncMock(
            side_effect=Exception("API connection failed")
        )
        mock_openai.return_value = mock_client

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await chat_service.send_message(
                user_id=test_user_id,
                message=user_message,
                conversation_id=str(test_conversation.id)
            )

        assert "API connection failed" in str(exc_info.value)


@pytest.mark.asyncio
async def test_send_message_validates_user_id(test_session):
    """Test that send_message validates user_id is provided."""
    # Arrange
    chat_service = ChatService(session=test_session)

    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        await chat_service.send_message(
            user_id="",
            message="Hello",
            conversation_id=None
        )

    assert "user_id" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_send_message_validates_message_not_empty(test_session, test_user_id):
    """Test that send_message validates message is not empty."""
    # Arrange
    chat_service = ChatService(session=test_session)

    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        await chat_service.send_message(
            user_id=test_user_id,
            message="",
            conversation_id=None
        )

    assert "message" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_send_message_returns_response_structure(test_session, test_user_id, test_conversation):
    """Test that send_message returns the expected response structure."""
    # Arrange
    chat_service = ChatService(session=test_session)
    user_message = "Hello"

    with patch('app.services.chat_service.OpenAI') as mock_openai:
        # Mock OpenRouter API response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Hi there!"
        mock_response.choices[0].message.tool_calls = None
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai.return_value = mock_client

        # Act
        result = await chat_service.send_message(
            user_id=test_user_id,
            message=user_message,
            conversation_id=str(test_conversation.id)
        )

        # Assert
        assert isinstance(result, dict)
        assert "conversation_id" in result
        assert "message" in result
        assert "role" in result
        assert result["role"] == "assistant"
        assert result["message"] == "Hi there!"
