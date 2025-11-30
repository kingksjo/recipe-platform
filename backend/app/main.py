from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.database import get_db, close_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"Backend starting in {settings.ENV} mode")
    yield
    # Shutdown
    await close_db()

app = FastAPI(
    title="Recipe Sharing Platform",
    version="0.1.0",
    lifespan=lifespan,
)

@app.get("/")
async def root(db = Depends(get_db)):
    # Just to prove DB connection works
    collections = await db.list_collection_names()
    return {
        "message": "Response from FastAPI backend!",
        "db_collections": collections,
        "env": settings.ENV,
    }