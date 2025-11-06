"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Task management system for jewelry shop with Telegram bot integration",
    version="1.0.0",
    debug=settings.DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "message": "Jewelry Shop Task Manager API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}


# Include API routers
from app.api import auth

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])

# Additional routers (to be added)
# from app.api import employees, tasks, routines, reports
# app.include_router(employees.router, prefix="/api/employees", tags=["employees"])
# app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
# app.include_router(routines.router, prefix="/api/routines", tags=["routines"])
# app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
