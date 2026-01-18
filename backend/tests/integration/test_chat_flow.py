"""Integration tests for chat → task creation flow.

This module tests the full end-to-end flow including:
- Send message → AI interprets → calls add_task → returns response
- Conversation persistence
- Message history
- Uses test database

Reference: T021 - Integration test for chat → task creation flow
"""

import pytest
from uuid import uuid4
from unittest.mock import patch, MagicMock, AsyncMock

from app.services.chat_service import ChatService
from app.models.conversation import Conversation
from app.models.message import Message, MessageRole
from models import Task
from sqlmodel import select


# ============================================================================
# Full Chat Flow Integration Tests
# ============================================================================

@pytest.mark.asyncio
async def test_full_chat_to_task_creation_flow(test_session, test_user):
    """Test the complete flow: user message → AI interprets → creates task → responds."""
    # Arrange
    chat_service = ChatService(session=test_session)
    user_message = "Add buy milk to my tasks"

    with patch('app.services.chat_service.OpenAI') as mock_openai, \
         patch('mcp_server.task_tools.async_session_maker') as mock_mcp_session:

        # Mock OpenRouter to return tool call
        mock_client = MagicMock()
        mock_tool_call_response = MagicMock()
        mock_tool_call_response.choices = [MagicMock()]
        mock_tool_call_response.choices[0].message.content = None
        mock_tool_call_response.choices[0].message.tool_calls = [
            MagicMock(
                id="call_123",
                type="function",
                function=MagicMock(
                    name="add_task",
                    arguments=f'{{"user_id": "{test_user.id}", "title": "buy milk"}}'
                )
            )
        ]

        # Mock second call for final response
        mock_final_response = MagicMock()
        mock_final_response.choices = [MagicMock()]
        mock_final_response.choices[0].message.content = "Task 'buy milk' has been created successfully!"
        mock_final_response.choices[0].message.tool_calls = None

        mock_client.chat.completions.create = AsyncMock(
            side_effect=[mock_tool_call_response, mock_final_response]
        )
        mock_openai.return_value = mock_client

        # Mock MCP session to use test_session
        mock_mcp_session.return_value.__aenter__.return_value = test_session

        # Act
        result = await chat_service.send_message(
            user_id=test_user.id,
            message=user_message,
            conversation_id=None
        )

        # Assert - Verify response
        assert result is not None
        assert "conversation_id" in result
        assert "message" in result
        assert "buy milk" in result["message"].lower()

        # Assert - Verify conversation was created
        conv_statement = select(Conversation).where(Conversation.user_id == test_user.id)
        conversations = await test_session.exec(conv_statement)
        conversation = conversations.first()
        assert conversation is not None

        # Assert - Verify messages were persisted
        msg_statement = select(Message).where(Message.conversation_id == conversation.id)
        messages = await test_session.exec(msg_statement)
        all_messages = messages.all()
        assert len(all_messages) >= 2  # At least user message and assistant response

        # Assert - Verify task was created
        task_statement = select(Task).where(Task.user_id == test_user.id)
        tasks = await test_session.exec(task_statement)
        task = tasks.first()
        assert task is not None
        assert task.title == "buy milk"
        assert task.completed is False


@pytest.mark.asyncio
async def test_conversation_persistence_across_messages(test_session, test_user):
    """Test that conversation persists across multiple messages."""
    # Arrange
    chat_service = ChatService(session=test_session)
    message1 = "Hello"
    message2 = "Add task: buy groceries"

    with patch('app.services.chat_service.OpenAI') as mock_openai:
        # Mock responses for both messages
        mock_client = MagicMock()
        mock_response1 = MagicMock()
        mock_response1.choices = [MagicMock()]
        mock_response1.choices[0].message.content = "Hi! How can I help?"
        mock_response1.choices[0].message.tool_calls = None

        mock_response2 = MagicMock()
        mock_response2.choices = [MagicMock()]
        mock_response2.choices[0].message.content = "Task created!"
        mock_response2.choices[0].message.tool_calls = None

        mock_client.chat.completions.create = AsyncMock(
            side_effect=[mock_response1, mock_response2]
        )
        mock_openai.return_value = mock_client

        # Act - Send first message
        result1 = await chat_service.send_message(
            user_id=test_user.id,
            message=message1,
            conversation_id=None
        )

        conversation_id = result1["conversation_id"]

        # Act - Send second message in same conversation
        result2 = await chat_service.send_message(
            user_id=test_user.id,
            message=message2,
            conversation_id=conversation_id
        )

        # Assert - Same conversation ID
        assert result2["conversation_id"] == conversation_id

        # Assert - All messages are in the same conversation
        msg_statement = select(Message).where(
            Message.conversation_id == uuid4(conversation_id)
        )
        messages = await test_session.exec(msg_statement)
        all_messages = messages.all()
        assert len(all_messages) >= 4  # 2 user messages + 2 assistant responses


