from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserRegister(BaseModel):
    email: EmailStr
    username: Optional[str] = Field(None, min_length=3, max_length=50)  # Optional, will be auto-generated if not provided
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2)
    phone_number: Optional[str] = None
    college: Optional[str] = None
    graduation_year: Optional[int] = None
    course: Optional[str] = None  # e.g., "B.Tech Computer Science"
    years_of_experience: Optional[int] = Field(default=0, ge=0)  # 0 for fresher, 1-50 for experienced

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    user_name: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    phone_number: Optional[str] = None
    college: Optional[str] = None
    course: Optional[str] = None
    years_of_experience: Optional[int] = None
    profile_picture: Optional[str] = None
    subscription_plan: str
    is_email_verified: bool = False
    is_tess_admin: bool = False
    
    class Config:
        from_attributes = True

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

class GoogleLoginRequest(BaseModel):
    id_token: str

class EmailVerificationRequest(BaseModel):
    token: str = Field(..., description="Email verification token from email link")

class VerificationResponse(BaseModel):
    success: bool
    message: str
    user_id: Optional[int] = None

class ResendVerificationRequest(BaseModel):
    email: EmailStr = Field(..., description="Email address to resend verification token")
