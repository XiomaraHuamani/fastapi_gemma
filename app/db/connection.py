from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from decouple import config  # Para manejar variables de entorno

DATABASE_URL = (
    f"mssql+pyodbc://{config('DB_USER')}:{config('DB_PASSWORD')}@"
    f"{config('DB_SERVER')}/{config('DB_NAME')}?driver={config('DB_DRIVER')}"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from app.models.user import User  # Importa todos los modelos
    Base.metadata.create_all(bind=engine)
