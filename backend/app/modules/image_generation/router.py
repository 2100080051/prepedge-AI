"""
Image Generation API Routes
Endpoints for generating and managing AI-generated images
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import asyncio
import logging

from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.database.models import User
from app.modules.image_generation.models import (
    PollinationsImageGenerator,
    ImageGenerationService,
    ImageType,
    ImageGenerationBase
)
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/image-generation",
    tags=["image-generation"]
)

# Initialize API key (from environment)
POLLINATIONS_API_KEY = getattr(settings, 'POLLINATIONS_API_KEY', '')


class ImageGenerationRequest(BaseModel):
    """Request to generate an image"""
    prompt: str
    image_type: str = "concept_art"
    width: int = 512
    height: int = 512
    quality: str = "medium"  # low, medium, high


class ImageGenerationResponse(BaseModel):
    """Response from image generation"""
    success: bool
    image_url: Optional[str] = None
    image_type: Optional[str] = None
    generation_time_ms: Optional[int] = None
    error: Optional[str] = None


@router.post("/generate", response_model=ImageGenerationResponse)
async def generate_image(
    request: ImageGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None
):
    """
    Generate an AI image using Pollinations.ai
    
    Supports:
    - Company profiles
    - Interview insights
    - Success stories
    - Gamification badges
    - Custom concept art
    
    Quality levels:
    - low: Fast, 15 steps
    - medium: Balanced, 20 steps
    - high: Best quality, 30 steps
    """
    
    if not POLLINATIONS_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Image generation not configured (missing API key)"
        )
    
    try:
        # Get image type
        image_type = ImageType[request.image_type.upper()] if request.image_type.upper() in ImageType.__members__ else ImageType.CONCEPT_ART
        
        # Initialize generator
        generator = PollinationsImageGenerator(POLLINATIONS_API_KEY)
        
        # Generate image
        result = await generator.generate_image(
            prompt=request.prompt,
            image_type=image_type,
            width=request.width,
            height=request.height,
            quality=request.quality
        )
        
        if result and result.get("success"):
            # Save to database asynchronously
            if background_tasks:
                background_tasks.add_task(
                    _save_image_to_db,
                    db=db,
                    user_id=current_user.id,
                    prompt=request.prompt,
                    image_url=result.get("image_url"),
                    image_type=image_type,
                    generation_time_ms=result.get("generation_time_ms")
                )
            
            return ImageGenerationResponse(
                success=True,
                image_url=result.get("image_url"),
                image_type=image_type.value,
                generation_time_ms=result.get("generation_time_ms")
            )
        else:
            error = result.get("error", "Unknown error") if result else "Generation failed"
            logger.error(f"Image generation failed: {error}")
            return ImageGenerationResponse(
                success=False,
                error=error
            )
            
    except ValueError as e:
        logger.error(f"Invalid image type: {str(e)}")
        return ImageGenerationResponse(
            success=False,
            error=f"Invalid image type: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Image generation error: {str(e)}")
        return ImageGenerationResponse(
            success=False,
            error=str(e)
        )


@router.post("/generate/company-profile")
async def generate_company_profile_image(
    company_name: str = Query(..., description="Name of the company"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a professional image for a company profile"""
    
    if not POLLINATIONS_API_KEY:
        raise HTTPException(status_code=500, detail="Image generation not configured")
    
    try:
        generator = PollinationsImageGenerator(POLLINATIONS_API_KEY)
        result = await generator.generate_company_profile_image(company_name)
        
        if result and result.get("success"):
            return {
                "status": "success",
                "company": company_name,
                "image_url": result.get("url"),
                "generation_time_ms": result.get("generation_time_ms")
            }
        else:
            return {
                "status": "failed",
                "company": company_name,
                "error": result.get("error") if result else "Unknown error"
            }
    except Exception as e:
        logger.error(f"Company profile image generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/interview-insights")
