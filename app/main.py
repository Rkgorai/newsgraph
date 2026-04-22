from fastapi import FastAPI
from app.core.config import settings
from app.api.v1 import health

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
    )
    
    # Include routers
    app.include_router(health.router, prefix="/api/v1")
    
    return app

app = create_app()