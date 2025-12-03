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
    from sqlalchemy import inspect
    
    # Verificar si la columna ya existe (idempotente)
    conn = op.get_bind()
    inspector = inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('certificado_pedido', schema='vecindapp')]
    
    # Agregar columna valor_certificado solo si no existe
    if 'valor_certificado' not in columns:
        op.add_column('certificado_pedido', 
                      sa.Column('valor_certificado', sa.Numeric(10, 2), nullable=False, server_default='2000.00'),
                      schema='vecindapp')
        print("✅ Columna valor_certificado agregada")
    else:
        print("ℹ️  Columna valor_certificado ya existe")
    
    # Verificar si el constraint ya existe
    constraints = [c['name'] for c in inspector.get_check_constraints('certificado_pedido', schema='vecindapp')]
    
    # Agregar constraint para valores positivos solo si no existe
    if 'ck_cert_pedido_valor_positivo' not in constraints:
        op.create_check_constraint(
            'ck_cert_pedido_valor_positivo',
            'certificado_pedido',
            'valor_certificado > 0',
            schema='vecindapp'
        )
        print("✅ Constraint ck_cert_pedido_valor_positivo agregado")
    else:
        print("ℹ️  Constraint ck_cert_pedido_valor_positivo ya existe")


def downgrade() -> None:
    """Downgrade schema."""
    # Eliminar constraint
    op.drop_constraint('ck_cert_pedido_valor_positivo', 'certificado_pedido', schema='vecindapp')
    
    # Eliminar columna
    op.drop_column('certificado_pedido', 'valor_certificado', schema='vecindapp')
