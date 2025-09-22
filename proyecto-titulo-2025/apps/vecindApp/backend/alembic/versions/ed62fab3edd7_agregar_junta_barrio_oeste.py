"""agregar_junta_barrio_oeste

Revision ID: ed62fab3edd7
Revises: 6793fd52c084
Create Date: 2025-09-21 22:55:50.586686

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ed62fab3edd7'
down_revision: Union[str, Sequence[str], None] = '6793fd52c084'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Primero, asegurar que existe la región y comuna necesaria
    # Crear región si no existe
    op.execute("""
        INSERT INTO "vecindapp".region (nombre) 
        SELECT 'Región Metropolitana de Santiago'
        WHERE NOT EXISTS (
            SELECT 1 FROM "vecindapp".region 
            WHERE nombre = 'Región Metropolitana de Santiago'
        )
    """)
    
    # Obtener ID de la región
    connection = op.get_bind()
    result = connection.execute(sa.text("""
        SELECT id_region FROM "vecindapp".region 
        WHERE nombre = 'Región Metropolitana de Santiago'
    """))
    id_region = result.scalar()
    
    # Crear comuna si no existe
    op.execute(f"""
        INSERT INTO "vecindapp".comuna (id_region, nombre) 
        SELECT {id_region}, 'Maipú'
        WHERE NOT EXISTS (
            SELECT 1 FROM "vecindapp".comuna 
            WHERE nombre = 'Maipú' AND id_region = {id_region}
        )
    """)
    
    # Obtener ID de la comuna
    result = connection.execute(sa.text(f"""
        SELECT id_comuna FROM "vecindapp".comuna 
        WHERE nombre = 'Maipú' AND id_region = {id_region}
    """))
    id_comuna = result.scalar()
    
    # Insertar la Junta de Vecinos Barrio Oeste
    op.execute(f"""
        INSERT INTO "vecindapp".junta (id_comuna, nombre, direccion, telefono, email, descripcion) 
        SELECT {id_comuna}, 'Junta de Vecinos Barrio Oeste', 'La Salle 1565', '+56 2 2890 1234', 'contacto@contacto.cl', 
               'Junta de vecinos del sector Barrio Oeste, comprometida con el desarrollo y bienestar de nuestra comunidad.'
        WHERE NOT EXISTS (
            SELECT 1 FROM "vecindapp".junta 
            WHERE nombre = 'Junta de Vecinos Barrio Oeste' AND id_comuna = {id_comuna}
        )
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # Eliminar la junta creada
    op.execute("""
        DELETE FROM "vecindapp".junta 
        WHERE nombre = 'Junta de Vecinos Barrio Oeste'
    """)
