from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from sqlalchemy.orm import Session, joinedload, subqueryload
from fastapi.encoders import jsonable_encoder
from typing import List
from app.db.connection import get_db
from app.apps.locales.schemas import (
    CategoriaCreate, CategoriaResponse,
    ZonaCreate, ZonaResponse, ZonaUpdate,
    MetrajeCreate, MetrajeResponse,
    ClienteCreate, ClienteResponse, ClienteUpdate,
    LocalCreate, LocalResponse, LocalUpdate,
    ResponseGrupoLocales, GrupoLocalesSchema, LocalSchema
)
from app.apps.locales.models import Categoria, Zona, Metraje, Cliente, Local
from app.apps.locales.utils import serialize_local, serialize_local_with_subniveles

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
            "categoria": {"nombre": zona.categoria.nombre},  
            "codigo": zona.codigo,
            "linea_base": zona.linea_base.value  
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

@router.get("/clientes/", response_model=list)
def listar_clientes(db: Session = Depends(get_db)):
    clientes = db.query(Cliente).all()

    response_data = []
    for cliente in clientes:
        cliente_data = {
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
        }

        if cliente.local:
            cliente_data["local"] = {
                "zona_codigo": cliente.local.zona.codigo if cliente.local.zona else None,
                "estado": cliente.local.estado.value,
                "precio_base": cliente.local.precio_base,
                "tipo": cliente.local.tipo.value,
                "metraje": {
                    "area": cliente.local.metraje.area if cliente.local.metraje else None,
                    "perimetro": cliente.local.metraje.perimetro if cliente.local.metraje else None,
                    "image": cliente.local.metraje.image if cliente.local.metraje else None
                } if cliente.local.metraje else None
            }

            if cliente.local.subnivel_de:
                cliente_data["local"]["subnivel_de"] = {
                    "categoria_id": cliente.local.zona.categoria_id if cliente.local.zona else None,
                    "codigo": cliente.local.zona.codigo if cliente.local.zona else None,
                    "linea_base": cliente.local.zona.linea_base.value if cliente.local.zona else None
                }

        response_data.append(cliente_data)

    return response_data


@router.get("/clientes/{cliente_id}", response_model=dict)
def obtener_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    cliente_data = {
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
    }

    if cliente.local:
        cliente_data["local"] = {
            "zona_codigo": cliente.local.zona.codigo if cliente.local.zona else None,
            "estado": cliente.local.estado.value,
            "precio_base": cliente.local.precio_base,
            "tipo": cliente.local.tipo.value,
            "metraje": {
                "area": cliente.local.metraje.area if cliente.local.metraje else None,
                "perimetro": cliente.local.metraje.perimetro if cliente.local.metraje else None,
                "image": cliente.local.metraje.image if cliente.local.metraje else None
            } if cliente.local.metraje else None
        }

        if cliente.local.subnivel_de:
            cliente_data["local"]["subnivel_de"] = {
                "categoria_id": cliente.local.zona.categoria_id if cliente.local.zona else None,
                "codigo": cliente.local.zona.codigo if cliente.local.zona else None,
                "linea_base": cliente.local.zona.linea_base.value if cliente.local.zona else None
            }

    return cliente_data


@router.post("/clientes/", response_model=dict)
def crear_cliente(cliente_data: ClienteCreate, db: Session = Depends(get_db)):
    local = db.query(Local).filter(Local.id == cliente_data.local_id).first()
    if not local:
        raise HTTPException(status_code=404, detail="Local no encontrado")

    nuevo_cliente = Cliente(
        **cliente_data.dict(exclude={"local_id"}),
        categoria_id=local.zona.categoria_id if local.zona else None,
        metraje_id=local.metraje_id,
        zona_id=local.zona_id,
        local_id=cliente_data.local_id,
        fecha_registro=datetime.utcnow()
    )

    db.add(nuevo_cliente)
    db.commit()
    db.refresh(nuevo_cliente)

    return obtener_cliente(nuevo_cliente.id, db)


