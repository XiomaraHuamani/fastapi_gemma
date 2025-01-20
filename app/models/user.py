from sqlalchemy import Column, Integer, String
from app.db.connection import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)  # ✅ Corrección aquí
    password = Column(String(255), nullable=False)  # Se almacena en hash
    role = Column(String(50), nullable=False, default="cliente")  # Roles: marketing, asesor, staff, cliente
