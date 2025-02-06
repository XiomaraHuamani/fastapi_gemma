# app/apps/locales/utils.py
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
