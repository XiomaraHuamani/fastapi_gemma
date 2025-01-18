from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.core.security import verify_token
from app.schemas.auth import UserTokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def role_required(required_role: str):
    def role_checker(token: str = Depends(oauth2_scheme)):
        user_data = verify_token(token)
        if user_data.role != required_role:
            raise HTTPException(status_code=403, detail="Acceso denegado")
        return user_data
    return role_checker
