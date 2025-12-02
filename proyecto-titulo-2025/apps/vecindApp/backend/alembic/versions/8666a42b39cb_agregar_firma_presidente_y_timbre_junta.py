"""agregar_firma_presidente_y_timbre_junta

Revision ID: 8666a42b39cb
Revises: 0c058d0a30d6
Create Date: 2025-01-27 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8666a42b39cb'
down_revision: Union[str, Sequence[str], None] = '0c058d0a30d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Agregar columna firma_presidente
    op.add_column('vecindapp.junta', 
        sa.Column('firma_presidente', sa.LargeBinary(), nullable=True)
    )
    
    # Agregar columna timbre
    op.add_column('vecindapp.junta',
        sa.Column('timbre', sa.LargeBinary(), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Eliminar columna timbre
    op.drop_column('vecindapp.junta', 'timbre')
    
    # Eliminar columna firma_presidente
    op.drop_column('vecindapp.junta', 'firma_presidente')

