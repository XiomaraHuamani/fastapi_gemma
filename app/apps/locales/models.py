from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DECIMAL, Enum, DateTime, func
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

    zonas = relationship("Zona", back_populates="categoria", lazy="joined")

class Zona(Base):
    __tablename__ = "zonas"

    id = Column(Integer, primary_key=True, index=True)
    categoria_nombre = Column(
        String(100), 
        ForeignKey("categorias.nombre", name="fk_zona_categoria"),  # 🔥 Se asigna nombre explícito a la FK
        nullable=False
    )
    codigo = Column(String(10), unique=True, nullable=False, index=True)
    linea_base = Column(Enum(LineaBaseEnum), default=LineaBaseEnum.primera_linea)
    tiene_subniveles = Column(Boolean, default=False, index=True)

    categoria = relationship("Categoria", back_populates="zonas", lazy="joined", foreign_keys=[categoria_nombre])
    locales = relationship("Local", back_populates="zona", lazy="joined")


class Metraje(Base):
    __tablename__ = "metrajes"

    id = Column(Integer, primary_key=True, index=True)
    area = Column(String(50),unique=True, nullable=False, index=True)
    perimetro = Column(String(50), nullable=False)
    image = Column(String(255), nullable=True)

    locales = relationship("Local", back_populates="metraje", lazy="joined")
class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nombres_cliente = Column(String(100), nullable=False)
    apellidos_cliente = Column(String(100), nullable=False)
    dni_cliente = Column(String(20), unique=True, nullable=False)
    ruc_cliente = Column(String(20), unique=True, nullable=True)
    f_nacimiento_cliente = Column(DateTime, nullable=False, default=datetime.utcnow)
    ocupacion_cliente = Column(String(100), nullable=True)
    phone_cliente = Column(String(20), nullable=False)
    direccion_cliente = Column(String(255), nullable=False)
    mail_cliente = Column(String(100), nullable=False)

    nombres_copropietario = Column(String(100), nullable=False)
    apellidos_copropietario = Column(String(100), nullable=False)
    dni_copropietario = Column(String(20), unique=True, nullable=True)
    ruc_copropietario = Column(String(20), unique=True, nullable=True)
    f_nacimiento_copropietario = Column(DateTime, nullable=False, default=datetime.utcnow)
    ocupacion_copropietario = Column(String(100), nullable=True)
    phone_copropietario = Column(String(20), nullable=True)
    direccion_copropietario = Column(String(255), nullable=True)
    mail_copropietario = Column(String(100), nullable=True)
    parentesco_copropietario = Column(String(100), nullable=True)

    nombres_conyuge = Column(String(100), nullable=False)
    dni_conyuge = Column(String(20), unique=True, nullable=False)

    metodo_separacion = Column(Enum(MetodoSeparacionEnum), nullable=False)
    moneda = Column(Enum(MonedaEnum), nullable=False)
    numero_operacion = Column(String(50), nullable=True)
    fecha_plazo = Column(String(50), nullable=False)
    fecha_registro = Column(DateTime, default=func.now())
    monto_arras = Column(DECIMAL(10, 2), nullable=False)

    locales = relationship("Local", back_populates="cliente", lazy="joined")

class Local(Base):
    __tablename__ = "locales"

    id = Column(Integer, primary_key=True, index=True)
    zona_id = Column(Integer, ForeignKey("zonas.id"), nullable=False)
    metraje_id = Column(Integer, ForeignKey("metrajes.id"), nullable=False)
    estado = Column(Enum(EstadoLocalEnum), default=EstadoLocalEnum.disponible)
    precio_base = Column(DECIMAL(10, 2), nullable=False, index=True)
    tipo = Column(Enum(TipoLocalEnum), nullable=False)

    subnivel_de_id = Column(Integer, ForeignKey("locales.id"), nullable=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True)

    zona = relationship("Zona", back_populates="locales", lazy="joined")
    metraje = relationship("Metraje", back_populates="locales", lazy="joined")
    cliente = relationship("Cliente", back_populates="locales", lazy="joined")