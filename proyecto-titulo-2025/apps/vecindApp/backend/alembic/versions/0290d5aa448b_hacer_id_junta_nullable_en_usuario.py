"""hacer_id_junta_nullable_en_usuario

Revision ID: 0290d5aa448b
Revises: 7d6fbf4d187c
Create Date: 2025-09-22 12:04:57.401156

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0290d5aa448b'
down_revision: Union[str, Sequence[str], None] = '7d6fbf4d187c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Hacer nullable la columna id_junta en la tabla usuario
    op.alter_column('usuario', 'id_junta',
                   existing_type=sa.BIGINT(),
                   nullable=True,
                   schema='vecindapp')


def downgrade() -> None:
    """Downgrade schema."""
    # Revertir: hacer NOT NULL la columna id_junta
    op.alter_column('usuario', 'id_junta',
                   existing_type=sa.BIGINT(),
                   nullable=False,
                   schema='vecindapp')
