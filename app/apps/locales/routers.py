from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.db.connection import get_db
from app.apps.locales.schemas import (
    CategoriaCreate, CategoriaResponse,
    ZonaCreate, ZonaResponse, ZonaUpdate,
    MetrajeCreate, MetrajeResponse,
    ClienteCreate, ClienteResponse, ClienteUpdate,
    LocalCreate, LocalResponse, LocalUpdate
)
from app.apps.locales.models import Categoria, Zona, Metraje, Cliente, Local

router = APIRouter()

# ---------------------- CATEGORIA ----------------------
@router.get("/categorias", response_model=List[CategoriaResponse])
def listar_categorias(db: Session = Depends(get_db)):
    return db.query(Categoria).all()

@router.post("/categorias", response_model=CategoriaResponse)
def crear_categoria(categoria: CategoriaCreate, db: Session = Depends(get_db)):
    nueva_categoria = Categoria(**categoria.dict())
    db.add(nueva_categoria)
    db.commit()
    db.refresh(nueva_categoria)
    return nueva_categoria

@router.delete("/categorias/{categoria_id}")
def eliminar_categoria(categoria_id: int, db: Session = Depends(get_db)):
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    db.delete(categoria)
    db.commit()
    return {"message": "Categoría eliminada"}

# ---------------------- ZONA ----------------------
@router.get("/zonas", response_model=List[ZonaResponse])
def listar_zonas(db: Session = Depends(get_db)):
    zonas = db.query(Zona).join(Categoria).all()

    return [
        {
            "id": zona.id,
            "categoria": {"nombre": zona.categoria.nombre},  # 🔥 Devuelve el nombre en lugar del ID
            "codigo": zona.codigo,
            "linea_base": zona.linea_base.value  # 🔥 Convierte Enum a string
        }
        for zona in zonas
    ]


# ✅ 📌 POST - Crear una zona
@router.post("/zonas", response_model=ZonaResponse)
def crear_zona(zona: ZonaCreate, db: Session = Depends(get_db)):
    nueva_zona = Zona(**zona.dict())
    db.add(nueva_zona)
    db.commit()
    db.refresh(nueva_zona)

    return {
        "id": nueva_zona.id,
        "categoria": {"nombre": nueva_zona.categoria.nombre},  # 🔥 Devuelve el nombre en lugar del ID
        "codigo": nueva_zona.codigo,
        "linea_base": nueva_zona.linea_base.value
    }



# ✅ 📌 PUT - Actualizar una zona
@router.put("/zonas/{zona_id}", response_model=ZonaResponse)
def actualizar_zona(zona_id: int, zona_data: ZonaUpdate, db: Session = Depends(get_db)):
    zona = db.query(Zona).filter(Zona.id == zona_id).first()
    if not zona:
        raise HTTPException(status_code=404, detail="Zona no encontrada")

    for key, value in zona_data.dict(exclude_unset=True).items():
        setattr(zona, key, value)

    db.commit()
    db.refresh(zona)
    return zona

# ✅ 📌 DELETE - Eliminar una zona
@router.delete("/zonas/{zona_id}")
def eliminar_zona(zona_id: int, db: Session = Depends(get_db)):
    zona = db.query(Zona).filter(Zona.id == zona_id).first()
    if not zona:
        raise HTTPException(status_code=404, detail="Zona no encontrada")
    db.delete(zona)
    db.commit()
    return {"message": "Zona eliminada"}

# ---------------------- METRAJE ----------------------
@router.get("/metrajes", response_model=List[MetrajeResponse])
def listar_metrajes(db: Session = Depends(get_db)):
    return db.query(Metraje).all()

@router.post("/metrajes", response_model=MetrajeResponse)
def crear_metraje(metraje: MetrajeCreate, db: Session = Depends(get_db)):
    nuevo_metraje = Metraje(**metraje.dict())
    db.add(nuevo_metraje)
    db.commit()
    db.refresh(nuevo_metraje)
    return nuevo_metraje

@router.delete("/metrajes/{metraje_id}")
def eliminar_metraje(metraje_id: int, db: Session = Depends(get_db)):
    metraje = db.query(Metraje).filter(Metraje.id == metraje_id).first()
    if not metraje:
        raise HTTPException(status_code=404, detail="Metraje no encontrado")
    db.delete(metraje)
    db.commit()
    return {"message": "Metraje eliminado"}

