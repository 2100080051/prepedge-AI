"""
Image Generation Module
Integrates Pollinations.ai for AI-powered image generation
Used for: Company profiles, feature visualizations, resume covers, interview insights
"""

import requests
import asyncio
import logging
from typing import Optional, Dict, List
from enum import Enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.orm import Session
from app.database.session import Base

logger = logging.getLogger(__name__)


class ImageGenerationBase(Base):
    """Track generated images for reuse and analytics"""
    __tablename__ = "generated_images"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=True)
    prompt = Column(Text, nullable=False)
    image_url = Column(String(500), nullable=True)
    image_path = Column(String(255), nullable=True)
    
    # Image metadata
    width = Column(Integer, default=512)
    height = Column(Integer, default=512)
    quality = Column(String(20), default="high")  # low, medium, high
    
    # Generation info
    provider = Column(String(50), default="pollinations")  # pollinations, local, etc
    generation_time_ms = Column(Integer, nullable=True)
    
    # Status
    is_generated = Column(Boolean, default=False)
    is_cached = Column(Boolean, default=False)
    error_message = Column(String(255), nullable=True)
    
    # Context
    image_type = Column(String(50))  # company_profile, feature_vis, resume_cover, etc
    context_data = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ImageType(str, Enum):
    """Types of images that can be generated"""
    COMPANY_PROFILE = "company_profile"
    FEATURE_VISUALIZATION = "feature_visualization"
    RESUME_COVER = "resume_cover"
    INTERVIEW_INSIGHTS = "interview_insights"
    GAMIFICATION_BADGE = "gamification_badge"
    SUCCESS_STORY = "success_story"
    CONCEPT_ART = "concept_art"


class PollinationsImageGenerator:
    """
    AI Image Generator using Pollinations.ai API
    
    Docs: https://pollinations.ai
    Features:
    - Fast image generation (Flux model)
    - Multiple model support
    - High quality outputs
    - Uses public endpoint (no auth required)
    """
    
    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        # Using the public endpoint which is more reliable
        self.base_url = "https://pollinations.ai/images"
        self.model = "flux"  # or "flux-pro", "flux-realism"
        self.timeout = 120  # seconds
    
    async def generate_image(
        self,
        prompt: str,
        image_type: ImageType = ImageType.CONCEPT_ART,
        width: int = 512,
        height: int = 512,
        quality: str = "high"
    ) -> Optional[Dict]:
        """
        Generate an image using Pollinations.ai public endpoint
        
        Args:
            prompt: Detailed description of image to generate
            image_type: Type of image being generated
            width: Image width (512, 768, 1024)
            height: Image height (512, 768, 1024)
            quality: "low" (fast), "medium", "high" (slow)
        
        Returns:
            Dict with image URL and metadata, or None if failed
        """
        import time
        start_time = time.time()
        
        try:
            logger.info(f"Generating {image_type.value} image: {prompt[:100]}")
            
            # Build URL for public endpoint
            # Format: https://pollinations.ai/images/{prompt}?model=flux&width=1024&height=1024
            clean_prompt = prompt.replace(" ", "%20")
            
            # Determine seed for reproducibility
            import hashlib
            seed = int(hashlib.md5(prompt.encode()).hexdigest(), 16) % (2**32)
            
            url = f"{self.base_url}/{clean_prompt}?model={self.model}&width={width}&height={height}&seed={seed}"
            
            response = requests.get(url, timeout=self.timeout)
            
            generation_time = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                # The response content IS the image
                # We need to store or return the URL
                # Since this is a direct image response, we return the request URL as the image URL
                
                logger.info(f"✅ Image generated in {generation_time}ms")
                return {
                    "image_url": url,
                    "success": True,
                    "image_type": image_type.value,
                    "prompt": prompt,
                    "width": width,
                    "height": height,
                    "generation_time_ms": generation_time,
                    "provider": "pollinations"
                }
            else:
                error_msg = f"Status {response.status_code}"
                logger.error(f"❌ Image generation failed: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "status_code": response.status_code,
                    "generation_time_ms": generation_time
                }
                
        except requests.Timeout:
            generation_time = int((time.time() - start_time) * 1000)
            logger.error("⏱️  Image generation timeout")
            return {
                "success": False,
                "error": "Request timeout",
                "generation_time_ms": generation_time
            }
        except Exception as e:
            generation_time = int((time.time() - start_time) * 1000)
            logger.error(f"❌ Image generation error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "generation_time_ms": generation_time
            }
    
    def _get_inference_steps(self, quality: str) -> int:
        """Get inference steps based on quality level"""
        return {
            "low": 15,
            "medium": 20,
            "high": 30
        }.get(quality, 20)
    
    async def generate_company_profile_image(self, company_name: str) -> Optional[Dict]:
        """Generate a professional image for company profile"""
        prompt = f"Professional company profile image for {company_name}. Modern, corporate, clean design. High quality professional photography style."
        return await self.generate_image(
            prompt=prompt,
            image_type=ImageType.COMPANY_PROFILE,
            quality="high"
        )
    
    async def generate_interview_insights_image(self, insights: str) -> Optional[Dict]:
        """Generate visualization for interview insights"""
        prompt = f"Professional infographic visualization showing interview insights: {insights[:100]}. Clean, modern design with charts and statistics."
        return await self.generate_image(
            prompt=prompt,
            image_type=ImageType.INTERVIEW_INSIGHTS,
            quality="medium"
        )
    
    async def generate_success_story_image(self, company: str, role: str) -> Optional[Dict]:
        """Generate image for success story"""
        prompt = f"Inspiring success story visualization. Person celebrating getting {role} position at {company}. Professional, motivational design."
        return await self.generate_image(
            prompt=prompt,
            image_type=ImageType.SUCCESS_STORY,
            quality="high"
        )
    
    async def generate_gamification_badge(self, achievement: str) -> Optional[Dict]:
        """Generate a badge for gamification achievement"""
        prompt = f"Colorful, fun gamification achievement badge for: {achievement}. Suitable for web interface. Vibrant, modern design."
        return await self.generate_image(
            prompt=prompt,
            image_type=ImageType.GAMIFICATION_BADGE,
            width=256,
            height=256,
            quality="medium"
        )


