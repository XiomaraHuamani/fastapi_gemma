from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.connection import get_db
from app.apps.locales.models import Categoria, Zona, Metraje, Cliente, Local
from app.apps.locales.schemas import (
    CategoriaCreate, CategoriaResponse,
    ZonaCreate, ZonaResponse,
    MetrajeCreate, MetrajeResponse,
    ClienteCreate, ClienteResponse,
    LocalCreate, LocalResponse
)

router = APIRouter(
    prefix="/locales",
    tags=["Locales"]
)

# ✅ CATEGORÍAS CRUD
@router.post("/categorias", response_model=CategoriaResponse)
def create_categoria(data: CategoriaCreate, db: Session = Depends(get_db)):
    categoria = Categoria(**data.dict())
    db.add(categoria)
    db.commit()
    db.refresh(categoria)
    return categoria

@router.get("/categorias", response_model=List[CategoriaResponse])  # ✅ Usa List en lugar de list
def get_categorias(db: Session = Depends(get_db)):
    categorias = db.query(Categoria).all()
    return categorias

@router.get("/categorias/{categoria_id}", response_model=CategoriaResponse)
def get_categoria(categoria_id: int, db: Session = Depends(get_db)):
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return categoria

@router.delete("/categorias/{categoria_id}")
def delete_categoria(categoria_id: int, db: Session = Depends(get_db)):
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    db.delete(categoria)
    db.commit()
    return {"message": "Categoría eliminada"}

# ✅ ZONAS CRUD
@router.post("/zonas", response_model=ZonaResponse)
def create_zona(data: ZonaCreate, db: Session = Depends(get_db)):
    zona = Zona(**data.dict())
    db.add(zona)
    db.commit()
    db.refresh(zona)
    return zona

@router.get("/zonas", response_model=List[ZonaResponse])  # ✅ Usa List en lugar de list
def get_zonas(db: Session = Depends(get_db)):
    zonas = db.query(Zona).all()
    return zonas

@router.delete("/zonas/{zona_id}")
def delete_zona(zona_id: int, db: Session = Depends(get_db)):
    zona = db.query(Zona).filter(Zona.id == zona_id).first()
    if not zona:
        raise HTTPException(status_code=404, detail="Zona no encontrada")
    db.delete(zona)
    db.commit()
    return {"message": "Zona eliminada"}

# ✅ METRAJES CRUD
@router.post("/metrajes", response_model=MetrajeResponse)
def create_metraje(data: MetrajeCreate, db: Session = Depends(get_db)):
    metraje = Metraje(**data.dict())
    db.add(metraje)
    db.commit()
    db.refresh(metraje)
    return metraje

@router.get("/metrajes", response_model=List[MetrajeResponse])  
def get_metrajes(db: Session = Depends(get_db)):
    metrajes = db.query(Metraje).all()
    return metrajes

# ✅ CLIENTES CRUD
@router.post("/clientes", response_model=ClienteResponse)
def create_cliente(data: ClienteCreate, db: Session = Depends(get_db)):
    cliente = Cliente(**data.dict())
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return cliente

@router.get("/clientes", response_model=List[ClienteResponse])  
def get_clientes(db: Session = Depends(get_db)):
    clientes = db.query(Cliente).all()
    return clientes

# ✅ LOCALES CRUD
@router.post("/locales", response_model=LocalResponse)
def create_local(data: LocalCreate, db: Session = Depends(get_db)):
    local = Local(**data.dict())
    db.add(local)
    db.commit()
    db.refresh(local)
    return local

@router.get("/locales", response_model=List[LocalResponse])  
def get_locales(db: Session = Depends(get_db)):
    locales = db.query(Local).all()
    return locales
