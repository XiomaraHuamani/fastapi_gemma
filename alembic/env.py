from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context
from app.db.connection import Base
from app.core.config import settings  # ✅ Importamos settings correctamente

# 🔥 IMPORTANTE: Importamos los modelos explícitamente para que Alembic los detecte
from app.apps.users import models  # ✅ Esto asegurará que la tabla `users` sea incluida
from app.apps.locales import models 

# Configuración del logging
config = context.config
fileConfig(config.config_file_name)

# ✅ Establecer la URL de conexión usando settings.DATABASE_URL
DATABASE_URL = settings.DATABASE_URL  # 🔥 Definimos la variable correctamente
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Metadatos de los modelos
target_metadata = Base.metadata

def run_migrations_offline():
    """Ejecutar migraciones en modo offline."""
    context.configure(
        url=DATABASE_URL,  # ✅ Aquí usamos la variable correcta
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Ejecutar migraciones en modo online."""
    engine = create_engine(DATABASE_URL, poolclass=pool.NullPool)  # ✅ Usamos `DATABASE_URL` correctamente
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
