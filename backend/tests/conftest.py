"""Pytest configuration and shared fixtures for all tests.

This module provides common fixtures for database setup, test users,
and mock configurations used across unit, contract, and integration tests.
"""

import asyncio
import os
from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession as SQLModelAsyncSession

# Import models
from models import User, Task
from app.models.conversation import Conversation
from app.models.message import Message


# ============================================================================
# Pytest Configuration
# ============================================================================

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def test_database_url() -> str:
    """Get test database URL from environment or use in-memory SQLite."""
    # Use in-memory SQLite for tests by default
    # Can be overridden with TEST_DATABASE_URL environment variable
    return os.getenv("TEST_DATABASE_URL", "sqlite+aiosqlite:///:memory:")


@pytest_asyncio.fixture(scope="function")
async def test_engine(test_database_url: str):
    """Create a test database engine."""
    engine = create_async_engine(
        test_database_url,
        echo=False,
        future=True
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    # Drop all tables after test
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session(test_engine) -> AsyncGenerator[SQLModelAsyncSession, None]:
    """Create a test database session."""
    async_session_maker = sessionmaker(
        test_engine,
        class_=SQLModelAsyncSession,
        expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session


# ============================================================================
# Test Data Fixtures
# ============================================================================

@pytest.fixture
def test_user_id() -> str:
    """Generate a test user ID."""
    return str(uuid4())


@pytest.fixture
def test_user_id_2() -> str:
    """Generate a second test user ID for isolation tests."""
    return str(uuid4())


@pytest_asyncio.fixture
async def test_user(test_session: SQLModelAsyncSession, test_user_id: str) -> User:
    """Create a test user in the database."""
    user = User(
        id=test_user_id,
        email="test@example.com",
        password_hash="hashed_password",
        name="Test User"
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_user_2(test_session: SQLModelAsyncSession, test_user_id_2: str) -> User:
    """Create a second test user for isolation tests."""
    user = User(
        id=test_user_id_2,
        email="test2@example.com",
        password_hash="hashed_password",
        name="Test User 2"
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_task(test_session: SQLModelAsyncSession, test_user: User) -> Task:
    """Create a test task in the database."""
    task = Task(
        user_id=test_user.id,
        title="Test Task",
        description="Test Description",
        completed=False
    )
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)
    return task


@pytest_asyncio.fixture
async def test_conversation(test_session: SQLModelAsyncSession, test_user: User) -> Conversation:
    """Create a test conversation in the database."""
    conversation = Conversation(
        user_id=test_user.id
    )
    test_session.add(conversation)
    await test_session.commit()
    await test_session.refresh(conversation)
    return conversation


# ============================================================================
# Mock Fixtures
# ============================================================================

@pytest.fixture
def mock_openrouter_response():
    """Mock OpenRouter API response for chat completion."""
    return {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "anthropic/claude-3.5-sonnet",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Task created successfully: buy milk"
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 50,
            "completion_tokens": 10,
            "total_tokens": 60
        }
    }


@pytest.fixture
def mock_openrouter_tool_call_response():
    """Mock OpenRouter API response with tool call."""
    return {
        "id": "chatcmpl-456",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "anthropic/claude-3.5-sonnet",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": "call_123",
                            "type": "function",
                            "function": {
                                "name": "add_task",
                                "arguments": '{"user_id": "test-user-id", "title": "buy milk"}'
                            }
                        }
                    ]
                },
                "finish_reason": "tool_calls"
            }
        ],
        "usage": {
            "prompt_tokens": 50,
            "completion_tokens": 20,
            "total_tokens": 70
        }
    }


@pytest.fixture
def mock_jwt_token(test_user_id: str) -> str:
    """Generate a mock JWT token for testing."""
    # This is a simplified mock - in real tests, you'd use jwt_utils to create a valid token
    return f"Bearer mock_token_for_{test_user_id}"
