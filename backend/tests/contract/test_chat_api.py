"""Contract tests for POST /api/{user_id}/chat endpoint.

This module tests the chat API endpoint contract including:
- Request/response schema validation
- JWT authentication requirement
- User ID validation
- Error response formats

Reference: T020 - Contract test for POST /api/{user_id}/chat endpoint
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
import json

from main import app


# ============================================================================
# Test Client Setup
# ============================================================================

@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


# ============================================================================
# POST /api/{user_id}/chat Contract Tests
# ============================================================================

def test_chat_endpoint_requires_authentication(client, test_user_id):
    """Test that the chat endpoint requires JWT authentication."""
    # Arrange
    endpoint = f"/api/{test_user_id}/chat"
    payload = {
        "message": "Hello",
        "conversation_id": None
    }

    # Act - Request without Authorization header
    response = client.post(endpoint, json=payload)

    # Assert
    assert response.status_code == 401
    assert "detail" in response.json()
    assert "unauthorized" in response.json()["detail"].lower() or \
           "authentication" in response.json()["detail"].lower()


def test_chat_endpoint_rejects_invalid_jwt_token(client, test_user_id):
    """Test that the chat endpoint rejects invalid JWT tokens."""
    # Arrange
    endpoint = f"/api/{test_user_id}/chat"
    payload = {
        "message": "Hello",
        "conversation_id": None
    }
    headers = {
        "Authorization": "Bearer invalid_token_12345"
    }

    # Act
    response = client.post(endpoint, json=payload)

    # Assert
    assert response.status_code == 401


def test_chat_endpoint_validates_user_id_match(client, test_user_id, mock_jwt_token):
    """Test that JWT user_id must match URL user_id."""
    # Arrange
    different_user_id = "different-user-id"
    endpoint = f"/api/{different_user_id}/chat"
    payload = {
        "message": "Hello",
        "conversation_id": None
    }
    headers = {
        "Authorization": mock_jwt_token  # Token for test_user_id
    }

    with patch('routes.chat.verify_jwt') as mock_verify:
        mock_verify.return_value = {"user_id": test_user_id}

        # Act
        response = client.post(endpoint, json=payload, headers=headers)

        # Assert
        assert response.status_code == 403
        assert "detail" in response.json()
        assert "user" in response.json()["detail"].lower()


def test_chat_endpoint_accepts_valid_request(client, test_user_id, mock_jwt_token):
    """Test that the chat endpoint accepts valid requests with proper authentication."""
    # Arrange
    endpoint = f"/api/{test_user_id}/chat"
    payload = {
        "message": "Add buy milk to my tasks",
        "conversation_id": None
    }
    headers = {
        "Authorization": mock_jwt_token
    }

    with patch('routes.chat.verify_jwt') as mock_verify, \
         patch('routes.chat.ChatService') as mock_chat_service:

        mock_verify.return_value = {"user_id": test_user_id}

        # Mock ChatService response
        mock_service_instance = MagicMock()
        mock_service_instance.send_message = AsyncMock(return_value={
            "conversation_id": "conv-123",
            "message": "Task created successfully",
            "role": "assistant"
        })
        mock_chat_service.return_value = mock_service_instance

        # Act
        response = client.post(endpoint, json=payload, headers=headers)

        # Assert
        assert response.status_code == 200


def test_chat_endpoint_validates_request_schema_missing_message(client, test_user_id, mock_jwt_token):
    """Test that the chat endpoint validates request schema - missing message field."""
    # Arrange
    endpoint = f"/api/{test_user_id}/chat"
    payload = {
        "conversation_id": None
        # Missing "message" field
    }
    headers = {
        "Authorization": mock_jwt_token
    }

    with patch('routes.chat.verify_jwt') as mock_verify:
        mock_verify.return_value = {"user_id": test_user_id}

        # Act
        response = client.post(endpoint, json=payload, headers=headers)

        # Assert
        assert response.status_code == 422  # Unprocessable Entity
        assert "detail" in response.json()


def test_chat_endpoint_validates_request_schema_empty_message(client, test_user_id, mock_jwt_token):
    """Test that the chat endpoint validates request schema - empty message."""
    # Arrange
    endpoint = f"/api/{test_user_id}/chat"
    payload = {
        "message": "",
        "conversation_id": None
    }
    headers = {
        "Authorization": mock_jwt_token
    }

    with patch('routes.chat.verify_jwt') as mock_verify:
        mock_verify.return_value = {"user_id": test_user_id}

        # Act
        response = client.post(endpoint, json=payload, headers=headers)

        # Assert
        assert response.status_code == 422 or response.status_code == 400


def test_chat_endpoint_validates_request_schema_invalid_conversation_id(client, test_user_id, mock_jwt_token):
    """Test that the chat endpoint validates conversation_id format."""
    # Arrange
    endpoint = f"/api/{test_user_id}/chat"
    payload = {
        "message": "Hello",
        "conversation_id": "invalid-uuid-format"
    }
    headers = {
        "Authorization": mock_jwt_token
    }

    with patch('routes.chat.verify_jwt') as mock_verify:
        mock_verify.return_value = {"user_id": test_user_id}

        # Act
        response = client.post(endpoint, json=payload, headers=headers)

        # Assert
        # Should either reject at validation level (422) or handle gracefully (400)
        assert response.status_code in [400, 422]


def test_chat_endpoint_response_schema_includes_required_fields(client, test_user_id, mock_jwt_token):
    """Test that the chat endpoint response includes all required fields."""
    # Arrange
    endpoint = f"/api/{test_user_id}/chat"
    payload = {
        "message": "Hello",
        "conversation_id": None
    }
    headers = {
        "Authorization": mock_jwt_token
    }

    with patch('routes.chat.verify_jwt') as mock_verify, \
         patch('routes.chat.ChatService') as mock_chat_service:

        mock_verify.return_value = {"user_id": test_user_id}

        # Mock ChatService response
        mock_service_instance = MagicMock()
        mock_service_instance.send_message = AsyncMock(return_value={
            "conversation_id": "conv-123",
            "message": "Hi there!",
            "role": "assistant"
        })
        mock_chat_service.return_value = mock_service_instance

        # Act
        response = client.post(endpoint, json=payload, headers=headers)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "conversation_id" in data
        assert "message" in data
        assert "role" in data
        assert data["role"] == "assistant"


def test_chat_endpoint_error_response_format(client, test_user_id, mock_jwt_token):
    """Test that error responses follow the expected format."""
    # Arrange
    endpoint = f"/api/{test_user_id}/chat"
    payload = {
        "message": "Hello",
        "conversation_id": None
    }
    headers = {
        "Authorization": mock_jwt_token
    }

    with patch('routes.chat.verify_jwt') as mock_verify, \
         patch('routes.chat.ChatService') as mock_chat_service:

        mock_verify.return_value = {"user_id": test_user_id}

        # Mock ChatService to raise an exception
        mock_service_instance = MagicMock()
        mock_service_instance.send_message = AsyncMock(
            side_effect=Exception("Service error")
        )
        mock_chat_service.return_value = mock_service_instance

        # Act
        response = client.post(endpoint, json=payload, headers=headers)

        # Assert
        assert response.status_code >= 400
        data = response.json()
        assert "detail" in data or "error" in data


def test_chat_endpoint_accepts_optional_conversation_id(client, test_user_id, mock_jwt_token):
    """Test that conversation_id is optional in the request."""
    # Arrange
    endpoint = f"/api/{test_user_id}/chat"
    payload = {
        "message": "Hello"
        # conversation_id is optional
    }
    headers = {
        "Authorization": mock_jwt_token
    }

    with patch('routes.chat.verify_jwt') as mock_verify, \
         patch('routes.chat.ChatService') as mock_chat_service:

        mock_verify.return_value = {"user_id": test_user_id}

        # Mock ChatService response
        mock_service_instance = MagicMock()
        mock_service_instance.send_message = AsyncMock(return_value={
            "conversation_id": "new-conv-123",
            "message": "Hi!",
            "role": "assistant"
        })
        mock_chat_service.return_value = mock_service_instance

        # Act
        response = client.post(endpoint, json=payload, headers=headers)

        # Assert
        assert response.status_code == 200


def test_chat_endpoint_validates_user_id_format(client, mock_jwt_token):
    """Test that the endpoint validates user_id format in URL."""
    # Arrange
    invalid_user_id = ""  # Empty user_id
    endpoint = f"/api/{invalid_user_id}/chat"
    payload = {
        "message": "Hello",
        "conversation_id": None
    }
    headers = {
        "Authorization": mock_jwt_token
    }

    # Act
    response = client.post(endpoint, json=payload, headers=headers)

    # Assert
    # Should return 404 (not found) or 400 (bad request)
    assert response.status_code in [400, 404]


def test_chat_endpoint_content_type_json(client, test_user_id, mock_jwt_token):
    """Test that the endpoint requires JSON content type."""
    # Arrange
    endpoint = f"/api/{test_user_id}/chat"
    payload = "message=Hello&conversation_id=null"  # Form data instead of JSON
    headers = {
        "Authorization": mock_jwt_token,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    with patch('routes.chat.verify_jwt') as mock_verify:
        mock_verify.return_value = {"user_id": test_user_id}

        # Act
        response = client.post(endpoint, data=payload, headers=headers)

        # Assert
        # Should reject non-JSON content type
        assert response.status_code in [400, 415, 422]


def test_chat_endpoint_returns_json_response(client, test_user_id, mock_jwt_token):
    """Test that the endpoint returns JSON response."""
    # Arrange
    endpoint = f"/api/{test_user_id}/chat"
    payload = {
        "message": "Hello",
        "conversation_id": None
    }
    headers = {
        "Authorization": mock_jwt_token
    }

    with patch('routes.chat.verify_jwt') as mock_verify, \
         patch('routes.chat.ChatService') as mock_chat_service:

        mock_verify.return_value = {"user_id": test_user_id}

        # Mock ChatService response
        mock_service_instance = MagicMock()
        mock_service_instance.send_message = AsyncMock(return_value={
            "conversation_id": "conv-123",
            "message": "Response",
            "role": "assistant"
        })
        mock_chat_service.return_value = mock_service_instance

        # Act
        response = client.post(endpoint, json=payload, headers=headers)

        # Assert
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/json")
        # Verify response is valid JSON
        assert isinstance(response.json(), dict)
