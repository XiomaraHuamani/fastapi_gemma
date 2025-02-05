from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DECIMAL, Enum, DateTime, func, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy.orm import relationship
from app.db.connection import Base
import enum

# Enum para Linea Base
class LineaBaseEnum(str, enum.Enum):
    primera_linea = "Primera Línea"
    segunda_linea = "Segunda Línea"
    tercera_linea = "Tercera Línea"

# Enum para Estado del Local
class EstadoLocalEnum(str, enum.Enum):
    disponible = "Disponible"
    reservado = "Reservado"
    vendido = "Vendido"

# Enum para Método de Separación
class MetodoSeparacionEnum(str, enum.Enum):
    efectivo = "Efectivo"
    deposito = "Depósito"
    banco = "Banco"

# Enum para Moneda
class MonedaEnum(str, enum.Enum):
    PEN = "PEN"
    USD = "USD"

# Enum para locales tipo
class TipoLocalEnum(str, enum.Enum):
    entrada_secundaria_grupo_1_izquierda = "Entrada secundaria grupo 1 izquierda"
    entrada_secundaria_grupo_1_derecha = "Entrada secundaria grupo 1 derecha"
    entrada_secundaria_grupo_2_izquierda = "Entrada secundaria grupo 2 izquierda"
    entrada_secundaria_grupo_2_derecha = "Entrada secundaria grupo 2 derecha"
    entrada_secundaria_grupo_3_izquierda = "Entrada secundaria grupo 3 izquierda"
    entrada_secundaria_grupo_3_derecha = "Entrada secundaria grupo 3 derecha"
    entrada_secundaria_grupo_4_izquierda = "Entrada secundaria grupo 4 izquierda"
    entrada_secundaria_grupo_4_derecha = "Entrada secundaria grupo 4 derecha"
    entrada_secundaria_grupo_5_izquierda = "Entrada secundaria grupo 5 izquierda"
    entrada_secundaria_grupo_5_derecha = "Entrada secundaria grupo 5 derecha"
    entrada_grupo_1_larga = "Entrada grupo 1 larga"
    entrada_grupo_2_larga = "Entrada grupo 2 larga"


class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False, index=True)

    zonas = relationship("Zona", back_populates="categoria", foreign_keys="Zona.categoria_id")  # ✅ Clave foránea corregida
    clientes = relationship("Cliente", back_populates="categoria")
    
class Zona(Base): 
    __tablename__ = "zonas"

    id = Column(Integer, primary_key=True, index=True)
    categoria_id = Column(Integer, ForeignKey("categorias.id", ondelete="CASCADE"), nullable=False)  

    codigo = Column(String(10), unique=True, nullable=False, index=True)
    linea_base = Column(Enum(LineaBaseEnum), default=LineaBaseEnum.primera_linea, nullable=False)

    categoria = relationship("Categoria", back_populates="zonas")
    locales = relationship("Local", back_populates="zona")
    clientes = relationship("Cliente", back_populates="zona")  

class Metraje(Base):
    __tablename__ = "metrajes"

    id = Column(Integer, primary_key=True, index=True)
    area = Column(String(50),unique=True, nullable=False, index=True)
    perimetro = Column(String(50), nullable=False)
    image = Column(String(255), nullable=True)

    locales = relationship("Local", back_populates="metraje")
    clientes = relationship("Cliente", back_populates="metraje") 


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nombres_cliente = Column(String(100), nullable=False)
    apellidos_cliente = Column(String(100), nullable=False)
    dni_cliente = Column(BigInteger,  nullable=False)  # ✅ Corrección
    ruc_cliente = Column(BigInteger,  nullable=True)  # ✅ Corrección
    f_nacimiento_cliente = Column(DateTime, nullable=False, default=datetime.utcnow)
    ocupacion_cliente = Column(String(50), nullable=True)
    phone_cliente = Column(BigInteger, nullable=False)  # ✅ Corrección
    direccion_cliente = Column(String(100), nullable=False)
    mail_cliente = Column(String(50), nullable=False)

    nombres_copropietario = Column(String(100), nullable=True)
    apellidos_copropietario = Column(String(100), nullable=True)
    dni_copropietario = Column(BigInteger,  nullable=True)  # ✅ Corrección
    ruc_copropietario = Column(BigInteger,  nullable=True)  # ✅ Corrección
    f_nacimiento_copropietario = Column(DateTime, nullable=True)
    ocupacion_copropietario = Column(String(50), nullable=True)
    phone_copropietario = Column(BigInteger, nullable=True)  # ✅ Corrección
    direccion_copropietario = Column(String(100), nullable=True)
    mail_copropietario = Column(String(50), nullable=True)
    parentesco_copropietario = Column(String(50), nullable=True)

    nombres_conyuge = Column(String(100), nullable=False)
    dni_conyuge = Column(BigInteger,  nullable=False)  # ✅ Corrección

    metodo_separacion = Column(Enum(MetodoSeparacionEnum), nullable=False)
    moneda = Column(Enum(MonedaEnum), nullable=False)
    numero_operacion = Column(String(50), nullable=True)
    fecha_plazo = Column(DateTime, nullable=True)
    fecha_registro = Column(DateTime, default=func.now())
    monto_arras = Column(DECIMAL(10, 2), nullable=False)

    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False)
    metraje_id = Column(Integer, ForeignKey("metrajes.id"), nullable=False)
    zona_id = Column(Integer, ForeignKey("zonas.id"), nullable=False)
    local_id = Column(Integer, ForeignKey("locales.id", ondelete="SET NULL"), nullable=True)

    categoria = relationship("Categoria", back_populates="clientes")
    metraje = relationship("Metraje", back_populates="clientes")
    zona = relationship("Zona", back_populates="clientes")
    local = relationship("Local", back_populates="clientes")


class Local(Base):
    __tablename__ = "locales"

    id = Column(Integer, primary_key=True, index=True)
    estado = Column(Enum(EstadoLocalEnum), default=EstadoLocalEnum.disponible)
    precio_base = Column(DECIMAL(10, 2), nullable=False, index=True)
    tipo = Column(Enum(TipoLocalEnum), nullable=False)

    subnivel_de = Column(String(20), unique=True, nullable=True)

    zona_id = Column(Integer, ForeignKey("zonas.id", ondelete="SET NULL"), nullable=True)
    metraje_id = Column(Integer, ForeignKey("metrajes.id", ondelete="SET NULL"), nullable=True)

    zona = relationship("Zona", back_populates="locales")
    metraje = relationship("Metraje", back_populates="locales")

    clientes = relationship("Cliente", back_populates="local")


