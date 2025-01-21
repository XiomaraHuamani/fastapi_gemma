from sqlalchemy.orm import Session
from app.apps.users.models import User
from app.apps.users.security import hash_password

def create_user(db: Session, username: str, email: str, password: str, role: str):
    hashed_password = hash_password(password)
    new_user = User(username=username, email=email, password=hashed_password, role=role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
