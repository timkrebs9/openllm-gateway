import logging
import os
from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from passlib.context import CryptContext
from dotenv import load_dotenv
from app.auth.models import User

load_dotenv()
logger = logging.getLogger(__name__)
router = APIRouter()

DATABASE_URL = f"postgresql+asyncpg://{os.getenv('PGUSER')}:{os.getenv('PGPASSWORD')}@{os.getenv('PGHOST')}:{os.getenv('PGPORT')}/{os.getenv('PGDATABASE')}"

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

async def get_db():
    async with AsyncSession(engine) as session:
        yield session

async def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    user = await db.get(User, token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    if user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return user

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

@router.post("/token", response_model=dict)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    user = await db.get(User, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    return {"access_token": user.username, "token_type": "bearer"}

class UserSignup(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    password: str

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user: UserSignup, db: AsyncSession = Depends(get_db)):
    logger.info(f"Signup request for user: {user.username}")
    existing_user = await db.get(User, user.username)
    if existing_user:
        logger.warning(f"Signup attempt with existing username: {user.username}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

    hashed_password = get_password_hash(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        disabled=False
    )
    db.add(new_user)
    await db.commit()
    logger.info(f"User created successfully: {user.username}")
    return {"message": "User created successfully"}

@router.post("/signin", response_model=dict)
async def signin(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    logger.info(f"Signin request for user: {form_data.username}")
    user = await db.get(User, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Signin failed for user: {form_data.username}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    logger.info(f"Signin successful for user: {form_data.username}")
    return {"access_token": user.username, "token_type": "bearer"}

@router.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return {
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name
    }

app = FastAPI(title="Auth Service")
app.include_router(router, prefix="/auth", tags=["Authentication"])
