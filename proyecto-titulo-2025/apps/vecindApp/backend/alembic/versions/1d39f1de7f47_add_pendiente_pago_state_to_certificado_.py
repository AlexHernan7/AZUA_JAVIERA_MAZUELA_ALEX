"""Add pendiente_pago state to certificado_pedido

Revision ID: 1d39f1de7f47
Revises: ddacb33eebe2
Create Date: 2025-09-22 19:53:02.740448

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1d39f1de7f47'
down_revision: Union[str, Sequence[str], None] = 'ddacb33eebe2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Actualizar la restricción CHECK para incluir 'pendiente_pago'
    op.drop_constraint('ck_cert_pedido_estado', 'certificado_pedido', schema='vecindapp')
    op.create_check_constraint(
        'ck_cert_pedido_estado',
        'certificado_pedido',
        "estado IN ('iniciado','pendiente_pago','emitido','rechazado')",
        schema='vecindapp'
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Revertir la restricción CHECK al estado anterior
    op.drop_constraint('ck_cert_pedido_estado', 'certificado_pedido', schema='vecindapp')
    op.create_check_constraint(
        'ck_cert_pedido_estado',
        'certificado_pedido',
        "estado IN ('iniciado','emitido','rechazado')",
        schema='vecindapp'
    )
