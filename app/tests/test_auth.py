import pytest
from httpx import AsyncClient
from fastapi import status

from app.main import app # Import the main FastAPI app instance
from app.auth.router import fake_users_db # Access for setup/assertion

# Use pytest-asyncio for async tests
pytestmark = pytest.mark.asyncio

# --- Test Cases ---

async def test_get_token_success():
    """Test successful token generation."""
    test_username = list(fake_users_db.keys())[0]
    test_password = fake_users_db[test_username]["hashed_password"] # Using fake password

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/auth/token",
            data={"username": test_username, "password": test_password} # Form data
        )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    # In fake auth, token is username
    assert data["access_token"] == test_username

async def test_get_token_invalid_credentials():
    """Test token generation with incorrect password."""
    test_username = list(fake_users_db.keys())[0]

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/auth/token",
            data={"username": test_username, "password": "wrongpassword"}
        )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Incorrect username or password" in response.json()["detail"]

async def test_read_users_me_success():
    """Test accessing a protected endpoint with a valid token."""
    test_username = list(fake_users_db.keys())[0]
    token = test_username # Using username as token based on fake auth

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/auth/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == test_username
    assert data["email"] == fake_users_db[test_username]["email"]

async def test_read_users_me_invalid_token():
    """Test accessing a protected endpoint with an invalid token."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/auth/users/me",
            headers={"Authorization": "Bearer invalidtoken"}
        )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid authentication credentials" in response.json()["detail"]

async def test_read_users_me_no_token():
    """Test accessing a protected endpoint without a token."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/auth/users/me")

    # FastAPI returns 403 if auth scheme dependency fails without header,
    # or 401 if the scheme runs but validation fails. OAuth2PasswordBearer expects the header.
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "Not authenticated" in response.json()["detail"]
