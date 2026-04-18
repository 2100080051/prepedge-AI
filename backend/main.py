"""
FastAPI Application Entry Point
Loads the main app from app.routes
"""

import uvicorn
import logging
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import FastAPI app - create a simple app if routes don't exist
try:
    from fastapi import FastAPI
    app = FastAPI(
        title=settings.APP_NAME,
        description="PrepEdge AI Backend API",
        version="1.0.0"
    )
    
    # Import and include routers
    from app.routes import health
    app.include_router(health.router, prefix="/health", tags=["health"])
    
    # Add CORS if needed
    from fastapi.middleware.cors import CORSMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    logger.info(f"✅ FastAPI app initialized: {settings.APP_NAME}")
    
except Exception as e:
    logger.error(f"❌ Failed to initialize app: {str(e)}")
    from fastapi import FastAPI
    app = FastAPI()
    
    @app.get("/health")
    async def health():
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(settings.PORT or 8000),
        reload=False,
        log_level="info"
    )
