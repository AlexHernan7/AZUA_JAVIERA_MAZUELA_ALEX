"""
Configuración de Alembic para VecindApp.
Configuración simple y directa para una sola base de datos.
"""

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool, text
from alembic import context

# Importar configuración y modelos
from src.core.config import settings
from src.database import Base

# Importar todos los modelos para que Alembic los detecte
from src.database.models import *

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata

def get_url():
    """Obtener la URL de conexión desde settings."""
    return settings.database.sync_url

def include_object(object, name, type_, reflected, compare_to):
    """Determina qué objetos incluir en las migraciones."""
    # Solo incluir objetos del schema vecindapp
    if type_ == "table":
        return object.schema == settings.database.db_schema
    elif type_ == "column":
        return object.table.schema == settings.database.db_schema
    elif type_ == "sequence":
        return object.schema == settings.database.db_schema
    return True

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        include_object=include_object,
        version_table_schema=settings.database.db_schema,
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Configurar la URL de conexión dinámicamente
    config.set_main_option("sqlalchemy.url", get_url())
    
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # Crear schema si no existe
        try:
            connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {settings.database.db_schema}"))
            connection.commit()
            print(f"✅ Schema {settings.database.db_schema} verificado/creado")
        except Exception as e:
            print(f"⚠️  Warning al crear schema: {e}")
        
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            include_object=include_object,
            version_table_schema=settings.database.db_schema,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()