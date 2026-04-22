from fastapi import FastAPI
from app.api.v1 import health, feed # <--- Add feed here
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

# Include routers
app.include_router(health.router, prefix="/api/v1/health", tags=["health"])
app.include_router(feed.router, prefix="/api/v1/feed", tags=["feed"]) # <--- Add this

@app.get("/")
async def root():
    return {"message": "Welcome to NewsGraph API", "docs": "/docs"}