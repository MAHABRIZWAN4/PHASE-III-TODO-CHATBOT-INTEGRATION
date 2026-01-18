"""Unit tests for MCP add_task tool.

This module tests the add_task MCP tool functionality including:
- Successful task creation
- Validation errors (empty title, etc.)
- User isolation
- Database errors

Reference: T019 - Unit test for MCP add_task tool
"""

import pytest
from datetime import datetime
from unittest.mock import patch, AsyncMock

from mcp_server.task_tools import add_task
from models import Task


# ============================================================================
# add_task Tool Tests
# ============================================================================

@pytest.mark.asyncio
async def test_add_task_creates_task_successfully(test_session, test_user_id):
    """Test that add_task creates a task successfully with valid inputs."""
    # Arrange
    title = "Buy groceries"
    description = "Milk, eggs, bread"
    due_date = "2026-01-20T10:00:00Z"

    with patch('mcp_server.task_tools.async_session_maker') as mock_session_maker:
        mock_session_maker.return_value.__aenter__.return_value = test_session

        # Act
        result = await add_task(
            user_id=test_user_id,
            title=title,
            description=description,
            due_date=due_date
        )

        # Assert
        assert result["success"] is True
        assert "task" in result
        assert result["task"]["title"] == title
        assert result["task"]["description"] == description
        assert result["task"]["user_id"] == test_user_id
        assert result["task"]["completed"] is False
        assert "message" in result
        assert "created successfully" in result["message"].lower()


@pytest.mark.asyncio
async def test_add_task_creates_task_without_optional_fields(test_session, test_user_id):
    """Test that add_task creates a task with only required fields."""
    # Arrange
    title = "Simple task"

    with patch('mcp_server.task_tools.async_session_maker') as mock_session_maker:
        mock_session_maker.return_value.__aenter__.return_value = test_session

        # Act
        result = await add_task(
            user_id=test_user_id,
            title=title,
            description=None,
            due_date=None
        )

        # Assert
        assert result["success"] is True
        assert result["task"]["title"] == title
        assert result["task"]["description"] is None
        assert result["task"]["due_date"] is None


