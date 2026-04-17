"""
Google OAuth Verification Service
Verifies Google ID tokens and manages Google login
"""

import httpx
import logging
from typing import Optional, Dict
from app.config import settings

logger = logging.getLogger(__name__)

class GoogleAuthService:
    """Handle Google OAuth verification"""
    
    GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/tokeninfo"
    
    @staticmethod
    async def verify_token(id_token: str) -> Optional[Dict]:
        """
        Verify Google ID token and extract user info
        
        Args:
            id_token: Google ID token from frontend
            
        Returns:
            User info dict with: id, email, name, picture
            or None if verification fails
        """
        try:
            # In development, bypass Google verification (for testing)
            if settings.ENVIRONMENT == "development" and id_token == "TEST_TOKEN":
                return {
                    "sub": "test-google-123",
                    "email": "testgoogle@example.com",
                    "name": "Test Google User",
                    "picture": "https://via.placeholder.com/150"
                }
            
            # Verify token with Google
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{GoogleAuthService.GOOGLE_TOKEN_URL}?id_token={id_token}",
                    timeout=10
                )
            
            if response.status_code != 200:
                logger.error(f"Google token verification failed: {response.text}")
                return None
            
            data = response.json()
            
            # Verify token is for our app
            if data.get("aud") != settings.GOOGLE_CLIENT_ID:
                logger.error("Token not for our app")
                return None
            
            return {
                "sub": data.get("sub"),  # Google user ID
                "email": data.get("email"),
                "name": data.get("name"),
                "picture": data.get("picture")
            }
            
        except Exception as e:
            logger.error(f"Google token verification error: {str(e)}")
            return None
    
    @staticmethod
    def generate_username_from_google(email: str) -> str:
        """
        Generate unique username from Google email
        e.g., john.doe@gmail.com -> john.doe_google
        """
        return email.split("@")[0] + "_google"