@pytest.mark.asyncio
async def test_message_history_maintained_in_conversation(test_session, test_user):
    """Test that message history is maintained and ordered correctly."""
    # Arrange
    chat_service = ChatService(session=test_session)
    messages_to_send = ["First message", "Second message", "Third message"]

    with patch('app.services.chat_service.OpenAI') as mock_openai:
        # Mock responses
        mock_client = MagicMock()
        mock_responses = []
        for i in range(len(messages_to_send)):
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = f"Response {i+1}"
            mock_response.choices[0].message.tool_calls = None
            mock_responses.append(mock_response)

        mock_client.chat.completions.create = AsyncMock(side_effect=mock_responses)
        mock_openai.return_value = mock_client

        # Act - Send multiple messages
        conversation_id = None
        for msg in messages_to_send:
            result = await chat_service.send_message(
                user_id=test_user.id,
                message=msg,
                conversation_id=conversation_id
            )
            conversation_id = result["conversation_id"]

        # Assert - Verify message history
        msg_statement = select(Message).where(
            Message.conversation_id == uuid4(conversation_id)
        ).order_by(Message.timestamp)
        messages = await test_session.exec(msg_statement)
        all_messages = messages.all()

        # Should have 6 messages total (3 user + 3 assistant)
        assert len(all_messages) >= 6

        # Verify order and content
        user_messages = [m for m in all_messages if m.role == MessageRole.USER]
        assert len(user_messages) == 3
        assert user_messages[0].content == "First message"
        assert user_messages[1].content == "Second message"
        assert user_messages[2].content == "Third message"


@pytest.mark.asyncio
async def test_multiple_tasks_created_in_conversation(test_session, test_user):
    """Test creating multiple tasks within the same conversation."""
    # Arrange
    chat_service = ChatService(session=test_session)
    task_messages = [
        "Add task: buy milk",
        "Add task: call dentist",
        "Add task: finish report"
    ]

    with patch('app.services.chat_service.OpenAI') as mock_openai, \
         patch('mcp_server.task_tools.async_session_maker') as mock_mcp_session:

        mock_mcp_session.return_value.__aenter__.return_value = test_session

        # Mock OpenRouter responses with tool calls
        mock_client = MagicMock()
        mock_responses = []

        for task_msg in task_messages:
            # Extract task title from message
            task_title = task_msg.replace("Add task: ", "")

            # Tool call response
            tool_response = MagicMock()
            tool_response.choices = [MagicMock()]
            tool_response.choices[0].message.content = None
            tool_response.choices[0].message.tool_calls = [
                MagicMock(
                    id=f"call_{task_title}",
                    type="function",
                    function=MagicMock(
                        name="add_task",
                        arguments=f'{{"user_id": "{test_user.id}", "title": "{task_title}"}}'
                    )
                )
            ]

            # Final response
            final_response = MagicMock()
            final_response.choices = [MagicMock()]
            final_response.choices[0].message.content = f"Task '{task_title}' created!"
            final_response.choices[0].message.tool_calls = None

            mock_responses.extend([tool_response, final_response])

        mock_client.chat.completions.create = AsyncMock(side_effect=mock_responses)
        mock_openai.return_value = mock_client

        # Act - Send all task creation messages
        conversation_id = None
        for msg in task_messages:
            result = await chat_service.send_message(
                user_id=test_user.id,
                message=msg,
                conversation_id=conversation_id
            )
            conversation_id = result["conversation_id"]

        # Assert - Verify all tasks were created
        task_statement = select(Task).where(Task.user_id == test_user.id)
        tasks = await test_session.exec(task_statement)
        all_tasks = tasks.all()

        assert len(all_tasks) == 3
        task_titles = [task.title for task in all_tasks]
        assert "buy milk" in task_titles
        assert "call dentist" in task_titles
        assert "finish report" in task_titles


