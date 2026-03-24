from pydantic import BaseModel, EmailStr

class UserRegister(BaseModel):
    email: str
    username: str
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    subscription_plan: str
    
    class Config:
        from_attributes = True
