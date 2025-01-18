from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
from app.db.connection import Base, DATABASE_URL

# Configuración del logging
config = context.config
fileConfig(config.config_file_name)

# Establecer la URL de conexión desde `DATABASE_URL`
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Metadatos de los modelos
target_metadata = Base.metadata

def run_migrations_offline():
    """Ejecutar migraciones en modo offline."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Ejecutar migraciones en modo online."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
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
