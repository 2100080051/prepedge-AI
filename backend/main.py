from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.database.session import engine
from app.database.models import Base
from app.auth.router import router as auth_router
from app.modules.flashlearn.router import router as flashlearn_router
from app.modules.resumeai.router import router as resumeai_router
from app.modules.mockmate.router import router as mockmate_router
from app.modules.learnai.router import router as learnai_router
from app.modules.proctoring.router import router as proctoring_router

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="All-in-One AI Placement Preparation Platform",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(flashlearn_router, prefix=settings.API_V1_STR)
app.include_router(resumeai_router, prefix=settings.API_V1_STR)
app.include_router(mockmate_router, prefix=settings.API_V1_STR)
app.include_router(learnai_router, prefix=settings.API_V1_STR)
app.include_router(proctoring_router, prefix=settings.API_V1_STR)

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "app": settings.APP_NAME}

# Root endpoint
@app.get("/")
def root():
    return {
        "message": "Welcome to PrepEdge AI",
        "version": "1.0.0",
        "docs": "/docs",
        "api_prefix": settings.API_V1_STR
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
