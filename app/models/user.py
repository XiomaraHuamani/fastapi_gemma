from sqlalchemy import Column, Integer, String
from app.db.connection import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)  # Guardaremos la contraseña en formato hash
    role = Column(String, nullable=False, default="cliente")  # marketing, asesor, staff, cliente