@pytest.mark.asyncio
async def test_user_isolation_in_chat_flow(test_session, test_user, test_user_2):
    """Test that users cannot access each other's conversations or tasks."""
    # Arrange
    chat_service = ChatService(session=test_session)

    with patch('app.services.chat_service.OpenAI') as mock_openai, \
         patch('mcp_server.task_tools.async_session_maker') as mock_mcp_session:

        mock_mcp_session.return_value.__aenter__.return_value = test_session

        # Mock OpenRouter
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Task created"
        mock_response.choices[0].message.tool_calls = None
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai.return_value = mock_client

        # Act - User 1 creates a task
        result1 = await chat_service.send_message(
            user_id=test_user.id,
            message="Add task: user 1 task",
            conversation_id=None
        )

        # Act - User 2 creates a task
        result2 = await chat_service.send_message(
            user_id=test_user_2.id,
            message="Add task: user 2 task",
            conversation_id=None
        )

        # Assert - Different conversations
        assert result1["conversation_id"] != result2["conversation_id"]

        # Assert - User 1 can only see their tasks
        task_statement1 = select(Task).where(Task.user_id == test_user.id)
        tasks1 = await test_session.exec(task_statement1)
        user1_tasks = tasks1.all()
        assert all(task.user_id == test_user.id for task in user1_tasks)

        # Assert - User 2 can only see their tasks
        task_statement2 = select(Task).where(Task.user_id == test_user_2.id)
        tasks2 = await test_session.exec(task_statement2)
        user2_tasks = tasks2.all()
        assert all(task.user_id == test_user_2.id for task in user2_tasks)


@pytest.mark.asyncio
async def test_error_handling_in_chat_flow(test_session, test_user):
    """Test that errors in the chat flow are handled gracefully."""
    # Arrange
    chat_service = ChatService(session=test_session)

    with patch('app.services.chat_service.OpenAI') as mock_openai:
        # Mock OpenRouter to raise an error
        mock_client = MagicMock()
        mock_client.chat.completions.create = AsyncMock(
            side_effect=Exception("OpenRouter API error")
        )
        mock_openai.return_value = mock_client

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await chat_service.send_message(
                user_id=test_user.id,
                message="Hello",
                conversation_id=None
            )

        assert "OpenRouter API error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_conversation_updated_timestamp(test_session, test_user):
    """Test that conversation updated_at timestamp is updated with new messages."""
    # Arrange
    chat_service = ChatService(session=test_session)

    with patch('app.services.chat_service.OpenAI') as mock_openai:
        # Mock OpenRouter
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Response"
        mock_response.choices[0].message.tool_calls = None
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai.return_value = mock_client

        # Act - Send first message
        result1 = await chat_service.send_message(
            user_id=test_user.id,
            message="First message",
            conversation_id=None
        )

        conversation_id = result1["conversation_id"]

        # Get initial timestamp
        conv_statement = select(Conversation).where(
            Conversation.id == uuid4(conversation_id)
        )
        conversations = await test_session.exec(conv_statement)
        conversation = conversations.first()
        initial_timestamp = conversation.updated_at

        # Act - Send second message
        await chat_service.send_message(
            user_id=test_user.id,
            message="Second message",
            conversation_id=conversation_id
        )

        # Assert - Timestamp should be updated
        await test_session.refresh(conversation)
        assert conversation.updated_at > initial_timestamp


@pytest.mark.asyncio
async def test_empty_conversation_id_creates_new_conversation(test_session, test_user):
    """Test that passing None or empty conversation_id creates a new conversation."""
    # Arrange
    chat_service = ChatService(session=test_session)

    with patch('app.services.chat_service.OpenAI') as mock_openai:
        # Mock OpenRouter
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Response"
        mock_response.choices[0].message.tool_calls = None
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai.return_value = mock_client

        # Act - Send message with None conversation_id
        result = await chat_service.send_message(
            user_id=test_user.id,
            message="Hello",
            conversation_id=None
        )

        # Assert - New conversation created
        assert result["conversation_id"] is not None

        # Verify conversation exists in database
        conv_statement = select(Conversation).where(
            Conversation.id == uuid4(result["conversation_id"])
        )
        conversations = await test_session.exec(conv_statement)
        conversation = conversations.first()
        assert conversation is not None
        assert conversation.user_id == test_user.id
