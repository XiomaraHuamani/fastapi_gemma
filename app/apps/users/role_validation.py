from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.apps.users.security import verify_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

def role_required(required_role: str):
    def role_checker(token: str = Depends(oauth2_scheme)):
        user_data = verify_access_token(token)
        if not user_data or user_data.get("role") != required_role:
            raise HTTPException(status_code=403, detail="Acceso denegado")
        return user_data
    return role_checker
