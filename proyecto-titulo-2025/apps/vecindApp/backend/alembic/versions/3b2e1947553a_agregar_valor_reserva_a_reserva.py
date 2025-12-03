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
    from sqlalchemy import inspect
    
    # Verificar si la columna ya existe (idempotente)
    conn = op.get_bind()
    inspector = inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('reserva', schema='vecindapp')]
    
    # Agregar columna valor_reserva solo si no existe
    if 'valor_reserva' not in columns:
        op.add_column('reserva', 
                      sa.Column('valor_reserva', sa.Numeric(10, 2), nullable=False, server_default='0.00'),
                      schema='vecindapp')
        print("✅ Columna valor_reserva agregada")
    else:
        print("ℹ️  Columna valor_reserva ya existe")
    
    # Verificar si el constraint ya existe
    constraints = [c['name'] for c in inspector.get_check_constraints('reserva', schema='vecindapp')]
    
    # Agregar constraint para valores positivos solo si no existe
    if 'ck_reserva_valor_positivo' not in constraints:
        op.create_check_constraint(
            'ck_reserva_valor_positivo',
            'reserva',
            'valor_reserva >= 0',
            schema='vecindapp'
        )
        print("✅ Constraint ck_reserva_valor_positivo agregado")
    else:
        print("ℹ️  Constraint ck_reserva_valor_positivo ya existe")


def downgrade() -> None:
    """Downgrade schema."""
    # Eliminar constraint
    op.drop_constraint('ck_reserva_valor_positivo', 'reserva', schema='vecindapp')
    
    # Eliminar columna
    op.drop_column('reserva', 'valor_reserva', schema='vecindapp')