@router.put("/clientes/{cliente_id}", response_model=dict)
def actualizar_cliente(cliente_id: int, cliente_data: ClienteUpdate, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    update_data = cliente_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(cliente, key, value)

    db.commit()
    db.refresh(cliente)

    return obtener_cliente(cliente.id, db)


# ✅ 📌 DELETE - Eliminar un cliente
@router.delete("/clientes/{cliente_id}", response_model=dict)
def eliminar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    db.delete(cliente)
    db.commit()

    return {"message": "Cliente eliminado correctamente"}



# ---------------------- LOCAL ----------------------

# ✅ 📌 GET - Listar locales
@router.get("/locales/", response_model=list)
def get_locales(db: Session = Depends(get_db)):
    locales = db.query(Local).all()

    response_data = []
    for local in locales:
        local_data = {
            "zona_codigo": local.zona.codigo if local.zona else None,
            "estado": local.estado.value,
            "precio_base": local.precio_base,
            "tipo": local.tipo.value,
            "metraje": {
                "area": local.metraje.area if local.metraje else None,
                "perimetro": local.metraje.perimetro if local.metraje else None,
                "image": local.metraje.image if local.metraje else None
            } if local.metraje else None
        }

        # ✅ Solo incluir `subnivel_de` si tiene datos
        if local.subnivel_de:
            local_data["subnivel_de"] = {
                "categoria_id": local.zona.categoria_id if local.zona else None,
                "codigo": local.zona.codigo if local.zona else None,
                "linea_base": local.zona.linea_base.value if local.zona else None
            }

        response_data.append(local_data)

    return response_data


# ✅ 📌 GET - Obtener un local por ID
@router.get("/locales/{local_id}", response_model=dict)
def get_local(local_id: int, db: Session = Depends(get_db)):
    local = db.query(Local).filter(Local.id == local_id).first()
    if not local:
        raise HTTPException(status_code=404, detail="Local no encontrado")

    local_data = {
        "zona_codigo": local.zona.codigo if local.zona else None,
        "estado": local.estado.value,
        "precio_base": local.precio_base,
        "tipo": local.tipo.value,
        "metraje": {
            "area": local.metraje.area if local.metraje else None,
            "perimetro": local.metraje.perimetro if local.metraje else None,
            "image": local.metraje.image if local.metraje else None
        } if local.metraje else None
    }

    # ✅ Solo incluir `subnivel_de` si tiene datos
    if local.subnivel_de:
        local_data["subnivel_de"] = {
            "categoria_id": local.zona.categoria_id if local.zona else None,
            "codigo": local.zona.codigo if local.zona else None,
            "linea_base": local.zona.linea_base.value if local.zona else None
        }

    return local_data


# ✅ 📌 POST - Crear un local
@router.post("/locales/", response_model=dict)
def create_local(local: LocalCreate, db: Session = Depends(get_db)):
    zona = db.query(Zona).filter(Zona.id == local.zona_id).first() if local.zona_id else None
    if local.zona_id and not zona:
        raise HTTPException(status_code=404, detail="Zona no encontrada")

    metraje = db.query(Metraje).filter(Metraje.id == local.metraje_id).first() if local.metraje_id else None
    if local.metraje_id and not metraje:
        raise HTTPException(status_code=404, detail="Metraje no encontrado")

    new_local = Local(
        estado=local.estado,
        precio_base=local.precio_base,
        tipo=local.tipo,
        subnivel_de=local.subnivel_de if local.subnivel_de else None,
        zona_id=local.zona_id,
        metraje_id=local.metraje_id
    )

    db.add(new_local)
    db.commit()
    db.refresh(new_local)

    response_data = {
        "zona_codigo": new_local.zona.codigo if new_local.zona else None,
        "estado": new_local.estado.value,
        "precio_base": new_local.precio_base,
        "tipo": new_local.tipo.value,
        "metraje": {
            "area": new_local.metraje.area if new_local.metraje else None,
            "perimetro": new_local.metraje.perimetro if new_local.metraje else None,
            "image": new_local.metraje.image if new_local.metraje else None
        } if new_local.metraje else None
    }

    # ✅ Solo incluir `subnivel_de` si tiene datos
    if new_local.subnivel_de:
        response_data["subnivel_de"] = {
            "categoria_id": new_local.zona.categoria_id if new_local.zona else None,
            "codigo": new_local.zona.codigo if new_local.zona else None,
            "linea_base": new_local.zona.linea_base.value if new_local.zona else None
        }

    return response_data


# ✅ 📌 PUT - Actualizar un local
@router.put("/locales/{local_id}", response_model=dict)
def actualizar_local(local_id: int, local_data: LocalCreate, db: Session = Depends(get_db)):
    local = db.query(Local).filter(Local.id == local_id).first()
    if not local:
        raise HTTPException(status_code=404, detail="Local no encontrado")

    update_data = jsonable_encoder(local_data)
    for key, value in update_data.items():
        setattr(local, key, value)

    db.commit()
    db.refresh(local)

    response_data = {
        "zona_codigo": local.zona.codigo if local.zona else None,
        "estado": local.estado.value,
        "precio_base": local.precio_base,
        "tipo": local.tipo.value,
        "metraje": {
            "area": local.metraje.area if local.metraje else None,
            "perimetro": local.metraje.perimetro if local.metraje else None,
            "image": local.metraje.image if local.metraje else None
        } if local.metraje else None
    }

    # ✅ Solo incluir `subnivel_de` si tiene datos
    if local.subnivel_de:
        response_data["subnivel_de"] = {
            "categoria_id": local.zona.categoria_id if local.zona else None,
            "codigo": local.zona.codigo if local.zona else None,
            "linea_base": local.zona.linea_base.value if local.zona else None
        }

    return response_data


# ✅ 📌 DELETE - Eliminar un local
@router.delete("/locales/{local_id}", response_model=dict)
def eliminar_local(local_id: int, db: Session = Depends(get_db)):
    local = db.query(Local).filter(Local.id == local_id).first()
    if not local:
        raise HTTPException(status_code=404, detail="Local no encontrado")

    db.delete(local)
    db.commit()

    return {"message": "Local eliminado correctamente"}

@router.get("/grupos", response_model=ResponseGrupoLocales)
def get_grupos(db: Session = Depends(get_db)):
    # Definición de grupos (cada grupo tiene un tipo y la lista de códigos de zona que lo integran)
    grupos_definidos = [
        {"tipo": "Entrada segundaria grupo 1 izquierda", "zona_codigos": ["PT 1", "PT 2", "PT 3", "PT 4", "PT 9", "PT 10", "PT 12", "PT 14"]},
        {"tipo": "Entrada segundaria grupo 1 derecha", "zona_codigos": ["PT 5", "PT 6", "PT 7", "PT 8", "PT 15", "PT 16", "PT 18", "PT 20"]},
        {"tipo": "Entrada segundaria grupo 2 izquierda", "zona_codigos": ["PT 21", "PT 22", "PT 23", "PT 24", "PT 25", "PT 26", "PT 33", "PT 34"]},
        {"tipo": "Entrada segundaria grupo 2 derecha", "zona_codigos": ["PT 27", "PT 28", "PT 29", "PT 30", "PT 31", "PT 32", "PT 37", "PT 38", "PT 93", "PT 40"]},
        {"tipo": "Entrada segundaria grupo 3 izquierda", "zona_codigos": ["PT 41", "PT 42", "PT 43", "PT 44", "PT 49", "PT 50", "PT 51", "PT 52", "PT 53", "PT 54"]},
        {"tipo": "Entrada segundaria grupo 3 derecha", "zona_codigos": ["PT 45", "PT 46", "PT 47", "PT 48", "PT 55", "PT 56", "PT 47", "PT 58", "PT 59", "PT 60"]},
        {"tipo": "Entrada segundaria grupo 4 izquierda", "zona_codigos": ["PT 61", "PT 62", "PT 63", "PT 64", "PT 65", "PT 66", "PT 73", "PT 74", "PT 75", "PT 76", "PT 77", "PT 78"]},
        {"tipo": "Entrada segundaria grupo 4 derecha", "zona_codigos": ["PT 67", "PT 68", "PT 69", "PT 70", "PT 71", "PT 72", "PT 79", "PT 80", "PT 81", "PT 82", "PT 83", "PT 84"]},
        {"tipo": "Entrada segundaria grupo 5 izquierda", "zona_codigos": ["PT 85", "PT 86", "PT 87", "PT 88", "PT 89", "PT 90", "PT 97", "PT 98", "PT 99", "PT 100"]},
        {"tipo": "Entrada segundaria grupo 5 derecha", "zona_codigos": ["PT 91", "PT 92", "PT 93", "PT 94", "PT 95", "PT 96", "PT 101", "PT 102", "PT 103", "PT 104"]},
        {"tipo": "Entrada grupo 1 larga", "zona_codigos": ["PT 105", "PT 106", "PT 107", "PT 108", "PT 109"]},
        {"tipo": "Entrada grupo 2 larga", "zona_codigos": ["PT 110", "PT 111", "PT 112", "PT 113", "PT 114", "PT 115", "PT 116", "PT 117"]}
    ]

    grupos_response = []

    # Para cada grupo definido se consulta en la BD:
    for grupo_def in grupos_definidos:
        tipo = grupo_def["tipo"]
        zona_codigos = grupo_def["zona_codigos"]

        # Se filtran solo los locales principales (donde subnivel_de_id es None)
        # cuya zona tenga un código en la lista.
        locales_qs = (
            db.query(Local)
            .join(Zona)
            .filter(Zona.codigo.in_(zona_codigos))
            .filter(Local.estado.in_(["Disponible", "Reservado", "Vendido"]))
            .filter(Local.subnivel_de_id == None)
            .options(
                joinedload(Local.zona),
                joinedload(Local.metraje),
                subqueryload(Local.subniveles).joinedload(Local.zona),
                subqueryload(Local.subniveles).joinedload(Local.metraje)
            )
            .all()
        )

        # Serializamos cada local (incluyendo sus subniveles, si existen)
        serialized_locales = [serialize_local_with_subniveles(local) for local in locales_qs]

        grupos_response.append({
            "tipo": tipo,  # este valor se obtiene de local.tipo.value en tus registros, pero aquí lo definimos según el grupo
            "locales": serialized_locales
        })

    return {"grupos": grupos_response}