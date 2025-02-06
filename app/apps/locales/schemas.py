from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum
from decimal import Decimal
from app.apps.locales.models import (
    MetodoSeparacionEnum, MonedaEnum, EstadoLocalEnum, TipoLocalEnum, LineaBaseEnum, EstadoLocalEnum, TipoLocalEnum
)

# ---------------- ENUMS ----------------
class LineaBaseEnum(str, Enum):
    primera_linea = "Primera Línea"
    segunda_linea = "Segunda Línea"
    tercera_linea = "Tercera Línea"

# Enum para Estado del Local
class EstadoLocalEnum(str, Enum):
    disponible = "Disponible"
    reservado = "Reservado"
    vendido = "Vendido"

class TipoLocalEnum(str, Enum):
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

class MetodoSeparacionEnum(str, Enum):
    efectivo = "Efectivo"
    deposito = "Depósito"
    banco = "Banco"

class MonedaEnum(str, Enum):
    PEN = "PEN"
    USD = "USD"


# 🔥 Subesquemas para Datos Relacionados
class CategoriaBase(BaseModel):
    nombre: str

class MetrajeBase(BaseModel):
    area: str

class ZonaBase(BaseModel):
    codigo: str

class LocalBase(BaseModel):
    
    
    estado: str

class MetrajeBase(BaseModel):
    area: str
    image: Optional[str] = None
    perimetro: str

# ---------------------- CATEGORIA ----------------------
class CategoriaBase(BaseModel):
    nombre: str

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaResponse(CategoriaBase):
    id: int
    class Config:
        from_attributes = True

# ---------------------- ZONA ----------------------
class ZonaBase(BaseModel):
    categoria_id: int  # ✅ Se enviará solo el ID
    codigo: str
    linea_base: LineaBaseEnum

class ZonaCreate(ZonaBase):
    pass

class ZonaResponse(BaseModel):
    id: int
    categoria: CategoriaBase  # ✅ Devuelve el nombre de la categoría
    codigo: str
    linea_base: LineaBaseEnum

    class Config:
        from_attributes = True

# 🔥 Esquema para ACTUALIZAR una Zona (PUT)
class ZonaUpdate(BaseModel):
    categoria_id: Optional[int] = None
    codigo: Optional[str] = None
    linea_base: Optional[LineaBaseEnum] = None

# ---------------------- METRAJE ----------------------
class MetrajeBase(BaseModel):
    area: str
    perimetro: str
    image: Optional[str] = None

class MetrajeCreate(MetrajeBase):
    pass

class MetrajeResponse(MetrajeBase):
    id: int
    class Config:
        from_attributes = True

# ---------------------- CLIENTE ----------------------

# 📌 Subnivel del local
class SubnivelSchema(BaseModel):
    categoria_id: int
    codigo: str
    linea_base: LineaBaseEnum

# 📌 Metraje del local
class MetrajeSchema(BaseModel):
    area: str
    perimetro: str
    image: Optional[str]

# 📌 Información del Local
class LocalSchema(BaseModel):
    zona_codigo: str
    estado: EstadoLocalEnum
    precio_base: float
    tipo: TipoLocalEnum
    subnivel_de: SubnivelSchema
    metraje: MetrajeSchema

# 📌 Esquema para Crear Cliente (POST)
class ClienteCreate(BaseModel):
    nombres_cliente: str
    apellidos_cliente: str
    dni_cliente: int
    ruc_cliente: Optional[int] = None
    ocupacion_cliente: Optional[str] = None
    phone_cliente: int
    direccion_cliente: str
    mail_cliente: EmailStr
    nombres_conyuge: str
    dni_conyuge: int
    metodo_separacion: MetodoSeparacionEnum
    moneda: MonedaEnum
    numero_operacion: Optional[str] = None
    fecha_plazo: Optional[datetime] = None
    monto_arras: float
    local_id: Optional[int] = None

# 📌 Esquema para Respuesta de Cliente (GET)
class ClienteResponse(ClienteCreate):
    id: int
    fecha_registro: datetime
    local: Optional[LocalSchema]

    class Config:
        from_attributes = True  # ✅ Convierte SQLAlchemy a Pydantic

# 🔥 SCHEMA para ACTUALIZAR Cliente (PUT)
class ClienteUpdate(BaseModel):
    nombres_cliente: Optional[str] = None
    apellidos_cliente: Optional[str] = None
    dni_cliente: Optional[str] = None
    ruc_cliente: Optional[str] = None
    ocupacion_cliente: Optional[str] = None
    phone_cliente: Optional[str] = None
    direccion_cliente: Optional[str] = None
    mail_cliente: Optional[str] = None
    nombres_conyuge: Optional[str] = None
    dni_conyuge: Optional[str] = None
    metodo_separacion: Optional[MetodoSeparacionEnum] = None
    moneda: Optional[MonedaEnum] = None
    numero_operacion: Optional[str] = None
    fecha_plazo: Optional[str] = None
    monto_arras: Optional[float] = None

    categoria_id: Optional[int] = None
    metraje_id: Optional[int] = None
    zona_id: Optional[int] = None
    local_id: Optional[int] = None

# ---------------------- LOCAL ----------------------
class LocalResponse(BaseModel):
    id: int
    estado: EstadoLocalEnum
    precio_base: Decimal
    tipo: TipoLocalEnum
    subnivel_de: Optional[str] = None
    subnivel_de_id: Optional[int] = None

    # Si quieres mostrar el código de la Zona
    zona_codigo: Optional[str] = None

    # Campos de metraje
    area: Optional[str] = None
    perimetro: Optional[str] = None
    image: Optional[str] = None

    class Config:
        orm_mode = True

# 📌 Esquema para creación (POST)
class LocalCreate(BaseModel):
    estado: EstadoLocalEnum
    precio_base: Decimal
    tipo: TipoLocalEnum
    subnivel_de: Optional[str] = None         # código
    subnivel_de_id: Optional[int] = None      # referencia al padre

    zona_id: Optional[int] = None
    metraje_id: Optional[int] = None

# 📌 Esquema para actualización (PUT)
class LocalUpdate(BaseModel):
    estado: Optional[EstadoLocalEnum] = None
    precio_base: Optional[Decimal] = None
    tipo: Optional[TipoLocalEnum] = None
    subnivel_de: Optional[str] = None
    subnivel_de_id: Optional[int] = None

    zona_id: Optional[int] = None
    metraje_id: Optional[int] = None



# ---------------------- LOCAL-grupos ----------------------


class LocalSchema(BaseModel):
    zona_codigo: str
    precio: str
    estado: str
    area: Optional[str] = None
    perimetro: Optional[str] = None
    image: Optional[str] = None
    linea_base: str
    subniveles: Optional[List["LocalSchema"]] = None  # ✅ Subniveles recursivos

    class Config:
        from_attributes = True

# ✅ Modelo para los grupos de locales
class GrupoLocalesSchema(BaseModel):
    tipo: str
    locales: List[LocalSchema]

# ✅ Modelo de respuesta que contiene los grupos
class ResponseGrupoLocales(BaseModel):
    grupos: List[GrupoLocalesSchema]