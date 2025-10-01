"""extender_espacio_con_campos_completos

Revision ID: extender_espacio_001
Revises: ddacb33eebe2
Create Date: 2025-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'extender_espacio_001'
down_revision: Union[str, Sequence[str], None] = 'ddacb33eebe2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Agregar nuevas columnas a la tabla espacio
    op.add_column('espacio', sa.Column('valor', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0'), schema='vecindapp')
    op.add_column('espacio', sa.Column('foto', sa.Text(), nullable=True), schema='vecindapp')
    op.add_column('espacio', sa.Column('permitido', postgresql.ARRAY(sa.Text()), nullable=True), schema='vecindapp')
    op.add_column('espacio', sa.Column('no_permitido', postgresql.ARRAY(sa.Text()), nullable=True), schema='vecindapp')
    op.add_column('espacio', sa.Column('max_horas', sa.Integer(), nullable=False, server_default='4'), schema='vecindapp')
    
    # Hacer capacidad no nullable
    op.alter_column('espacio', 'capacidad', nullable=False, schema='vecindapp')
    
    # Agregar constraints
    op.create_check_constraint('ck_espacio_valor_positivo', 'espacio', 'valor >= 0', schema='vecindapp')
    op.create_check_constraint('ck_espacio_capacidad_positiva', 'espacio', 'capacidad > 0', schema='vecindapp')
    op.create_check_constraint('ck_espacio_max_horas_positivo', 'espacio', 'max_horas > 0', schema='vecindapp')


def downgrade() -> None:
    """Downgrade schema."""
    # Eliminar constraints
    op.drop_constraint('ck_espacio_max_horas_positivo', 'espacio', type_='check', schema='vecindapp')
    op.drop_constraint('ck_espacio_capacidad_positiva', 'espacio', type_='check', schema='vecindapp')
    op.drop_constraint('ck_espacio_valor_positivo', 'espacio', type_='check', schema='vecindapp')
    
    # Eliminar columnas agregadas
    op.drop_column('espacio', 'max_horas', schema='vecindapp')
    op.drop_column('espacio', 'no_permitido', schema='vecindapp')
    op.drop_column('espacio', 'permitido', schema='vecindapp')
    op.drop_column('espacio', 'foto', schema='vecindapp')
    op.drop_column('espacio', 'valor', schema='vecindapp')
    
    # Hacer capacidad nullable nuevamente
    op.alter_column('espacio', 'capacidad', nullable=True, schema='vecindapp')
