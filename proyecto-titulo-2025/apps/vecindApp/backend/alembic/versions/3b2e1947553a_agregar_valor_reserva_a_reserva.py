"""agregar_valor_reserva_a_reserva

Revision ID: 3b2e1947553a
Revises: 1361d67f6c39
Create Date: 2025-10-02 19:43:16.608298

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3b2e1947553a'
down_revision: Union[str, Sequence[str], None] = '1361d67f6c39'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Agregar columna valor_reserva a reserva
    op.add_column('reserva', 
                  sa.Column('valor_reserva', sa.Numeric(10, 2), nullable=False, server_default='0.00'),
                  schema='vecindapp')
    
    # Agregar constraint para valores positivos
    op.create_check_constraint(
        'ck_reserva_valor_positivo',
        'reserva',
        'valor_reserva >= 0',
        schema='vecindapp'
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Eliminar constraint
    op.drop_constraint('ck_reserva_valor_positivo', 'reserva', schema='vecindapp')
    
    # Eliminar columna
    op.drop_column('reserva', 'valor_reserva', schema='vecindapp')
