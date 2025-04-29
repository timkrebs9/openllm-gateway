import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from app.auth.models import Base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = f"postgresql+asyncpg://{os.getenv('PGUSER')}:{os.getenv('PGPASSWORD')}@{os.getenv('PGHOST')}:{os.getenv('PGPORT')}/{os.getenv('PGDATABASE')}"

engine = create_async_engine(DATABASE_URL)

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init_models())