@pytest.mark.asyncio
async def test_add_task_rejects_empty_title(test_session, test_user_id):
    """Test that add_task rejects empty title."""
    # Arrange
    title = ""

    with patch('mcp_server.task_tools.async_session_maker') as mock_session_maker:
        mock_session_maker.return_value.__aenter__.return_value = test_session

        # Act
        result = await add_task(
            user_id=test_user_id,
            title=title
        )

        # Assert
        assert result["success"] is False
        assert "error" in result
        assert "title" in result["error"].lower()
        assert "empty" in result["error"].lower()
        assert result["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_add_task_rejects_whitespace_only_title(test_session, test_user_id):
    """Test that add_task rejects title with only whitespace."""
    # Arrange
    title = "   "

    with patch('mcp_server.task_tools.async_session_maker') as mock_session_maker:
        mock_session_maker.return_value.__aenter__.return_value = test_session

        # Act
        result = await add_task(
            user_id=test_user_id,
            title=title
        )

        # Assert
        assert result["success"] is False
        assert "error" in result
        assert "title" in result["error"].lower()
        assert result["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_add_task_rejects_title_exceeding_max_length(test_session, test_user_id):
    """Test that add_task rejects title exceeding 200 characters."""
    # Arrange
    title = "A" * 201  # 201 characters

    with patch('mcp_server.task_tools.async_session_maker') as mock_session_maker:
        mock_session_maker.return_value.__aenter__.return_value = test_session

        # Act
        result = await add_task(
            user_id=test_user_id,
            title=title
        )

        # Assert
        assert result["success"] is False
        assert "error" in result
        assert "200" in result["error"]
        assert result["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_add_task_rejects_description_exceeding_max_length(test_session, test_user_id):
    """Test that add_task rejects description exceeding 1000 characters."""
    # Arrange
    title = "Valid title"
    description = "A" * 1001  # 1001 characters

    with patch('mcp_server.task_tools.async_session_maker') as mock_session_maker:
        mock_session_maker.return_value.__aenter__.return_value = test_session

        # Act
        result = await add_task(
            user_id=test_user_id,
            title=title,
            description=description
        )

        # Assert
        assert result["success"] is False
        assert "error" in result
        assert "1000" in result["error"]
        assert result["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_add_task_rejects_invalid_due_date_format(test_session, test_user_id):
    """Test that add_task rejects invalid due_date format."""
    # Arrange
    title = "Valid title"
    due_date = "invalid-date-format"

    with patch('mcp_server.task_tools.async_session_maker') as mock_session_maker:
        mock_session_maker.return_value.__aenter__.return_value = test_session

        # Act
        result = await add_task(
            user_id=test_user_id,
            title=title,
            due_date=due_date
        )

        # Assert
        assert result["success"] is False
        assert "error" in result
        assert "due_date" in result["error"].lower()
        assert "format" in result["error"].lower()
        assert result["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_add_task_rejects_empty_user_id(test_session):
    """Test that add_task rejects empty user_id."""
    # Arrange
    user_id = ""
    title = "Valid title"

    with patch('mcp_server.task_tools.async_session_maker') as mock_session_maker:
        mock_session_maker.return_value.__aenter__.return_value = test_session

        # Act
        result = await add_task(
            user_id=user_id,
            title=title
        )

        # Assert
        assert result["success"] is False
        assert "error" in result
        assert "user" in result["error"].lower()
        assert result["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_add_task_enforces_user_isolation(test_session, test_user_id, test_user_id_2):
    """Test that tasks are isolated by user_id."""
    # Arrange
    title_user1 = "User 1 task"
    title_user2 = "User 2 task"

    with patch('mcp_server.task_tools.async_session_maker') as mock_session_maker:
        mock_session_maker.return_value.__aenter__.return_value = test_session

        # Act - Create tasks for two different users
        result1 = await add_task(user_id=test_user_id, title=title_user1)
        result2 = await add_task(user_id=test_user_id_2, title=title_user2)

        # Assert
        assert result1["success"] is True
        assert result2["success"] is True
        assert result1["task"]["user_id"] == test_user_id
        assert result2["task"]["user_id"] == test_user_id_2
        assert result1["task"]["user_id"] != result2["task"]["user_id"]


@pytest.mark.asyncio
async def test_add_task_handles_database_error(test_session, test_user_id):
    """Test that add_task handles database errors gracefully."""
    # Arrange
    title = "Valid title"

    with patch('mcp_server.task_tools.async_session_maker') as mock_session_maker:
        # Mock session to raise an exception
        mock_session = AsyncMock()
        mock_session.add = AsyncMock(side_effect=Exception("Database connection failed"))
        mock_session_maker.return_value.__aenter__.return_value = mock_session

        # Act
        result = await add_task(
            user_id=test_user_id,
            title=title
        )

        # Assert
        assert result["success"] is False
        assert "error" in result
        assert "database" in result["error"].lower()
        assert result["code"] == "DATABASE_ERROR"


@pytest.mark.asyncio
async def test_add_task_trims_whitespace_from_title(test_session, test_user_id):
    """Test that add_task trims whitespace from title."""
    # Arrange
    title = "  Task with spaces  "
    expected_title = "Task with spaces"

    with patch('mcp_server.task_tools.async_session_maker') as mock_session_maker:
        mock_session_maker.return_value.__aenter__.return_value = test_session

        # Act
        result = await add_task(
            user_id=test_user_id,
            title=title
        )

        # Assert
        assert result["success"] is True
        assert result["task"]["title"] == expected_title


@pytest.mark.asyncio
async def test_add_task_trims_whitespace_from_description(test_session, test_user_id):
    """Test that add_task trims whitespace from description."""
    # Arrange
    title = "Valid title"
    description = "  Description with spaces  "
    expected_description = "Description with spaces"

    with patch('mcp_server.task_tools.async_session_maker') as mock_session_maker:
        mock_session_maker.return_value.__aenter__.return_value = test_session

        # Act
        result = await add_task(
            user_id=test_user_id,
            title=title,
            description=description
        )

        # Assert
        assert result["success"] is True
        assert result["task"]["description"] == expected_description


@pytest.mark.asyncio
async def test_add_task_returns_all_task_fields(test_session, test_user_id):
    """Test that add_task returns all expected task fields."""
    # Arrange
    title = "Complete task"
    description = "With all fields"
    due_date = "2026-01-20T10:00:00Z"

    with patch('mcp_server.task_tools.async_session_maker') as mock_session_maker:
        mock_session_maker.return_value.__aenter__.return_value = test_session

        # Act
        result = await add_task(
            user_id=test_user_id,
            title=title,
            description=description,
            due_date=due_date
        )

        # Assert
        assert result["success"] is True
        task = result["task"]
        assert "id" in task
        assert "user_id" in task
        assert "title" in task
        assert "description" in task
        assert "completed" in task
        assert "due_date" in task
        assert "created_at" in task
        assert "updated_at" in task
