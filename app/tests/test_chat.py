import pytest
from httpx import AsyncClient, Response, Request
from fastapi import status
import respx # For mocking HTTP requests

from app.main import app # Import the main FastAPI app instance
from app.chat.router import OLLAMA_API_URL, session_data # Access for setup/teardown/assertion
from app.auth.router import fake_users_db # To get a valid token for testing

# Use pytest-asyncio for async tests
pytestmark = pytest.mark.asyncio

# --- Test Fixtures ---

@pytest.fixture(scope="function", autouse=True)
def reset_session_data():
    """Clears session data before each test."""
    session_data.clear()
    yield # Test runs here
    session_data.clear() # Cleanup after test

@pytest.fixture(scope="module")
def test_token() -> str:
    """Provides a valid token for testing authenticated endpoints."""
    # In a real app, you might generate a test JWT
    test_username = list(fake_users_db.keys())[0] # Get the first test user
    return test_username # Using username as token based on fake auth

# --- Test Cases ---

@respx.mock
async def test_chat_endpoint_success(test_token):
    """Test successful chat interaction."""
    session_id = "test-session-1"
    user_message = "Hello Ollama!"
    model_name = "test-model"
    expected_ollama_response = "Hello there! How can I help?"

    # Mock the Ollama API call
    respx.post(OLLAMA_API_URL).mock(return_value=Response(
        status.HTTP_200_OK,
        json={
            "model": model_name,
            "created_at": "2023-10-26T10:00:00Z",
            "message": {
                "role": "assistant",
                "content": expected_ollama_response
            },
            "done": True
        }
    ))

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/chat/",
            json={"session_id": session_id, "message": user_message, "model": model_name},
            headers={"Authorization": f"Bearer {test_token}"} # Add auth header
        )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["response"] == expected_ollama_response
    assert data["session_id"] == session_id
    assert data["model"] == model_name

    # Verify session history
    assert session_id in session_data
    assert len(session_data[session_id]) == 2 # User message + Assistant response
    assert session_data[session_id][0] == {"role": "user", "content": user_message}
    assert session_data[session_id][1] == {"role": "assistant", "content": expected_ollama_response}

@respx.mock
async def test_chat_endpoint_ollama_error(test_token):
    """Test handling of Ollama API error."""
    session_id = "test-session-error"
    user_message = "Trigger error"
    model_name = "error-model"

    # Mock the Ollama API call to return an error
    respx.post(OLLAMA_API_URL).mock(return_value=Response(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        text="Ollama internal failure"
    ))

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/chat/",
            json={"session_id": session_id, "message": user_message, "model": model_name},
            headers={"Authorization": f"Bearer {test_token}"}
        )

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Ollama service error" in response.json()["detail"]

@respx.mock
async def test_chat_endpoint_network_error(test_token):
    """Test handling of network error when connecting to Ollama."""
    session_id = "test-session-network-error"
    user_message = "Trigger network error"
    model_name = "network-error-model"

    # Mock a network error
    respx.post(OLLAMA_API_URL).mock(side_effect=httpx.ConnectError("Connection refused"))

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/chat/",
            json={"session_id": session_id, "message": user_message, "model": model_name},
            headers={"Authorization": f"Bearer {test_token}"}
        )

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert "Could not connect to Ollama service" in response.json()["detail"]

async def test_get_session_history_not_found():
    """Test retrieving history for a non-existent session."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/chat/history/non-existent-session")
    assert response.status_code == status.HTTP_404_NOT_FOUND

async def test_get_session_history_success(test_token):
    """Test retrieving history for an existing session."""
    session_id = "history-session"
    user_message = "Message 1"
    assistant_response = "Response 1"

    # Manually populate session data for testing history retrieval
    session_data[session_id] = [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": assistant_response}
    ]

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(f"/chat/history/{session_id}")

    assert response.status_code == status.HTTP_200_OK
    history = response.json()
    assert len(history) == 2
    assert history[0]["content"] == user_message
    assert history[1]["content"] == assistant_response

# Add test for authentication requirement if needed
# async def test_chat_endpoint_unauthorized():
#     """Test chat endpoint without authentication."""
#     async with AsyncClient(app=app, base_url="http://test") as client:
#         response = await client.post(
#             "/chat/",
#             json={"session_id": "no-auth", "message": "test", "model": "test"}
#         )
#     assert response.status_code == status.HTTP_401_UNAUTHORIZED # Or 403 depending on setup
