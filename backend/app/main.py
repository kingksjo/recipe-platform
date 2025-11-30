from fastapi import FastAPI

app = FastAPI(
    title="Recipe Sharing Platform",
    version="0.1.0",
    description="Recipe Sharing Platform Backend API",
)

@app.get("/")
async def root():
    return {"message": "Welcome to the Recipe Sharing Platform API!"}