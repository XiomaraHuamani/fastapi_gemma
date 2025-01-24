from sqlalchemy.orm import Session
from app.apps.locales.models import Local
from app.apps.locales.schemas import LocalCreate, LocalUpdate


def get_locales(db: Session):
    return db.query(Local).all()

def get_local_by_id(db: Session, local_id: int):
    return db.query(Local).filter(Local.id == local_id).first()

def create_local(db: Session, local: LocalCreate):
    nuevo_local = Local(**local.dict())
    db.add(nuevo_local)
    db.commit()
    db.refresh(nuevo_local)
    return nuevo_local

def update_local(db: Session, local_id: int, local_data: LocalUpdate):
    local = db.query(Local).filter(Local.id == local_id).first()
    if not local:
        return None

    for key, value in local_data.dict().items():
        setattr(local, key, value)

    db.commit()
    db.refresh(local)
    return local

def delete_local(db: Session, local_id: int):
    local = db.query(Local).filter(Local.id == local_id).first()
    if not local:
        return None

    db.delete(local)
    db.commit()
    return local
