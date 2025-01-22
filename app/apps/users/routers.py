from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.db.connection import get_db
from app.apps.users.models import User, RoleEnum
from app.apps.users.schemas import RegisterRequest, LoginRequest, UserResponse, TokenResponse, UpdateUserRequest
from app.apps.users.security import create_access_token, hash_password, verify_password
from app.core.config import settings
from typing import List


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")


# ✅ CREAR USUARIO (Registro)
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    # Verificar si el usuario ya existe
    existing_user = db.query(User).filter(User.username == data.username).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario ya existe")

    # Hashear la contraseña antes de guardarla
    hashed_password = hash_password(data.password)

    # Crear nuevo usuario
    new_user = User(
        username=data.username, 
        email=data.email, 
        password=hashed_password,
        role=RoleEnum(data.role).value  # ✅ Convertimos a string antes de guardar
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ✅ LOGIN (Genera Token JWT)
@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value},
        expires_delta=access_token_expires
    )

    return {
        "user": {
            "username": user.username
        },
        "tokens": {
            "access": access_token
        },
        "role": user.role.value,
        "message": "Inicio de sesión exitoso"
    }


# ✅ Obtener todos los usuarios
@router.get("/", response_model=List[UserResponse])  # ✅ List ahora está definido
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

# ✅ OBTENER USUARIO POR ID
@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return user


# ✅ ACTUALIZAR USUARIO
@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, data: UpdateUserRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    user.username = data.username
    user.email = data.email
    if data.password:
        user.password = hash_password(data.password)
    user.role = RoleEnum(data.role).value

    db.commit()
    db.refresh(user)
    return user


# ✅ ELIMINAR USUARIO
@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    
    db.delete(user)
    db.commit()
    return {"message": "Usuario eliminado correctamente"}
