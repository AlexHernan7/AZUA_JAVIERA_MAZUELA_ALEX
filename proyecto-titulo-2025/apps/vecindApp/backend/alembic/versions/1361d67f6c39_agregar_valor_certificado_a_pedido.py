"""agregar_valor_certificado_a_pedido

Revision ID: 1361d67f6c39
Revises: 371433ac8f3c
Create Date: 2025-10-02 18:27:00.565921

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1361d67f6c39'
down_revision: Union[str, Sequence[str], None] = '371433ac8f3c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Agregar columna valor_certificado a certificado_pedido
    op.add_column('certificado_pedido', 
                  sa.Column('valor_certificado', sa.Numeric(10, 2), nullable=False, server_default='2000.00'),
                  schema='vecindapp')
    
    # Agregar constraint para valores positivos
    op.create_check_constraint(
        'ck_cert_pedido_valor_positivo',
        'certificado_pedido',
        'valor_certificado > 0',
        schema='vecindapp'
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Eliminar constraint
    op.drop_constraint('ck_cert_pedido_valor_positivo', 'certificado_pedido', schema='vecindapp')
    
    # Eliminar columna
    op.drop_column('certificado_pedido', 'valor_certificado', schema='vecindapp')
