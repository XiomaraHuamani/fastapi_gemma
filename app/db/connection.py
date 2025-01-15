from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from decouple import config  # Para manejar variables de entorno

# Configuración de la URL de conexión
DATABASE_URL = (
    f"mssql+pyodbc://{config('DB_USER')}:{config('DB_PASSWORD')}@"
    f"{config('DB_SERVER')}/{config('DB_NAME')}?driver={config('DB_DRIVER')}"
)

# Crear el motor de SQLAlchemy
engine = create_engine(DATABASE_URL)

# Crear una sesión de conexión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()

# Dependencia para obtener la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
