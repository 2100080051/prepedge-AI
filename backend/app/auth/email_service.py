"""
Email Service - Send emails via Resend API
"""

import logging
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)

# Lazy import - only when Resend API key is configured
_resend_client = None

def get_resend_client():
    """Get or initialize Resend client"""
    global _resend_client
    if _resend_client is None and settings.RESEND_API_KEY:
        try:
            import resend
            resend.api_key = settings.RESEND_API_KEY
            _resend_client = resend
        except ImportError:
            logger.warning("Resend package not installed. Install with: pip install resend")
    return _resend_client

class EmailService:
    """Send emails via Resend API"""
    
    @staticmethod
    def send_verification_email(email: str, verification_token: str, user_name: Optional[str] = None):
        """Send email verification link to user"""
        try:
            if settings.ENVIRONMENT == "development":
                logger.info(f"✉️  EMAIL VERIFICATION TOKEN for {email}: {verification_token}")
                logger.info(f"Verify link: http://localhost:3000/auth/verify-email?token={verification_token}")
                return True
            
            resend = get_resend_client()
            if not resend:
                logger.warning("Resend not configured. Email not sent to: " + email)
                return False
            
            verification_link = f"{settings.FRONTEND_URL}/auth/verify-email?token={verification_token}"
            
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2>Welcome to PrepEdge! 🚀</h2>
                <p>Hi {user_name or email},</p>
                <p>Thank you for signing up! Please verify your email address to get started.</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_link}" 
                       style="background-color: #4CAF50; color: white; padding: 12px 30px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        Verify Email
                    </a>
                </div>
                
                <p>Or copy this link: <code style="background: #f0f0f0; padding: 5px;">{verification_link}</code></p>
                
                <p>This link expires in 24 hours.</p>
                <p>If you didn't create this account, please ignore this email.</p>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                <p style="color: #666; font-size: 12px;">
                    © 2026 PrepEdge AI. All rights reserved.
                </p>
            </div>
            """
            
            # Send email via Resend
            email_response = resend.Emails.send({
                "from": settings.RESEND_FROM_EMAIL,
                "to": email,
                "subject": "Verify Your PrepEdge Email",
                "html": html_content
            })
            
            if email_response.get("id"):
                logger.info(f"✅ Verification email sent to {email} (ID: {email_response['id']})")
                return True
            else:
                logger.error(f"❌ Failed to send verification email to {email}: {email_response}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send verification email to {email}: {str(e)}")
            return False
    
    @staticmethod
    def send_password_reset_email(email: str, reset_token: str, user_name: Optional[str] = None):
        """Send password reset email with token link"""
        try:
            # For development: print token to console
            if settings.ENVIRONMENT == "development":
                logger.info(f"🔑 PASSWORD RESET TOKEN for {email}: {reset_token}")
                logger.info(f"Reset link: http://localhost:3000/auth/reset-password?token={reset_token}")
                return True
            
            resend = get_resend_client()
            if not resend:
                logger.warning("Resend not configured. Email not sent to: " + email)
                return False
            
            reset_link = f"{settings.FRONTEND_URL}/auth/reset-password?token={reset_token}"
            
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2>Password Reset Request 🔐</h2>
                <p>Hi {user_name or email},</p>
                <p>We received a request to reset your password. Click the button below to reset it.</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_link}" 
                       style="background-color: #2196F3; color: white; padding: 12px 30px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        Reset Password
                    </a>
                </div>
                
                <p>Or copy this link: <code style="background: #f0f0f0; padding: 5px;">{reset_link}</code></p>
                
                <p>This link expires in 1 hour.</p>
                <p>If you didn't request a password reset, please ignore this email and your password will remain unchanged.</p>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                <p style="color: #666; font-size: 12px;">
                    © 2026 PrepEdge AI. All rights reserved.
                </p>
            </div>
            """
            
            email_response = resend.Emails.send({
                "from": settings.RESEND_FROM_EMAIL,
                "to": email,
                "subject": "Reset Your PrepEdge Password",
                "html": html_content
            })
            
            if email_response.get("id"):
                logger.info(f"✅ Password reset email sent to {email}")
                return True
            else:
                logger.error(f"❌ Failed to send password reset email to {email}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to send password reset email to {email}: {str(e)}")
            return False
    
    @staticmethod
    def send_welcome_email(email: str, user_name: Optional[str] = None):
        """Send welcome email to new user after verification"""
        try:
            if settings.ENVIRONMENT == "development":
                logger.info(f"👋 Welcome email for {email}")
                return True
            
            resend = get_resend_client()
            if not resend:
                logger.warning("Resend not configured. Email not sent to: " + email)
                return False
            
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2>Welcome to PrepEdge! 🎉</h2>
                <p>Hi {user_name or email},</p>
                <p>Your email has been verified. You're all set to start your interview preparation journey!</p>
                
                <h3>What's Next?</h3>
                <ul>
                    <li>📚 Complete your profile with your education details</li>
                    <li>🎯 Start practicing DSA questions</li>
                    <li>📊 Track your progress with our analytics dashboard</li>
                    <li>🏆 Earn achievements and badges</li>
                </ul>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{settings.FRONTEND_URL}/dashboard" 
                       style="background-color: #4CAF50; color: white; padding: 12px 30px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        Go to Dashboard
                    </a>
                </div>
                
                <p>Happy learning! 🚀</p>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                <p style="color: #666; font-size: 12px;">
                    © 2026 PrepEdge AI. All rights reserved.
                </p>
            </div>
            """
            
            email_response = resend.Emails.send({
                "from": settings.RESEND_FROM_EMAIL,
                "to": email,
                "subject": "Welcome to PrepEdge! 🚀",
                "html": html_content
            })
            
            if email_response.get("id"):
                logger.info(f"✅ Welcome email sent to {email}")
                return True
            else:
                logger.error(f"❌ Failed to send welcome email to {email}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to send welcome email to {email}: {str(e)}")
            return False
    
    @staticmethod
    def send_login_notification(email: str, user_name: Optional[str] = None, location: Optional[str] = None):
        """Notify user of login attempt"""
        try:
            if settings.ENVIRONMENT == "development":
                logger.info(f"🔐 Login notification for {email}")
                return True
            
            resend = get_resend_client()
            if not resend:
                logger.warning("Resend not configured. Email not sent to: " + email)
                return False
            
            location_text = f"Location: {location}" if location else "Unknown location"
            
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2>Login Notification 🔐</h2>
                <p>Hi {user_name or email},</p>
                <p>A new login to your PrepEdge account was detected.</p>
                
                <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>{location_text}</strong></p>
                    <p>Time: {str(__import__('datetime').datetime.utcnow())}</p>
                </div>
                
                <p>If this wasn't you, please <a href="{settings.FRONTEND_URL}/auth/forgot-password">reset your password</a> immediately.</p>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                <p style="color: #666; font-size: 12px;">
                    © 2026 PrepEdge AI. All rights reserved.
                </p>
            </div>
            """
            
            email_response = resend.Emails.send({
                "from": settings.RESEND_FROM_EMAIL,
                "to": email,
                "subject": "New Login to Your PrepEdge Account",
                "html": html_content
            })
            
            if email_response.get("id"):
                logger.info(f"✅ Login notification sent to {email}")
                return True
            else:
                logger.error(f"❌ Failed to send login notification to {email}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to send login notification to {email}: {str(e)}")
            return False


# Singleton instance
email_service = EmailService()
