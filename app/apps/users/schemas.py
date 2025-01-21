from pydantic import BaseModel, EmailStr, Field
from app.models.user import RoleEnum

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str
    role: RoleEnum = RoleEnum.cliente

class LoginRequest(BaseModel):
    username: str
    password: str

class UpdateUserRequest(BaseModel):
    username: str
    email: EmailStr
    password: str = None  # Opcional, solo cambiar si se envía
    role: RoleEnum

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: RoleEnum

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
