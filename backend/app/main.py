"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Team task management system with employee tracking and Telegram bot integration",
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
        "message": "Team Task Manager API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}


# Include API routers
from app.api import auth, employees, labels, tasks, routines, attendance, dashboard

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(employees.router, prefix="/api/employees", tags=["Employees"])
app.include_router(labels.router, prefix="/api/labels", tags=["Labels"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(routines.router, prefix="/api/routines", tags=["Routines"])
app.include_router(attendance.router, prefix="/api/attendance", tags=["Attendance"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
