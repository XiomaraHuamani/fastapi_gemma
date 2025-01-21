from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.apps.users.models import Base  # ✅ Asegúrate de importar los modelos

# Crear el motor de SQLAlchemy
engine = create_engine(settings.DATABASE_URL)

# Crear una sesión de conexión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()  # ⬅️ Si esta línea está en tu código, ¡BORRALA!

# Asegurar que Base.metadata tenga los modelos
Base.metadata.create_all(bind=engine)
