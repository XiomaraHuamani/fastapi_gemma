from typing import List, Dict, Any
import copy
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.connection import get_db
from app.apps.locales.models import Local, Zona

def _get_image_url(metraje):
    if metraje and metraje.image:
        try:
            return metraje.image.url
        except AttributeError:
            return metraje.image
    return None

def serialize_local(local):
    precio = f"${local.precio_base:,.2f}" if local.precio_base is not None else None
    estado = local.estado.capitalize() if local.estado else None
    area = f"{local.metraje.area} m²" if local.metraje and local.metraje.area else None
    perimetro = local.metraje.perimetro if local.metraje and local.metraje.perimetro else None
    image = _get_image_url(local.metraje)
    linea_base = local.zona.linea_base.value if local.zona and hasattr(local.zona.linea_base, "value") else None

    data = {
        "zona_codigo": local.zona.codigo if local.zona else None,
        "precio": precio,
        "estado": estado,
        "area": area,
        "perimetro": perimetro,
        "image": image,
        "linea_base": linea_base,
        "altura": getattr(local, "altura", None)
    }
    return data

def serialize_local_with_subniveles(local):
    data = serialize_local(local)
    if local.subniveles:
        data["subniveles"] = [serialize_local(sub) for sub in local.subniveles]
    return data
# Ajusta según tu modelo


# Función recursiva para recolectar todos los zona_codigos de la estructura
def recolectar_zona_codigos_recursivo(local_item: Dict[str, Any], codigos_set: set):
    zona_codigo = local_item.get("zona_codigo")
    if zona_codigo:
        codigos_set.add(zona_codigo)
    for sub in local_item.get("subniveles", []):
        recolectar_zona_codigos_recursivo(sub, codigos_set)


def recolectar_todos_los_codigos(grupos_estaticos: List[Dict[str, Any]]) -> set:
    codigos = set()
    for grupo in grupos_estaticos:
        for local_item in grupo.get("locales", []):
            recolectar_zona_codigos_recursivo(local_item, codigos)
    return codigos


# Función para hacer una sola consulta y armar un diccionario { zona_codigo: Local }
def armar_diccionario_locales(db: Session, codigos_set: set) -> Dict[str, Local]:
    if not codigos_set:
        return {}
    lista_codigos = list(codigos_set)
    # Realiza una sola consulta que traiga todos los Local que tengan zona.codigo en la lista
    locales_db = (
        db.query(Local)
        .join(Zona)
        .filter(Zona.codigo.in_(lista_codigos))
        .all()
    )
    dict_locales = {}
    for loc in locales_db:
        if loc.zona:
            dict_locales[loc.zona.codigo] = loc
    return dict_locales


# Función para actualizar los datos de un local usando el diccionario
def actualizar_local_desde_dict(local_item: Dict[str, Any], dict_locales: Dict[str, Local]):
    zona_codigo = local_item.get("zona_codigo")
    if not zona_codigo:
        return
    local_db = dict_locales.get(zona_codigo)
    if not local_db:
        return

    # Actualiza el precio formateado
    if local_db.precio_base is not None:
        local_item["precio"] = f"${local_db.precio_base:,.0f}"
    # Actualiza el estado (asumiendo que es un Enum)
    if local_db.estado:
        local_item["estado"] = local_db.estado.value.capitalize()
    # Actualiza área, perímetro e imagen si existe metraje
    if local_db.metraje:
        if local_db.metraje.area:
            local_item["area"] = f"{local_db.metraje.area} m²"
        if local_db.metraje.perimetro:
            local_item["perimetro"] = local_db.metraje.perimetro
        if local_db.metraje.image:
            local_item["image"] = local_db.metraje.image
    # Actualiza linea_base
    if local_db.zona and hasattr(local_db.zona.linea_base, "value"):
        local_item["linea_base"] = local_db.zona.linea_base.value
    elif local_db.zona and local_db.zona.linea_base:
        local_item["linea_base"] = local_db.zona.linea_base


# Función recursiva para procesar locales y subniveles usando el dict_locales
def procesar_local_recursivo(local_item: Dict[str, Any], dict_locales: Dict[str, Local]):
    actualizar_local_desde_dict(local_item, dict_locales)
    for sub in local_item.get("subniveles", []):
        procesar_local_recursivo(sub, dict_locales)


# Función principal que combina la estructura estática con datos de la BD
def combinar_grupos_con_bd(db: Session, grupos_estaticos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    grupos_resultantes = copy.deepcopy(grupos_estaticos)
    # Recolecta todos los zona_codigos de la estructura
    codigos = recolectar_todos_los_codigos(grupos_estaticos)
    # Realiza una única consulta para traer los Local y arma un dict
    dict_locales = armar_diccionario_locales(db, codigos)
    # Procesa cada local y subnivel en la estructura
    for grupo in grupos_resultantes:
        for local_item in grupo.get("locales", []):
            procesar_local_recursivo(local_item, dict_locales)
    return grupos_resultantes

