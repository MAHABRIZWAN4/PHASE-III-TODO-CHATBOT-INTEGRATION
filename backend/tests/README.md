# Test Suite for AI-Powered Todo Chatbot

This directory contains comprehensive tests for the AI-Powered Todo Chatbot backend, following Test-Driven Development (TDD) principles.

## Test Structure

```
tests/
├── conftest.py                          # Shared fixtures and configuration
├── unit/                                # Unit tests (isolated component testing)
│   ├── test_chat_service.py           # ChatService.send_message() tests (T018)
│   └── test_mcp_tools.py               # MCP add_task tool tests (T019)
├── contract/                            # Contract tests (API schema validation)
│   └── test_chat_api.py                # POST /api/{user_id}/chat endpoint tests (T020)
└── integration/                         # Integration tests (end-to-end flows)
    └── test_chat_flow.py               # Chat → task creation flow tests (T021)
```

## Test Coverage

### T018: Unit Tests for ChatService.send_message()
**File**: `tests/unit/test_chat_service.py`

Tests the core ChatService functionality:
- ✓ Creates new conversation when none exists
- ✓ Persists user messages to database
- ✓ Persists assistant responses to database
- ✓ Calls OpenRouter API with correct parameters
- ✓ Handles MCP tool calls from AI
- ✓ Handles OpenRouter API errors gracefully
- ✓ Validates user_id and message inputs
- ✓ Returns expected response structure

**Total Tests**: 10 test cases

### T019: Unit Tests for MCP add_task Tool
**File**: `tests/unit/test_mcp_tools.py`

Tests the add_task MCP tool:
- ✓ Creates tasks successfully with valid inputs
- ✓ Creates tasks with only required fields
- ✓ Rejects empty or whitespace-only titles
- ✓ Rejects titles exceeding 200 characters
- ✓ Rejects descriptions exceeding 1000 characters
- ✓ Rejects invalid due_date formats
- ✓ Rejects empty user_id
- ✓ Enforces user isolation
- ✓ Handles database errors gracefully
- ✓ Trims whitespace from inputs
- ✓ Returns all expected task fields

**Total Tests**: 14 test cases

### T020: Contract Tests for POST /api/{user_id}/chat
**File**: `tests/contract/test_chat_api.py`

Tests the chat API endpoint contract:
- ✓ Requires JWT authentication
- ✓ Rejects invalid JWT tokens
- ✓ Validates JWT user_id matches URL user_id
- ✓ Accepts valid authenticated requests
- ✓ Validates request schema (missing/empty message)
- ✓ Validates conversation_id format
- ✓ Response includes required fields
- ✓ Error responses follow expected format
- ✓ Accepts optional conversation_id
- ✓ Validates user_id format in URL
- ✓ Requires JSON content type
- ✓ Returns JSON response

**Total Tests**: 14 test cases

### T021: Integration Tests for Chat Flow
**File**: `tests/integration/test_chat_flow.py`

Tests the complete end-to-end flow:
- ✓ Full chat → AI interprets → creates task → responds
- ✓ Conversation persistence across messages
- ✓ Message history maintained and ordered
- ✓ Multiple tasks created in conversation
- ✓ User isolation in chat flow
- ✓ Error handling in chat flow
- ✓ Conversation updated_at timestamp updates
- ✓ Empty conversation_id creates new conversation

**Total Tests**: 9 test cases

## Running Tests

### Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Run All Tests

```bash
pytest tests/
```

### Run Specific Test Suites

```bash
# Unit tests only
pytest tests/unit/

# Contract tests only
pytest tests/contract/

# Integration tests only
pytest tests/integration/

# Specific test file
pytest tests/unit/test_chat_service.py

# Specific test function
pytest tests/unit/test_mcp_tools.py::test_add_task_creates_task_successfully
```

### Run with Coverage

```bash
pytest --cov=app --cov=mcp_server --cov-report=term-missing tests/
```

### Run with Verbose Output

```bash
pytest -v tests/
```

## Test Database

Tests use an in-memory SQLite database by default for fast, isolated testing. You can override this with the `TEST_DATABASE_URL` environment variable:

```bash
export TEST_DATABASE_URL="postgresql+asyncpg://user:pass@localhost/test_db"
pytest tests/
```

## TDD Approach

These tests were written **BEFORE** implementation (Test-Driven Development):

1. **Red Phase**: Tests are written first and FAIL (no implementation exists)
2. **Green Phase**: Implementation is written to make tests PASS
3. **Refactor Phase**: Code is improved while keeping tests passing

### Expected Behavior (Current State)

Since the implementation doesn't exist yet, all tests should **FAIL** with import errors or missing module errors. This is expected and correct for TDD.

Example expected failures:
- `ModuleNotFoundError: No module named 'app.services.chat_service'`
- `ModuleNotFoundError: No module named 'routes.chat'`
- `AttributeError: module 'app' has no attribute 'services'`

## Fixtures

The `conftest.py` file provides shared fixtures:

- `test_database_url`: Test database connection string
- `test_engine`: Async database engine for tests
- `test_session`: Async database session
- `test_user_id`: Generated test user ID
- `test_user`: Test user in database
- `test_task`: Test task in database
- `test_conversation`: Test conversation in database
- `mock_openrouter_response`: Mock OpenRouter API response
- `mock_openrouter_tool_call_response`: Mock tool call response
- `mock_jwt_token`: Mock JWT token for authentication

## Next Steps

After completing these tests (T018-T021), proceed with implementation tasks:

1. **T022-T023**: Create Pydantic models (ChatRequest, ChatResponse)
2. **T024-T027**: Implement ChatService with OpenRouter integration
3. **T028-T031**: Create chat API endpoint with authentication
4. **T032-T038**: Build frontend components and tests

As implementation progresses, tests should transition from **RED** (failing) to **GREEN** (passing).

## Test Statistics

- **Total Test Files**: 4
- **Total Test Cases**: 47
- **Total Lines of Test Code**: ~1,456 lines
- **Coverage Target**: 80%+

## References

- Task IDs: T018, T019, T020, T021
- Spec: `/specs/003-ai-todo-chatbot/spec.md`
- Plan: `/specs/003-ai-todo-chatbot/plan.md`
- Tasks: `/specs/003-ai-todo-chatbot/tasks.md`