# ---------------------- CLIENTE ----------------------
# ✅ 📌 GET - Listar todos los clientes con datos relacionados
@router.get("/clientes", response_model=List[ClienteResponse])
def listar_clientes(db: Session = Depends(get_db)):
    clientes = (
        db.query(Cliente)
        .join(Categoria, Cliente.categoria_id == Categoria.id)
        .join(Metraje, Cliente.metraje_id == Metraje.id)
        .join(Zona, Cliente.zona_id == Zona.id)
        .join(Local, Cliente.local_id == Local.id)
        .all()
    )

    return [
        {
            "id": cliente.id,
            "nombres_cliente": cliente.nombres_cliente,
            "apellidos_cliente": cliente.apellidos_cliente,
            "dni_cliente": cliente.dni_cliente,
            "ruc_cliente": cliente.ruc_cliente,
            "ocupacion_cliente": cliente.ocupacion_cliente,
            "phone_cliente": cliente.phone_cliente,
            "direccion_cliente": cliente.direccion_cliente,
            "mail_cliente": cliente.mail_cliente,
            "nombres_conyuge": cliente.nombres_conyuge,
            "dni_conyuge": cliente.dni_conyuge,
            "metodo_separacion": cliente.metodo_separacion.value,
            "moneda": cliente.moneda.value,
            "numero_operacion": cliente.numero_operacion,
            "fecha_plazo": cliente.fecha_plazo,
            "monto_arras": cliente.monto_arras,
            "fecha_registro": cliente.fecha_registro,

            "categoria": {"nombre": cliente.categoria.nombre} if cliente.categoria else None,
            "metraje": {"area": cliente.metraje.area} if cliente.metraje else None,
            "zona": {"codigo": cliente.zona.codigo} if cliente.zona else None,
            "local": {"estado": cliente.local.estado.value} if cliente.local else None,
        }
        for cliente in clientes
    ]

# ✅ 📌 POST - Crear un cliente
@router.post("/clientes", response_model=ClienteResponse)
def crear_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    nuevo_cliente = Cliente(**cliente.dict())
    db.add(nuevo_cliente)
    db.commit()
    db.refresh(nuevo_cliente)
    return nuevo_cliente

# ✅ 📌 PUT - Actualizar un cliente
@router.put("/clientes/{cliente_id}", response_model=ClienteResponse)
def actualizar_cliente(cliente_id: int, cliente_data: ClienteUpdate, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    for key, value in cliente_data.dict(exclude_unset=True).items():
        setattr(cliente, key, value)

    db.commit()
    db.refresh(cliente)
    return cliente

# ✅ 📌 DELETE - Eliminar un cliente
@router.delete("/clientes/{cliente_id}")
def eliminar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    db.delete(cliente)
    db.commit()
    return {"message": "Cliente eliminado"}

# ---------------------- LOCAL ----------------------
# ✅ 📌 GET - Listar todos los locales con datos relacionados
@router.get("/locales", response_model=List[LocalResponse])
def listar_locales(db: Session = Depends(get_db)):
    locales = db.query(Local).join(Metraje).join(Zona).all()

    return [
        {
            "id": local.id,
            "zona": {"codigo": local.zona.codigo},  # 🔥 Devuelve el código de la zona
            "estado": local.estado.value,  # 🔥 Convertimos Enum a string
            "precio_base": f"{local.precio_base:.2f}",  # 🔥 Formato decimal a string con 2 decimales
            "metraje": {
                "area": local.metraje.area,
                "image": local.metraje.image if local.metraje.image else None,  # ✅ Si no hay imagen, devuelve None
                "perimetro": local.metraje.perimetro,
            },
            "subnivel_de": local.subnivel_de  # 🔥 Se devuelve el código del subnivel si existe
        }
        for local in locales
    ]

# ✅ 📌 POST - Crear un local
@router.post("/locales", response_model=LocalResponse)
def crear_local(local: LocalCreate, db: Session = Depends(get_db)):
    nuevo_local = Local(**local.dict())
    db.add(nuevo_local)
    db.commit()
    db.refresh(nuevo_local)
    return nuevo_local

# ✅ 📌 PUT - Actualizar un local
@router.put("/locales/{local_id}", response_model=LocalResponse)
def actualizar_local(local_id: int, local_data: LocalUpdate, db: Session = Depends(get_db)):
    local = db.query(Local).filter(Local.id == local_id).first()
    if not local:
        raise HTTPException(status_code=404, detail="Local no encontrado")

    for key, value in local_data.dict(exclude_unset=True).items():
        setattr(local, key, value)

    db.commit()
    db.refresh(local)
    return local

# ✅ 📌 DELETE - Eliminar un local
@router.delete("/locales/{local_id}")
def eliminar_local(local_id: int, db: Session = Depends(get_db)):
    local = db.query(Local).filter(Local.id == local_id).first()
    if not local:
        raise HTTPException(status_code=404, detail="Local no encontrado")
    db.delete(local)
    db.commit()
    return {"message": "Local eliminado"}
