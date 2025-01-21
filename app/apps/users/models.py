from sqlalchemy import Column, Integer, String, Enum
from app.db.connection import Base
import enum

class RoleEnum(str, enum.Enum):
    marketing = "marketing"
    asesor = "asesor"
    staff = "staff"
    cliente = "cliente"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False, default=RoleEnum.cliente)
 