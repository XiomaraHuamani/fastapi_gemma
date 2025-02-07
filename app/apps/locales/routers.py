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
from app.apps.locales.utils import (
    procesar_local_recursivo,
    combinar_grupos_con_bd
)

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



@router.get("/grupos", response_model=dict)
def get_grupos(db: Session = Depends(get_db)):

    # Aquí copias tal cual tu estructura estática
    grupos_estaticos = [
        {
            "tipo": "entrada segundaria grupo 1 izquierda",
            "locales": [
                {
                    "zona_codigo": "PT 1",
                    "precio": "$51,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "primera_linea"
                },
                {
                    "zona_codigo": "PT 2",
                    "precio": "$51,990",
                    "estado": "Reservado",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "primera_linea"
                },
                {
                    "zona_codigo": "PT 3",
                    "precio": "$51,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "segunda_linea"
                },
                {
                    "zona_codigo": "PT 4",
                    "precio": "$51,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "segunda_linea"
                },
                {
                    "zona_codigo": "PT 9",
                    "precio": "$51,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "primera_linea"
                },
                {
                    "zona_codigo": "PT 10",
                    "subniveles": [
                        {
                            "zona_codigo": "PT 10",
                            "precio": "$29,990",
                            "estado": "Disponible",
                            "area": "25 m²",
                            "perimetro": "5x5",
                            "image": "../assets/tipos_locales/mediano.png",
                            "linea_base": "primera_linea"
                        },
                        {
                            "zona_codigo": "PT 11",
                            "precio": "$29,990",
                            "estado": "Disponible",
                            "area": "25 m²",
                            "perimetro": "5x5",
                            "image": "../assets/tipos_locales/mediano.png",
                            "linea_base": "primera_linea"
                        }
                    ]
                },
                {
                    "zona_codigo": "PT 12",
                    "subniveles": [
                        {
                            "zona_codigo": "PT 12",
                            "precio": "$28,990",
                            "estado": "Disponible",
                            "area": "25 m²",
                            "perimetro": "5x5",
                            "image": "../assets/tipos_locales/mediano.png",
                            "linea_base": "segunda_linea"
                        },
                        {
                            "zona_codigo": "PT 13",
                            "precio": "$28,990",
                            "estado": "Disponible",
                            "area": "25 m²",
                            "perimetro": "5x5",
                            "image": "../assets/tipos_locales/mediano.png",
                            "linea_base": "segunda_linea"
                        }
                    ]
                },
                {
                    "zona_codigo": "PT 14",
                    "precio": "$51,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "segunda_linea"
                }
            ]
        },
        {
            "tipo": "entrada segundaria grupo 1 derecha",
            "locales": [
                {
                    "zona_codigo": "PT 5",
                    "precio": "$56,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "segunda_linea"
                },
                {
                    "zona_codigo": "PT 6",
                    "precio": "$56,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "segunda_linea"
                },
                {
                    "zona_codigo": "PT 7",
                    "precio": "$51,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "tercera_linea"
                },
                {
                    "zona_codigo": "PT 8",
                    "precio": "$51,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "tercera_linea"
                },
                {
                    "zona_codigo": "PT 15",
                    "precio": "$51,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "segunda_linea"
                },
                {
                    "zona_codigo": "PT 16",
                    "subniveles": [
                        {
                            "zona_codigo": "PT 16",
                            "precio": "$51,990",
                            "estado": "Disponible",
                            "area": "25 m²",
                            "perimetro": "5x5",
                            "image": "../assets/tipos_locales/mediano.png",
                            "linea_base": "segunda_linea"
                        },
                        {
                            "zona_codigo": "PT 17",
                            "precio": "$46,990",
                            "estado": "Disponible",
                            "area": "25 m²",
                            "perimetro": "5x5",
                            "image": "../assets/tipos_locales/mediano.png",
                            "linea_base": "segunda_linea"
                        }
                    ]
                },
                {
                    "zona_codigo": "PT 18",
                    "subniveles": [
                        {
                            "zona_codigo": "PT 18",
                            "precio": "$46,990",
                            "estado": "Disponible",
                            "area": "25 m²",
                            "perimetro": "5x5",
                            "image": "../assets/tipos_locales/mediano.png",
                            "linea_base": "tercera_linea"
                        },
                        {
                            "zona_codigo": "PT 19",
                            "precio": "$56,990",
                            "estado": "Disponible",
                            "area": "25 m²",
                            "perimetro": "5x5",
                            "image": "../assets/tipos_locales/mediano.png",
                            "linea_base": "tercera_linea"
                        }
                    ]
                },
                {
                    "zona_codigo": "PT 20",
                    "precio": "$28,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "tercera_linea"
                }
            ]
        },
        {
            "tipo": "entrada segundaria grupo 2 izquierda",
            "locales": [
                {
                    "zona_codigo": "PT 21",
                    "precio": "$56,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "primera_linea"
                },
                {
                    "zona_codigo": "PT 22",
                    "subniveles": [
                        {
                            "zona_codigo": "PT 22",
                            "precio": "$29,990",
                            "estado": "Disponible",
                            "area": "25 m²",
                            "perimetro": "5x5",
                            "image": "../assets/tipos_locales/mediano.png",
                            "linea_base": "primera_linea"
                        },
                        {
                            "zona_codigo": "PT 23",
                            "precio": "$29,990",
                            "estado": "Disponible",
                            "area": "25 m²",
                            "perimetro": "5x5",
                            "image": "../assets/tipos_locales/mediano.png",
                            "linea_base": "primera_linea"
                        }
                    ]
                },
                {
                    "zona_codigo": "PT 24",
                    "subniveles": [
                        {
                            "zona_codigo": "PT 24",
                            "precio": "$29,990",
                            "estado": "Disponible",
                            "area": "25 m²",
                            "perimetro": "5x5",
                            "image": "../assets/tipos_locales/mediano.png",
                            "linea_base": "segunda_linea"
                        },
                        {
                            "zona_codigo": "PT 25",
                            "precio": "$29,990",
                            "estado": "Disponible",
                            "area": "25 m²",
                            "perimetro": "5x5",
                            "image": "../assets/tipos_locales/mediano.png",
                            "linea_base": "segunda_linea"
                        }
                    ]
                },
                {
                    "zona_codigo": "PT 26",
                    "precio": "$51,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "segunda_linea"
                },
                {
                    "zona_codigo": "PT 33",
                    "precio": "$46,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "primera_linea"
                },
                {
                    "zona_codigo": "PT 34",
                    "precio": "$46,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "primera_linea"
                },
                {
                    "zona_codigo": "PT 35",
                    "precio": "$56,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "segunda_linea"
                },
                {
                    "zona_codigo": "PT 360",
                    "precio": "$28,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "segunda_linea"
                }
            ]
        },
        {
            "tipo": "entrada segundaria grupo 2 derecha",
            "locales": [
                {
                    "zona_codigo": "PT 27",
                    "precio": "$56,990",
                    "estado": "Reservado",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "segunda_linea"
                },
                {
                    "zona_codigo": "PT 28",
                    "subniveles": [
                        {
                            "zona_codigo": "PT 28",
                            "precio": "$29,990",
                            "estado": "Disponible",
                            "area": "25 m²",
                            "perimetro": "5x5",
                            "image": "../assets/tipos_locales/mediano.png",
                            "linea_base": "segunda_linea"
                        },
                        {
                            "zona_codigo": "PT 29",
                            "precio": "$29,990",
                            "estado": "Disponible",
                            "area": "25 m²",
                            "perimetro": "5x5",
                            "image": "../assets/tipos_locales/mediano.png",
                            "linea_base": "segunda_linea"
                        }
                    ]
                },
                {
                    "zona_codigo": "PT 30",
                    "subniveles": [
                        {
                            "zona_codigo": "PT 30",
                            "precio": "$29,990",
                            "estado": "Disponible",
                            "area": "25 m²",
                            "perimetro": "5x5",
                            "image": "../assets/tipos_locales/mediano.png",
                            "linea_base": "tercera_linea"
                        },
                        {
                            "zona_codigo": "PT 31",
                            "precio": "$29,990",
                            "estado": "Disponible",
                            "area": "25 m²",
                            "perimetro": "5x5",
                            "image": "../assets/tipos_locales/mediano.png",
                            "linea_base": "tercera_linea"
                        }
                    ]
                },
                {
                    "zona_codigo": "PT 32",
                    "precio": "$51,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "tercera_linea"
                },
                {
                    "zona_codigo": "PT 37",
                    "precio": "$46,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "segunda_linea"
                },
                {
                    "zona_codigo": "PT 38",
                    "precio": "$46,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "segunda_linea"
                },
                {
                    "zona_codigo": "PT 39",
                    "precio": "$56,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "segunda_linea"
                },
                {
                    "zona_codigo": "PT 40",
                    "precio": "$28,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "segunda_linea"
                }
            ]
        },
        {
            "tipo": "entrada segundaria grupo 3 izquierda",
            "locales": [
                {
                    "zona_codigo": "PT 41",
                    "precio": "$56,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "primera_linea"
                },
                {
                    "zona_codigo": "PT 42",
                    "precio": "$56,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "primera_linea"
                },
                {
                    "zona_codigo": "PT 43",
                    "precio": "$51,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "segunda_linea"
                },
                {
                    "zona_codigo": "PT 44",
                    "precio": "$51,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "segunda_linea"
                },
                {
                    "zona_codigo": "PT 49",
                    "precio": "$51,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "primera_linea"
                },
                {
                    "zona_codigo": "PT 50",
                    "subniveles": [
                        {
                            "zona_codigo": "PT 50",
                            "precio": "$29,990",
                            "estado": "Disponible",
                            "area": "25 m²",
                            "perimetro": "5x5",
                            "image": "../assets/tipos_locales/mediano.png",
                            "linea_base": "primera_linea"
                        },
                        {
                            "zona_codigo": "PT 51",
                            "precio": "$29,990",
                            "estado": "Disponible",
                            "area": "25 m²",
                            "perimetro": "5x5",
                            "image": "../assets/tipos_locales/mediano.png",
                            "linea_base": "primera_linea"
                        }
                    ]
                },
                {
                    "zona_codigo": "PT 52",
                    "subniveles": [
                        {
                            "zona_codigo": "PT 52",
                            "precio": "$29,990",
                            "estado": "Disponible",
                            "area": "25 m²",
                            "perimetro": "5x5",
                            "image": "../assets/tipos_locales/mediano.png",
                            "linea_base": "segunda_linea"
                        },
                        {
                            "zona_codigo": "PT 53",
                            "precio": "$29,990",
                            "estado": "Disponible",
                            "area": "25 m²",
                            "perimetro": "5x5",
                            "image": "../assets/tipos_locales/mediano.png",
                            "linea_base": "segunda_linea"
                        }
                    ]
                },
                {
                    "zona_codigo": "PT 54",
                    "precio": "$28,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "segunda_linea"
                }
            ]
        },
        {
            "tipo": "entrada segundaria grupo 3 derecha",
            "locales": [
                {
                    "zona_codigo": "PT 45",
                    "precio": "$56,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "segunda_linea"
                },
                {
                    "zona_codigo": "PT 46",
                    "precio": "$56,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "segunda_linea"
                },
                {
                    "zona_codigo": "PT 47",
                    "precio": "$51,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "segunda_linea"
                },
                {
                    "zona_codigo": "PT 48",
                    "precio": "$51,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "segunda_linea"
                },
                {
                    "zona_codigo": "PT 55",
                    "precio": "$51,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "segunda_linea"
                },
                {
                    "zona_codigo": "PT 56",
                    "subniveles": [
                        {
                            "zona_codigo": "PT 56",
                            "precio": "$29,990",
                            "estado": "Disponible",
                            "area": "25 m²",
                            "perimetro": "5x5",
                            "image": "../assets/tipos_locales/mediano.png",
                            "linea_base": "segunda_linea"
                        },
                        {
                            "zona_codigo": "PT 57",
                            "precio": "$29,990",
                            "estado": "Disponible",
                            "area": "25 m²",
                            "perimetro": "5x5",
                            "image": "../assets/tipos_locales/mediano.png",
                            "linea_base": "segunda_linea"
                        }
                    ]
                },
                {
                    "zona_codigo": "PT 58",
                    "subniveles": [
                        {
                            "zona_codigo": "PT 58",
                            "precio": "$29,990",
                            "estado": "Disponible",
                            "area": "25 m²",
                            "perimetro": "5x5",
                            "image": "../assets/tipos_locales/mediano.png",
                            "linea_base": "tercera_linea"
                        },
                        {
                            "zona_codigo": "PT 59",
                            "precio": "$29,990",
                            "estado": "Disponible",
                            "area": "25 m²",
                            "perimetro": "5x5",
                            "image": "../assets/tipos_locales/mediano.png",
                            "linea_base": "tercera_linea"
                        }
                    ]
                },
                {
                    "zona_codigo": "PT 60",
                    "precio": "$28,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "tercera_linea"
                }
            ]
        },
        {
            "tipo": "entrada segundaria grupo 4 izquierda",
            "locales": [
                {
                    "zona_codigo": "PT 61",
                    "precio": "$56,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "primera_linea"
                },
                {
                    "zona_codigo": "PT 62-63",
                    "subniveles": [
                        {
                            "zona_codigo": "PT 62",
                            "precio": "$29,990",
                            "estado": "Disponible",
                            "area": "25 m²",
                            "perimetro": "5x5",
                            "image": "../assets/tipos_locales/mediano.png",
                            "linea_base": "primera_linea"
                        },
                        {
                            "zona_codigo": "PT 63",
                            "precio": "$29,990",
                            "estado": "Disponible",
                            "area": "25 m²",
                            "perimetro": "5x5",
                            "image": "../assets/tipos_locales/mediano.png",
                            "linea_base": "primera_linea"
                        }
                    ]
                },
                {
                    "zona_codigo": "PT 64-65",
                    "subniveles": [
                        {
                            "zona_codigo": "PT 64",
                            "precio": "$29,990",
                            "estado": "Disponible",
                            "area": "25 m²",
                            "perimetro": "5x5",
                            "image": "../assets/tipos_locales/mediano.png",
                            "linea_base": "segunda_linea"
                        },
                        {
                            "zona_codigo": "PT 65",
                            "precio": "$29,990",
                            "estado": "Disponible",
                            "area": "25 m²",
                            "perimetro": "5x5",
                            "image": "../assets/tipos_locales/mediano.png",
                            "linea_base": "segunda_linea"
                        }
                    ]
                },
                {
                    "zona_codigo": "PT 66",
                    "precio": "$51,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "segunda_linea"
                },
                {
                    "zona_codigo": "PT 73",
                    "precio": "$46,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "primera_linea"
                },
                {
                    "zona_codigo": "PT 74-75",
                    "subniveles": [
                        {
                            "zona_codigo": "PT 74",
                            "precio": "$29,990",
                            "estado": "Disponible",
                            "area": "25 m²",
                            "perimetro": "5x5",
                            "image": "../assets/tipos_locales/mediano.png",
                            "linea_base": "primera_linea"
                        },
                        {
                            "zona_codigo": "PT 75",
                            "precio": "$29,990",
                            "estado": "Disponible",
                            "area": "25 m²",
                            "perimetro": "5x5",
                            "image": "../assets/tipos_locales/mediano.png",
                            "linea_base": "primera_linea"
                        }
                    ]
                },
                {
                    "zona_codigo": "PT 76-77",
                    "subniveles": [
                        {
                            "zona_codigo": "PT 76",
                            "precio": "$29,990",
                            "estado": "Disponible",
                            "area": "25 m²",
                            "perimetro": "5x5",
                            "image": "../assets/tipos_locales/mediano.png",
                            "linea_base": "segunda_linea"
                        },
                        {
                            "zona_codigo": "PT 77",
                            "precio": "$29,990",
                            "estado": "Disponible",
                            "area": "25 m²",
                            "perimetro": "5x5",
                            "image": "../assets/tipos_locales/mediano.png",
                            "linea_base": "segunda_linea"
                        }
                    ]
                },
                {
                    "zona_codigo": "PT 78",
                    "precio": "$28,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "segunda_linea"
                }
            ]
        },
        {
            "tipo": "entrada segundaria grupo 4 derecha",
            "locales": [
                {
                    "zona_codigo": "PT 67",
                    "precio": "$56,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "segunda_linea"
                },
                {
                    "zona_codigo": "PT 68-69",
                    "subniveles": [
                        {
                            "zona_codigo": "PT 68",
                            "precio": "$29,990",
                            "estado": "Disponible",
                            "area": "25 m²",
                            "perimetro": "5x5",
                            "image": "../assets/tipos_locales/mediano.png",
                            "linea_base": "segunda_linea"
                        },
                        {
                            "zona_codigo": "PT 69",
                            "precio": "$29,990",
                            "estado": "Disponible",
                            "area": "25 m²",
                            "perimetro": "5x5",
                            "image": "../assets/tipos_locales/mediano.png",
                            "linea_base": "segunda_linea"
                        }
                    ]
                },
                {
                    "zona_codigo": "PT 70-71",
                    "subniveles": [
                        {
                            "zona_codigo": "PT 70",
                            "precio": "$29,990",
                            "estado": "Disponible",
                            "area": "25 m²",
                            "perimetro": "5x5",
                            "image": "../assets/tipos_locales/mediano.png",
                            "linea_base": "tercera_linea"
                        },
                        {
                            "zona_codigo": "PT 71",
                            "precio": "$29,990",
                            "estado": "Disponible",
                            "area": "25 m²",
                            "perimetro": "5x5",
                            "image": "../assets/tipos_locales/mediano.png",
                            "linea_base": "tercera_linea"
                        }
                    ]
                },
                {
                    "zona_codigo": "PT 72",
                    "precio": "$51,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "tercera_linea"
                },
                {
                    "zona_codigo": "PT 79",
                    "precio": "$46,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "segunda_linea"
                },
                {
                    "zona_codigo": "PT 80-81",
                    "subniveles": [
                        {
                            "zona_codigo": "PT 80",
                            "precio": "$29,990",
                            "estado": "Disponible",
                            "area": "25 m²",
                            "perimetro": "5x5",
                            "image": "../assets/tipos_locales/mediano.png",
                            "linea_base": "segunda_linea"
                        },
                        {
                            "zona_codigo": "PT 81",
                            "precio": "$29,990",
                            "estado": "Disponible",
                            "area": "25 m²",
                            "perimetro": "5x5",
                            "image": "../assets/tipos_locales/mediano.png",
                            "linea_base": "segunda_linea"
                        }
                    ]
                },
                {
                    "zona_codigo": "PT 82-83",
                    "subniveles": [
                        {
                            "zona_codigo": "PT 82",
                            "precio": "$29,990",
                            "estado": "Disponible",
                            "area": "25 m²",
                            "perimetro": "5x5",
                            "image": "../assets/tipos_locales/mediano.png",
                            "linea_base": "tercera_linea"
                        },
                        {
                            "zona_codigo": "PT 83",
                            "precio": "$29,990",
                            "estado": "Disponible",
                            "area": "25 m²",
                            "perimetro": "5x5",
                            "image": "../assets/tipos_locales/mediano.png",
                            "linea_base": "tercera_linea"
                        }
                    ]
                },
                {
                    "zona_codigo": "PT 84",
                    "precio": "$28,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "tercera_linea"
                }
            ]
        },
        {
            "tipo": "entrada segundaria grupo 5 izquierda",
            "locales": [
                {
                    "zona_codigo": "PT 85",
                    "precio": "$56,990",
                    "estado": "Disponible",
                    "linea_base": "primera_linea"
                },
                {
                    "zona_codigo": "PT 86-87",
                    "subniveles": [
                        {
                            "zona_codigo": "PT 86",
                            "precio": "$29,990",
                            "estado": "Disponible",
                            "area": "25 m²",
                            "perimetro": "5x5",
                            "image": "../assets/tipos_locales/mediano.png",
                            "linea_base": "primera_linea"
                        },
                        {
                            "zona_codigo": "PT 87",
                            "precio": "$29,990",
                            "estado": "Disponible",
                            "area": "25 m²",
                            "perimetro": "5x5",
                            "image": "../assets/tipos_locales/mediano.png",
                            "linea_base": "primera_linea"
                        }
                    ]
                },
                {
                    "zona_codigo": "PT 88-89",
                    "subniveles": [
                        {
                            "zona_codigo": "PT 88",
                            "precio": "$29,990",
                            "estado": "Disponible",
                            "area": "25 m²",
                            "perimetro": "5x5",
                            "linea_base": "segunda_linea"
                        },
                        {
                            "zona_codigo": "PT 89",
                            "precio": "$29,990",
                            "estado": "Disponible",
                            "area": "25 m²",
                            "perimetro": "5x5",
                            "linea_base": "segunda_linea"
                        }
                    ]
                },
                {
                    "zona_codigo": "PT 90",
                    "precio": "$51,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "segunda_linea"
                },
                {
                    "zona_codigo": "PT 97",
                    "precio": "$46,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "primera_linea"
                },
                {
                    "zona_codigo": "PT 98",
                    "precio": "$46,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "primera_linea"
                },
                {
                    "zona_codigo": "PT 99",
                    "precio": "$56,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "segunda_linea"
                },
                {
                    "zona_codigo": "PT 100",
                    "precio": "$28,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "segunda_linea"
                }
            ]
        },
        {
            "tipo": "entrada segundaria grupo 5 derecha",
            "locales": [
                {
                    "zona_codigo": "PT 91",
                    "precio": "$56,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "segunda_linea"
                },
                {
                    "zona_codigo": "PT 92-93",
                    "subniveles": [
                        {
                            "zona_codigo": "PT 92",
                            "precio": "$29,990",
                            "estado": "Disponible",
                            "area": "25 m²",
                            "perimetro": "5x5",
                            "image": "../assets/tipos_locales/mediano.png",
                            "linea_base": "segunda_linea"
                        },
                        {
                            "zona_codigo": "PT 93",
                            "precio": "$29,990",
                            "estado": "Disponible",
                            "area": "25 m²",
                            "perimetro": "5x5",
                            "image": "../assets/tipos_locales/mediano.png",
                            "linea_base": "segunda_linea"
                        }
                    ]
                },
                {
                    "zona_codigo": "PT 94-95",
                    "subniveles": [
                        {
                            "zona_codigo": "PT 94",
                            "precio": "$29,990",
                            "estado": "Disponible",
                            "area": "25 m²",
                            "perimetro": "5x5",
                            "image": "../assets/tipos_locales/mediano.png",
                            "linea_base": "tercera_linea"
                        },
                        {
                            "zona_codigo": "PT 95",
                            "precio": "$29,990",
                            "estado": "Disponible",
                            "area": "25 m²",
                            "perimetro": "5x5",
                            "image": "../assets/tipos_locales/mediano.png",
                            "linea_base": "tercera_linea"
                        }
                    ]
                },
                {
                    "zona_codigo": "PT 96",
                    "precio": "$51,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "tercera_linea"
                },
                {
                    "zona_codigo": "PT 101",
                    "precio": "$46,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "segunda_linea"
                },
                {
                    "zona_codigo": "PT 102",
                    "precio": "$46,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "segunda_linea"
                },
                {
                    "zona_codigo": "PT 103",
                    "precio": "$56,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "tercera_linea"
                },
                {
                    "zona_codigo": "PT 104",
                    "precio": "$28,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "tercera_linea"
                }
            ]
        },
        {
            "tipo": "entrada grupo 1 larga",
            "locales": [
                {
                    "zona_codigo": "PT 105",
                    "altura":"h-[80px]",
                    "precio": "$56,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "tercera_linea"
                },
                {
                    "zona_codigo": "PT 106",
                    "altura":"h-[80px]",
                    "precio": "$56,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "tercera_linea"
                },
                {
                    "zona_codigo": "PT 107",
                    "altura":"h-[38px]",
                    "precio": "$27,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "tercera_linea"
                },
                {
                    "zona_codigo": "PT 108",
                    "altura":"h-[80px]",
                    "precio": "$27,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "tercera_linea"
                },
                {
                    "zona_codigo": "PT 109",
                    "altura":"h-[80px]",
                    "precio": "$27,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "tercera_linea"
                }
            ]
        },
        {
            "tipo": "entrada grupo 2 larga",
            "locales": [
                {
                    "zona_codigo": "PT 110",
                    "altura":"h-[80px]",
                    "precio": "$51,990",
                    "estado": "Vendido",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "tercera_linea"
                },
                {
                    "zona_codigo": "PT 111",
                    "altura":"h-[80px]",
                    "precio": "$46,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "tercera_linea"
                },
                {
                    "zona_codigo": "PT 112",
                    "altura":"h-[38px]",
                    "precio": "$51,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "tercera_linea"
                },
                {
                    "zona_codigo": "PT 113",
                    "altura":"h-[80px]",
                    "precio": "$51,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "tercera_linea"
                },
                {
                    "zona_codigo": "PT 114",
                    "altura":"h-[80px]",
                    "precio": "$51,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "tercera_linea"
                },
                {
                    "zona_codigo": "PT 115",
                    "altura":"h-[38px]",
                    "precio": "$51,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "tercera_linea"
                },
                {
                    "zona_codigo": "PT 116",
                    "altura":"h-[80px]",
                    "precio": "$51,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "tercera_linea"
                },
                {
                    "zona_codigo": "PT 117",
                    "altura":"h-[80px]",
                    "precio": "$51,990",
                    "estado": "Disponible",
                    "area": "25 m²",
                    "perimetro": "5x5",
                    "image": "../assets/tipos_locales/mediano.png",
                    "linea_base": "tercera_linea"
                }
            ]
        }
        
    ]

    grupos_final = combinar_grupos_con_bd(db, grupos_estaticos)
    return {"grupos": grupos_final}







