from sqlalchemy import Column, Integer, String, Enum
from enum import Enum as PyEnum  # ✅ Importar `Enum` de `enum`
from app.db.connection import Base  # ✅ Ahora `Base` viene desde `connection.py`

# 🔥 Definir el Enum correctamente
class RoleEnum(PyEnum):
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
    role = Column(Enum(RoleEnum, native_enum=False), nullable=False, default=RoleEnum.cliente.value)