from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from secrets import token_urlsafe
import logging
from app.database.session import get_db
from app.database.models import User
from app.auth.schemas import (
    UserRegister, UserLogin, TokenResponse, UserResponse,
    ForgotPasswordRequest, ResetPasswordRequest, GoogleLoginRequest,
    EmailVerificationRequest, VerificationResponse, ResendVerificationRequest
)
from app.auth.utils import get_password_hash, verify_password, create_access_token
from app.auth.dependencies import get_current_user
from app.auth.email_service import email_service
from app.auth.google_auth import GoogleAuthService
from app.config import settings
from app.security import InputValidator, SecurityEventLogger, get_client_ip

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
def register(user_data: UserRegister, request: Request, db: Session = Depends(get_db)):
    """Register a new user with email and password - sends verification email"""
    try:
        ip = get_client_ip(request)
        
        # Validate input
        if not user_data.email or not user_data.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and password are required"
            )
        
        # Security: Check for SQL injection in all string fields
        dangerous_fields = {
            "email": user_data.email,
            "username": user_data.username,
            "full_name": user_data.full_name,
        }
        
        for field_name, value in dangerous_fields.items():
            if value and InputValidator.check_sql_injection(value):
                SecurityEventLogger.log_sql_injection_attempt(
                    endpoint="/auth/register",
                    ip=ip,
                    payload=value
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid characters in {field_name}"
                )
            
            if value and InputValidator.check_xss_injection(value):
                SecurityEventLogger.log_xss_attempt(
                    endpoint="/auth/register",
                    ip=ip,
                    payload=value
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid characters in {field_name}"
                )
        
        # Validate email format
        if not InputValidator.validate_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )
        
        # Validate password strength
        is_valid, message = InputValidator.validate_password(user_data.password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password requirements: {message}"
            )
        
        # Auto-generate username from email if not provided
        username = user_data.username
        if not username:
            username = user_data.email.split('@')[0]
            counter = 1
            base_username = username
            while db.query(User).filter(User.username == username).first():
                username = f"{base_username}{counter}"
                counter += 1
        else:
            # Validate username format
            if not InputValidator.validate_username(username):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username must be 3-50 characters and contain only letters, numbers, hyphens, and underscores"
                )
        
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.email == user_data.email) | (User.username == username)
        ).first()
        
        if existing_user:
            if existing_user.email == user_data.email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered. Try login or use forgot password."
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken. Choose another username."
                )
        
        # Create new user (NOT verified by default)
        user = User(
            email=user_data.email,
            username=username,
            full_name=user_data.full_name,
            phone_number=user_data.phone_number,
            college=user_data.college,
            graduation_year=user_data.graduation_year,
            course=user_data.course,
            years_of_experience=user_data.years_of_experience,
            hashed_password=get_password_hash(user_data.password),
            subscription_plan="free",
            is_active=True,
            is_email_verified=False  # NEW: Email not verified yet
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Generate email verification token
        verification_token = token_urlsafe(32)
        user.email_verification_token = verification_token
        user.email_verification_expires = datetime.utcnow() + timedelta(hours=24)
        db.commit()
        
        # Send verification email
        email_service.send_verification_email(
            email=user.email,
            verification_token=verification_token,
            user_name=user.full_name
        )
        
        # Log successful registration
        SecurityEventLogger.log_successful_event(
            event="user_registration",
            user_id=user.id,
            ip=ip
        )
        
        return {
            "user_id": user.id,
            "email": user.email,
            "username": user.username,
            "message": "Registration successful! Check your email to verify your account.",
            "verification_required": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, request: Request, db: Session = Depends(get_db)):
    """Login with email and password"""
    try:
        ip = get_client_ip(request)
        
        # Security: Check for SQL injection
        if InputValidator.check_sql_injection(credentials.email):
            SecurityEventLogger.log_sql_injection_attempt(
                endpoint="/auth/login",
                ip=ip,
                payload=credentials.email
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid request"
            )
        
        # Find user
        user = db.query(User).filter(User.email == credentials.email).first()
        
        if not user:
            SecurityEventLogger.log_failed_login(
                email=credentials.email,
                ip=ip,
                reason="User not found"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # NEW: Check if email is verified
        if not user.is_email_verified:
            SecurityEventLogger.log_failed_login(
                email=credentials.email,
                ip=ip,
                reason="Email not verified"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email not verified. Please check your email for verification link."
            )
        
        # Check password
        if not user.hashed_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="This account uses OAuth login. Use Google sign-in instead."
            )
        
        if not verify_password(credentials.password, user.hashed_password):
            SecurityEventLogger.log_failed_login(
                email=credentials.email,
                ip=ip,
                reason="Invalid password"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if user is active
        if not user.is_active:
            SecurityEventLogger.log_failed_login(
                email=credentials.email,
                ip=ip,
                reason="Account deactivated"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account has been deactivated"
            )
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires
        )
        
        # Log successful login
        SecurityEventLogger.log_successful_event(
            event="user_login",
            user_id=user.id,
            ip=ip
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user.id,
            "user_name": user.username
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logging.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.post("/verify-email", response_model=VerificationResponse)
def verify_email(request: EmailVerificationRequest, db: Session = Depends(get_db)):
    """Verify user email using token from email link"""
    try:
        # Find user with valid token
        user = db.query(User).filter(
            User.email_verification_token == request.token,
            User.email_verification_expires > datetime.utcnow()
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification link. Please request a new one."
            )
        
        # Mark email as verified
        user.is_email_verified = True
        user.email_verification_token = None
        user.email_verification_expires = None
        db.commit()
        
        # Send welcome email
        email_service.send_welcome_email(
            email=user.email,
            user_name=user.full_name
        )
        
        return {
            "success": True,
            "message": "Email verified successfully! You can now login to your account.",
            "user_id": user.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Email verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email verification failed. Please try again."
        )

@router.post("/resend-verification-email", response_model=dict)
def resend_verification_email(request: ResendVerificationRequest, db: Session = Depends(get_db)):
    """Resend verification email if user hasn't verified yet"""
    try:
        user = db.query(User).filter(User.email == request.email).first()
        
        # For security - don't reveal if email exists
        safe_response = {
            "message": "If this email exists and is unverified, a new verification link has been sent.",
            "email": request.email
        }
        
        if not user:
            return safe_response
        
        # Check if already verified
        if user.is_email_verified:
            return {
                "message": "This email is already verified. You can login to your account.",
                "email": request.email
            }
        
        # Generate new verification token
        verification_token = token_urlsafe(32)
        user.email_verification_token = verification_token
        user.email_verification_expires = datetime.utcnow() + timedelta(hours=24)
        db.commit()
        
        # Send verification email
        email_service.send_verification_email(
            email=user.email,
            verification_token=verification_token,
            user_name=user.full_name
        )
        
        return safe_response
        
    except Exception as e:
        db.rollback()
        logger.error(f"Resend verification error: {str(e)}")
        return {
            "message": "If this email exists and is unverified, a new verification link has been sent.",
            "email": request.email
        }

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Generate password reset token and send email"""
    try:
        user = db.query(User).filter(User.email == request.email).first()
        
        # For security - don't reveal if email exists
        safe_response = {
            "message": "If this email exists in our system, a password reset link has been sent. Check your email.",
            "email": request.email
        }
        
        if not user:
            return safe_response
        
        # Generate reset token
        reset_token = token_urlsafe(32)
        user.password_reset_token = reset_token
        user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
        db.commit()
        
        # Send email with reset link
        reset_url = f"{settings.FRONTEND_URL}/auth/reset-password?token={reset_token}"
        email_service.send_password_reset_email(
            email=user.email,
            reset_token=reset_token,
            user_name=user.full_name
        )
        
        return safe_response
        
    except Exception as e:
        db.rollback()
        import logging
        logging.error(f"Forgot password error: {str(e)}")
        # Return same response for security
        return {
            "message": "If this email exists in our system, a password reset link has been sent. Check your email.",
            "email": request.email
        }

@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset password using token"""
    try:
        # Find user with valid token
        user = db.query(User).filter(
            User.password_reset_token == request.token,
            User.password_reset_expires > datetime.utcnow()
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired password reset link. Please request a new one."
            )
        
        # Update password
        user.hashed_password = get_password_hash(request.new_password)
        user.password_reset_token = None
        user.password_reset_expires = None
        user.updated_at = datetime.utcnow()
        db.commit()
        
        # Send confirmation email
        email_service.send_password_reset_email(
            email=user.email,
            reset_token="CONFIRMED",
            user_name=user.full_name
        )
        
        return {
            "message": "Password reset successfully. You can now login with your new password.",
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        import logging
        logging.error(f"Reset password error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset password. Please try again."
        )

@router.post("/google-login", response_model=TokenResponse)
def google_login(request: GoogleLoginRequest, db: Session = Depends(get_db)):
    """Login or signup with Google OAuth"""
    try:
        logger.info(f"Google login attempt with token: {request.id_token[:20]}...")
        
        # For development - allow TEST_TOKEN
        if settings.ENVIRONMENT == "development" and request.id_token == "TEST_TOKEN":
            logger.info("Using TEST_TOKEN for development")
            # Create test user or get existing
            test_email = "testgoogle@example.com"
            user = db.query(User).filter(User.email == test_email).first()
            logger.info(f"Found existing user: {user is not None}")
            
            if not user:
                logger.info("Creating new test user")
                user = User(
                    email=test_email,
                    username="testgoogle",
                    full_name="Test Google User",
                    google_id="test-google-123",
                    profile_picture="https://via.placeholder.com/150",
                    subscription_plan="free",
                    is_active=True
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                logger.info(f"Created user with ID: {user.id}")
        else:
            # Verify with Google using their library
            try:
                import google.auth.transport.requests
                import google.oauth2.id_token
                
                request_obj = google.auth.transport.requests.Request()
                id_info = google.oauth2.id_token.verify_oauth2_token(
                    request.id_token,
                    request_obj,
                    settings.GOOGLE_CLIENT_ID
                )
            except ImportError:
                logger.error("google-auth library not installed")
                raise HTTPException(
                    status_code=status.HTTP_501_NOT_IMPLEMENTED,
                    detail="Google OAuth not available. Contact support."
                )
            except ValueError as e:
                logger.error(f"Invalid Google token: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Google token"
                )
            
            email = id_info.get('email')
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Google account must have an email"
                )
            
            full_name = id_info.get('name', email.split('@')[0])
            google_id = id_info.get('sub')
            picture = id_info.get('picture')
            
            # Find or create user
            user = db.query(User).filter(User.email == email).first()
            
            if not user:
                # Generate unique username
                username = email.split('@')[0]
                counter = 1
                base_username = username
                while db.query(User).filter(User.username == username).first():
                    username = f"{base_username}_g{counter}"
                    counter += 1
                
                # Create new user from Google
                user = User(
                    email=email,
                    username=username,
                    full_name=full_name,
                    google_id=google_id,
                    profile_picture=picture,
                    subscription_plan="free",
                    is_active=True
                )
                db.add(user)
            else:
                # Update existing user with Google info
                if not user.google_id:
                    user.google_id = google_id
                if picture:
                    user.profile_picture = picture
            
            db.commit()
            db.refresh(user)
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user.id,
            "user_name": user.username
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Google login error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google login failed. Please try again."
        )

@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """Logout user (invalidate token on frontend)"""
    return {"message": "Logged out successfully. Please clear your token."}