class ImageGenerationService:
    """Service for managing image generation across the platform"""
    
    def __init__(self, api_key: str):
        self.generator = PollinationsImageGenerator(api_key)
        
    def save_generated_image(
        self,
        db: Session,
        user_id: Optional[int],
        prompt: str,
        image_url: str,
        image_type: ImageType,
        generation_time_ms: int,
        provider: str = "pollinations"
    ) -> ImageGenerationBase:
        """Save generated image to database for tracking"""
        
        image = ImageGenerationBase(
            user_id=user_id,
            prompt=prompt,
            image_url=image_url,
            image_type=image_type.value,
            provider=provider,
            generation_time_ms=generation_time_ms,
            is_generated=True
        )
        
        db.add(image)
        db.commit()
        db.refresh(image)
        
        logger.info(f"Saved generated image (ID: {image.id}, Type: {image_type.value})")
        return image
    
    def get_cached_image(
        self,
        db: Session,
        image_type: ImageType,
        context_data: str
    ) -> Optional[str]:
        """Get cached image if available"""
        image = db.query(ImageGenerationBase).filter(
            ImageGenerationBase.image_type == image_type.value,
            ImageGenerationBase.context_data == context_data,
            ImageGenerationBase.is_generated == True
        ).first()
        
        return image.image_url if image else None
    
    def get_images_by_type(
        self,
        db: Session,
        image_type: ImageType,
        limit: int = 10
    ) -> List[ImageGenerationBase]:
        """Get recent images of a specific type"""
        return db.query(ImageGenerationBase).filter(
            ImageGenerationBase.image_type == image_type.value,
            ImageGenerationBase.is_generated == True
        ).order_by(
            ImageGenerationBase.created_at.desc()
        ).limit(limit).all()
    
    def get_generation_stats(self, db: Session) -> Dict:
        """Get image generation statistics"""
        total = db.query(ImageGenerationBase).count()
        successful = db.query(ImageGenerationBase).filter(
            ImageGenerationBase.is_generated == True
        ).count()
        
        avg_time = db.query(
            db.func.avg(ImageGenerationBase.generation_time_ms)
        ).filter(
            ImageGenerationBase.is_generated == True
        ).scalar() or 0
        
        by_type = db.query(
            ImageGenerationBase.image_type,
            db.func.count(ImageGenerationBase.id)
        ).filter(
            ImageGenerationBase.is_generated == True
        ).group_by(
            ImageGenerationBase.image_type
        ).all()
        
        return {
            "total_images": total,
            "successful": successful,
            "failed": total - successful,
            "avg_generation_time_ms": int(avg_time),
            "by_type": {item_type: count for item_type, count in by_type}
        }


# Helper function for quick image generation
async def generate_image_quickly(
    api_key: str,
    prompt: str,
    image_type: ImageType = ImageType.CONCEPT_ART
) -> Optional[Dict]:
    """Quick function to generate an image"""
    generator = PollinationsImageGenerator(api_key)
    return await generator.generate_image(prompt, image_type)
