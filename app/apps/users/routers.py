from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import timedelta
from app.db.connection import get_db
from app.apps.users.models import User, RoleEnum
from app.apps.users.schemas import RegisterRequest, LoginRequest, UserResponse
from app.apps.users.security import hash_password, verify_password, create_access_token, create_refresh_token

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# ✅ REGISTRO DE USUARIO
@router.post("/register", response_model=UserResponse)
def register_user(data: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")

    new_user = User(username=data.username, email=data.email, password=hash_password(data.password), role=data.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# ✅ LOGIN DE USUARIO
@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    access_token = create_access_token(data={"sub": user.username, "role": user.role}, expires_delta=timedelta(minutes=30))
    refresh_token = create_refresh_token(data={"sub": user.username, "role": user.role})

    return {
        "user": {
            "username": user.username
        },
        "tokens": {
            "refresh": refresh_token,
            "access": access_token
        },
        "role": user.role,
        "message": "Inicio de sesión exitoso"
    }