async def generate_interview_insights_image(
    insights: str = Query(..., description="Interview insights summary"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a visualization for interview insights"""
    
    if not POLLINATIONS_API_KEY:
        raise HTTPException(status_code=500, detail="Image generation not configured")
    
    try:
        generator = PollinationsImageGenerator(POLLINATIONS_API_KEY)
        result = await generator.generate_interview_insights_image(insights)
        
        if result and result.get("success"):
            return {
                "status": "success",
                "image_url": result.get("url"),
                "generation_time_ms": result.get("generation_time_ms")
            }
        else:
            return {
                "status": "failed",
                "error": result.get("error") if result else "Unknown error"
            }
    except Exception as e:
        logger.error(f"Interview insights image generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/success-story")
async def generate_success_story_image(
    company: str = Query(..., description="Company name"),
    role: str = Query(..., description="Job role"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate an inspiring image for a success story"""
    
    if not POLLINATIONS_API_KEY:
        raise HTTPException(status_code=500, detail="Image generation not configured")
    
    try:
        generator = PollinationsImageGenerator(POLLINATIONS_API_KEY)
        result = await generator.generate_success_story_image(company, role)
        
        if result and result.get("success"):
            return {
                "status": "success",
                "company": company,
                "role": role,
                "image_url": result.get("url"),
                "generation_time_ms": result.get("generation_time_ms")
            }
        else:
            return {
                "status": "failed",
                "error": result.get("error") if result else "Unknown error"
            }
    except Exception as e:
        logger.error(f"Success story image generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/badge")
async def generate_gamification_badge(
    achievement: str = Query(..., description="Achievement description"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a badge image for gamification"""
    
    if not POLLINATIONS_API_KEY:
        raise HTTPException(status_code=500, detail="Image generation not configured")
    
    try:
        generator = PollinationsImageGenerator(POLLINATIONS_API_KEY)
        result = await generator.generate_gamification_badge(achievement)
        
        if result and result.get("success"):
            return {
                "status": "success",
                "achievement": achievement,
                "badge_url": result.get("url"),
                "generation_time_ms": result.get("generation_time_ms")
            }
        else:
            return {
                "status": "failed",
                "error": result.get("error") if result else "Unknown error"
            }
    except Exception as e:
        logger.error(f"Badge generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_generation_history(
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's image generation history"""
    
    try:
        images = db.query(ImageGenerationBase).filter(
            ImageGenerationBase.user_id == current_user.id,
            ImageGenerationBase.is_generated == True
        ).order_by(
            ImageGenerationBase.created_at.desc()
        ).limit(limit).all()
        
        return {
            "status": "success",
            "user_id": current_user.id,
            "total": len(images),
            "images": [
                {
                    "id": img.id,
                    "url": img.image_url,
                    "type": img.image_type,
                    "prompt": img.prompt[:100],
                    "generation_time_ms": img.generation_time_ms,
                    "created_at": img.created_at.isoformat()
                }
                for img in images
            ]
        }
    except Exception as e:
        logger.error(f"Failed to get generation history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_generation_stats(
    db: Session = Depends(get_db)
):
    """Get platform image generation statistics"""
    
    try:
        service = ImageGenerationService(POLLINATIONS_API_KEY)
        stats = service.get_generation_stats(db)
        
        return {
            "status": "success",
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Failed to get stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def image_generation_health():
    """Health check for image generation module"""
    
    api_configured = bool(POLLINATIONS_API_KEY)
    
    return {
        "status": "healthy" if api_configured else "degraded",
        "module": "image_generation",
        "api_configured": api_configured,
        "features": [
            "generate",
            "generate/company-profile",
            "generate/interview-insights",
            "generate/success-story",
            "generate/badge",
            "history",
            "stats"
        ]
    }


# Helper function to save image to database
def _save_image_to_db(
    db: Session,
    user_id: int,
    prompt: str,
    image_url: str,
    image_type: ImageType,
    generation_time_ms: int
):
    """Save generated image to database (background task)"""
    try:
        service = ImageGenerationService(POLLINATIONS_API_KEY)
        service.save_generated_image(
            db=db,
            user_id=user_id,
            prompt=prompt,
            image_url=image_url,
            image_type=image_type,
            generation_time_ms=generation_time_ms
        )
        logger.info(f"Saved image to database for user {user_id}")
    except Exception as e:
        logger.error(f"Failed to save image to database: {str(e)}")


# Optional: Endpoint to test API connectivity
@router.get("/test")
async def test_image_generation():
    """Test image generation API connectivity"""
    
    if not POLLINATIONS_API_KEY:
        return {
            "status": "error",
            "message": "API key not configured"
        }
    
    try:
        generator = PollinationsImageGenerator(POLLINATIONS_API_KEY)
        result = await generator.generate_image(
            prompt="Test image: simple red square",
            image_type=ImageType.CONCEPT_ART,
            width=256,
            height=256,
            quality="low"
        )
        
        if result and result.get("success"):
            return {
                "status": "success",
                "message": "✅ API is working",
                "generation_time_ms": result.get("generation_time_ms"),
                "image_url": result.get("url")[:100] + "..."
            }
        else:
            error = result.get("error") if result else "Unknown error"
            return {
                "status": "failed",
                "message": f"❌ API returned error: {error}"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"❌ Error: {str(e)[:200]}"
        }
