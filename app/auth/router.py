import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()

# This is where clients will post username/password to get a token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# --- Placeholder User Database ---
# In a real app, fetch this from a database
fake_users_db = {
    "testuser": {
        "username": "testuser",
        "full_name": "Test User",
        "email": "test@example.com",
        "hashed_password": "fakehashedpassword", # Never store plain text passwords! Use passlib
        "disabled": False,
    }
}

# --- Placeholder Token Model ---
class Token(BaseModel):
    access_token: str
    token_type: str

# --- Placeholder Token Validation ---
# In a real app, use JWT, verify signature, expiry, etc.
def fake_decode_token(token):
    # This is insecure! Replace with actual JWT decoding and validation.
    user = fake_users_db.get(token) # Using token directly as username for demo
    if not user:
        return None
    return user

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Placeholder function to validate a token and return the user.
    Replace with actual JWT validation.
    """
    logger.debug(f"Attempting to validate token: {token[:5]}...") # Log only prefix
    user = fake_decode_token(token)
    if not user:
        logger.warning("Token validation failed.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.get("disabled"):
        logger.warning(f"Authentication attempt for disabled user: {user.get('username')}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    logger.info(f"Token validated successfully for user: {user.get('username')}")
    return user

# --- Placeholder Token Endpoint ---
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Placeholder endpoint to issue a token.
    Replace with actual password verification and token generation.
    """
    logger.info(f"Token request received for user: {form_data.username}")
    user = fake_users_db.get(form_data.username)
    # WARNING: This compares plain text passwords - DO NOT USE IN PRODUCTION
    # Use a library like passlib to hash and verify passwords securely.
    if not user or user.get("hashed_password") != form_data.password:
        logger.warning(f"Authentication failed for user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # In a real app, create a JWT token here. Using username as token for demo.
    access_token = user["username"]
    logger.info(f"Token generated successfully for user: {form_data.username}")
    return {"access_token": access_token, "token_type": "bearer"}

# --- Example Protected Endpoint ---
@router.get("/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """
    Example endpoint protected by authentication.
    """
    logger.info(f"Accessing protected user info for: {current_user.get('username')}")
    # Return user info obtained from the token validation
    return current_user
