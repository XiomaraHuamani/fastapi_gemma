from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

# 🔥 Enums
class LineaBaseEnum(str, Enum):
    primera_linea = "Primera Línea"
    segunda_linea = "Segunda Línea"
    tercera_linea = "Tercera Línea"

class EstadoLocalEnum(str, Enum):
    disponible = "Disponible"
    reservado = "Reservado"
    vendido = "Vendido"

class MetodoSeparacionEnum(str, Enum):
    efectivo = "Efectivo"
    deposito = "Depósito"
    banco = "Banco"

class MonedaEnum(str, Enum):
    PEN = "PEN"
    USD = "USD"

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

# ✅ Esquema de Categoría
class CategoriaBase(BaseModel):
    nombre: str

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaResponse(CategoriaBase):
    id: int

    class Config:
        from_attributes = True  # ✅ Corrección para Pydantic v2

# ✅ Esquema de Zona
class ZonaBase(BaseModel):
    categoria_id: int
    codigo: str
    linea_base: LineaBaseEnum
    tiene_subniveles: bool

class ZonaCreate(ZonaBase):
    pass

class ZonaResponse(ZonaBase):
    id: int

    class Config:
        from_attributes = True  # ✅ Corrección para Pydantic v2

# ✅ Esquema de Metraje
class MetrajeBase(BaseModel):
    area: str
    perimetro: str
    image: Optional[str] = None

class MetrajeCreate(MetrajeBase):
    pass

class MetrajeResponse(MetrajeBase):
    id: int

    class Config:
        from_attributes = True  # ✅ Corrección para Pydantic v2

# ✅ Esquema de Cliente
class ClienteBase(BaseModel):
    nombres_cliente: str
    apellidos_cliente: str
    dni_cliente: str
    ruc_cliente: Optional[str] = None
    f_nacimiento_cliente: datetime
    metodo_separacion: MetodoSeparacionEnum
    moneda: MonedaEnum
    numero_operacion: Optional[str] = None
    fecha_plazo: str
    monto_arras: float

class ClienteCreate(ClienteBase):
    pass

class ClienteResponse(ClienteBase):
    id: int

    class Config:
        from_attributes = True  # ✅ Corrección para Pydantic v2

# ✅ Esquema de Local
class LocalBase(BaseModel):
    zona_id: int
    metraje_id: int
    estado: EstadoLocalEnum
    precio_base: float
    tipo: TipoLocalEnum
    subnivel_de_id: Optional[int] = None
    cliente_id: Optional[int] = None

class LocalCreate(LocalBase):
    pass

class LocalResponse(LocalBase):
    id: int

    class Config:
        from_attributes = True  # ✅ Corrección para Pydantic v2
