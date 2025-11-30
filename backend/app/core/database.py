from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from typing import AsyncGenerator
from fastapi import Depends

client: AsyncIOMotorClient | None = None

async def get_db() -> AsyncGenerator:
    global client
    if client is None:
        client = AsyncIOMotorClient(settings.MONGODB_URL)
    
    db = client[settings.DATABASE_NAME]
    try:
        yield db
    finally:
        # In real production we close on shutdown, but for dev this is fine
        pass

# Optional: proper shutdown (we'll wire this in the next step)
async def close_db():
    global client
    if client is not None:
        client.close()
        client = None