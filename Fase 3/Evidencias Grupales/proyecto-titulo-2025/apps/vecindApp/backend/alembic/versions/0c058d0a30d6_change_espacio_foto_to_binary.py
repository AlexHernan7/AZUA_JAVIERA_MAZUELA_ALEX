"""change_espacio_foto_to_binary

Revision ID: 0c058d0a30d6
Revises: d08f032c9633
Create Date: 2025-10-15 20:10:07.142078

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0c058d0a30d6'
down_revision: Union[str, Sequence[str], None] = 'd08f032c9633'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Primero, establecer todos los valores existentes a NULL
    # porque no podemos convertir rutas de texto a binario automáticamente
    op.execute("UPDATE vecindapp.espacio SET foto = NULL WHERE foto IS NOT NULL")
    
    # Cambiar el tipo de columna de TEXT a BYTEA usando USING para forzar la conversión
    op.execute("ALTER TABLE vecindapp.espacio ALTER COLUMN foto TYPE BYTEA USING foto::BYTEA")


def downgrade() -> None:
    """Downgrade schema."""
    # Establecer todos los valores a NULL antes de cambiar el tipo
    op.execute("UPDATE vecindapp.espacio SET foto = NULL WHERE foto IS NOT NULL")
    
    # Volver a cambiar el tipo de columna de BYTEA a TEXT
    op.execute("ALTER TABLE vecindapp.espacio ALTER COLUMN foto TYPE TEXT")
