from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context
from app.db.connection import Base, DATABASE_URL

# Configuración del logging
config = context.config
fileConfig(config.config_file_name)

# Establecer la URL de conexión desde `DATABASE_URL`
config.set_main_option("sqlalchemy.url", str(DATABASE_URL))

# Metadatos de los modelos
target_metadata = Base.metadata

# 🔥 Cambiar el `engine` para que use directamente DATABASE_URL
def run_migrations_offline():
    """Ejecutar migraciones en modo offline."""
    context.configure(
        url=str(DATABASE_URL),  # 🔥 Aquí aseguramos que use la URL correcta
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Ejecutar migraciones en modo online."""
    engine = create_engine(DATABASE_URL, poolclass=pool.NullPool)  # 🔥 Aquí usamos `create_engine`
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
