from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from app.apps.users.models import RoleEnum

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: str = Field(default=RoleEnum.cliente.value)

class LoginRequest(BaseModel):
    username: str
    password: str

class UpdateUserRequest(BaseModel):
    username: str
    email: EmailStr
    password: Optional[str] = None  # ✅ Compatible con Python 3.8
    role: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str

class TokenResponse(BaseModel):
    user: dict
    tokens: dict
    role: str
    message: str
