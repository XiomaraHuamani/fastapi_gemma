from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

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

class ClienteCreate(BaseModel):
    nombres_cliente: str
    apellidos_cliente: str
    dni_cliente: str
    ruc_cliente: Optional[str] = None
    ocupacion_cliente: Optional[str] = None
    phone_cliente: str
    direccion_cliente: str
    mail_cliente: str
    nombres_conyuge: str
    dni_conyuge: str
    metodo_separacion: MetodoSeparacionEnum
    moneda: MonedaEnum
    numero_operacion: Optional[str] = None
    fecha_plazo: str
    monto_arras: float
    categoria_id: int
    metraje_id: int
    zona_id: int
    local_id: int


class ClienteResponse(BaseModel):
    id: int
    nombres_cliente: str
    apellidos_cliente: str
    dni_cliente: str
    ruc_cliente: Optional[str] = None
    ocupacion_cliente: Optional[str] = None
    phone_cliente: str
    direccion_cliente: str
    mail_cliente: str
    nombres_conyuge: str
    dni_conyuge: str
    metodo_separacion: MetodoSeparacionEnum
    moneda: MonedaEnum
    numero_operacion: Optional[str] = None
    fecha_plazo: str
    monto_arras: float
    fecha_registro: datetime

    categoria: CategoriaBase
    metraje: MetrajeBase
    zona: ZonaBase
    local: LocalBase

    class Config:
        from_attributes = True

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
    estado: str
    precio_base: float
    tipo: str
    area: str
    zona: ZonaBase
    subnivel_de: Optional[str]
    perimetro: str
    image: Optional[str]
    zona_codigo: str

    class Config:
        from_attributes = True  # ✅ Permite convertir SQLAlchemy a Pydantic

# 📌 Esquema para creación (POST)
class LocalCreate(BaseModel):
    estado: str
    precio_base: float
    tipo: str
    subnivel_de: Optional[str]
    zona_id: Optional[int]
    metraje_id: Optional[int]

# 📌 Esquema para actualización (PUT)
class LocalUpdate(BaseModel):
    estado: Optional[EstadoLocalEnum] = None
    precio_base: Optional[float] = None
    tipo: Optional[TipoLocalEnum] = None
    subnivel_de: Optional[str] = None
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