"""implementar_tablas_maestras

Revision ID: d08f032c9633
Revises: 3b2e1947553a
Create Date: 2025-10-06 19:38:55.990518

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd08f032c9633'
down_revision: Union[str, Sequence[str], None] = '3b2e1947553a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    from sqlalchemy import inspect
    
    # Verificar qué tablas ya existen (idempotente)
    conn = op.get_bind()
    inspector = inspect(conn)
    tables = inspector.get_table_names(schema='vecindapp')
    
    # Crear tablas solo si no existen
    if 'estado_certificado' not in tables:
        op.create_table('estado_certificado',
        sa.Column('id_estado', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('nombre_estado', sa.Text(), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('activo', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id_estado'),
        sa.UniqueConstraint('nombre_estado'),
        schema='vecindapp'
        )
        print("✅ Tabla estado_certificado creada")
    else:
        print("ℹ️  Tabla estado_certificado ya existe")
    
    if 'estado_reserva' not in tables:
        op.create_table('estado_reserva',
        sa.Column('id_estado', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('nombre_estado', sa.Text(), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('activo', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id_estado'),
        sa.UniqueConstraint('nombre_estado'),
        schema='vecindapp'
        )
        print("✅ Tabla estado_reserva creada")
    else:
        print("ℹ️  Tabla estado_reserva ya existe")
    
    if 'motivo_solicitud' not in tables:
        op.create_table('motivo_solicitud',
        sa.Column('id_motivo', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('motivo', sa.Text(), nullable=False),
        sa.Column('grupo', sa.Text(), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('activo', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id_motivo'),
        sa.UniqueConstraint('motivo'),
        schema='vecindapp'
        )
        print("✅ Tabla motivo_solicitud creada")
    else:
        print("ℹ️  Tabla motivo_solicitud ya existe")
    
    if 'tipo_espacio' not in tables:
        op.create_table('tipo_espacio',
        sa.Column('id_tipo', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('tipo', sa.Text(), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('activo', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id_tipo'),
        sa.UniqueConstraint('tipo'),
        schema='vecindapp'
        )
        print("✅ Tabla tipo_espacio creada")
    else:
        print("ℹ️  Tabla tipo_espacio ya existe")
    
    # Poblar tablas maestras con datos iniciales (idempotente con ON CONFLICT)
    # Estados de certificado
    op.execute("""
        INSERT INTO vecindapp.estado_certificado (nombre_estado, descripcion, activo) VALUES
        ('pendiente_pago', 'Certificado pendiente de pago', true),
        ('generado', 'Certificado generado y listo', true),
        ('entregado', 'Certificado entregado al solicitante', true)
        ON CONFLICT (nombre_estado) DO NOTHING
    """)
    
    # Estados de reserva
    op.execute("""
        INSERT INTO vecindapp.estado_reserva (nombre_estado, descripcion, activo) VALUES
        ('pendiente', 'Reserva pendiente de confirmación', true),
        ('pagada', 'Reserva pagada', true),
        ('aprobada', 'Reserva aprobada por la junta', true),
        ('rechazada', 'Reserva rechazada', true),
        ('cancelada', 'Reserva cancelada', true),
        ('confirmada', 'Reserva confirmada y activa', true)
        ON CONFLICT (nombre_estado) DO NOTHING
    """)
    
    # Tipos de espacio
    op.execute("""
        INSERT INTO vecindapp.tipo_espacio (tipo, descripcion, activo) VALUES
        ('cancha', 'Cancha deportiva', true),
        ('sala', 'Sala de reuniones o eventos', true),
        ('plaza', 'Plaza o espacio al aire libre', true),
        ('otro', 'Otro tipo de espacio', true)
        ON CONFLICT (tipo) DO NOTHING
    """)
    
    # Motivos de solicitud (extraídos del frontend)
    op.execute("""
        INSERT INTO vecindapp.motivo_solicitud (motivo, grupo, descripcion, activo) VALUES
        ('Postulación a beneficios sociales (Registro Social de Hogares, subsidios habitacionales, bonos)', 'Trámites ante instituciones públicas', 'Para postular a beneficios sociales del estado', true),
        ('Procesos en municipalidades (inscripción en juntas de vecinos, becas municipales o ayudas sociales)', 'Trámites ante instituciones públicas', 'Para trámites municipales', true),
        ('Solicitudes en el SII o Tesorería para acreditar domicilio tributario', 'Trámites ante instituciones públicas', 'Para acreditar domicilio tributario', true),
        ('Juicios civiles, laborales o de familia (para demostrar residencia)', 'Procesos judiciales o notariales', 'Para procesos judiciales', true),
        ('Trámites de posesión efectiva, herencias o escrituras', 'Procesos judiciales o notariales', 'Para trámites notariales', true),
        ('Cambio de domicilio en causas judiciales', 'Procesos judiciales o notariales', 'Para cambio de domicilio judicial', true),
        ('Acreditar residencia ante el Servicio Nacional de Migraciones', 'Trámites migratorios', 'Para trámites migratorios', true),
        ('Solicitudes de permanencia definitiva, visados o nacionalización', 'Trámites migratorios', 'Para permanencia definitiva', true),
        ('Bancos o financieras (abrir cuentas, solicitar créditos)', 'Instituciones privadas', 'Para trámites bancarios', true),
        ('Aseguradoras o instituciones educativas para validar dirección', 'Instituciones privadas', 'Para validar dirección', true),
        ('Postulación a colegios con criterios de cercanía', 'Otros casos prácticos', 'Para postulación escolar', true),
        ('Contratos de arriendo o servicios básicos sin boletas propias', 'Otros casos prácticos', 'Para contratos de servicios', true)
        ON CONFLICT (motivo) DO NOTHING
    """)
    # Agregar nuevas columnas como nullable primero (idempotente)
    cert_columns = [col['name'] for col in inspector.get_columns('certificado_pedido', schema='vecindapp')]
    
    if 'id_estado' not in cert_columns:
        op.add_column('certificado_pedido', sa.Column('id_estado', sa.BigInteger(), nullable=True), schema='vecindapp')
        print("✅ Columna id_estado agregada a certificado_pedido")
    else:
        print("ℹ️  Columna id_estado ya existe en certificado_pedido")
    
    if 'id_motivo' not in cert_columns:
        op.add_column('certificado_pedido', sa.Column('id_motivo', sa.BigInteger(), nullable=True), schema='vecindapp')
        print("✅ Columna id_motivo agregada a certificado_pedido")
    else:
        print("ℹ️  Columna id_motivo ya existe en certificado_pedido")
    
    # Migrar datos existentes (solo si las columnas antiguas existen)
    # Para certificados: mapear estados existentes a nuevos IDs
    if 'estado' in cert_columns:
        try:
            op.execute("""
                UPDATE vecindapp.certificado_pedido 
                SET id_estado = (
                    CASE 
                        WHEN estado = 'iniciado' THEN 1  -- pendiente_pago
                        WHEN estado = 'pendiente_pago' THEN 1  -- pendiente_pago
                        WHEN estado = 'emitido' THEN 2  -- generado
                        WHEN estado = 'rechazado' THEN 1  -- pendiente_pago (por defecto)
                        ELSE 1  -- pendiente_pago por defecto
                    END
                )
                WHERE id_estado IS NULL
            """)
            print("✅ Datos de estado migrados a id_estado en certificado_pedido")
        except Exception as e:
            print(f"ℹ️  No se pudieron migrar datos de estado (puede que ya estén migrados): {e}")
    else:
        print("ℹ️  Columna estado no existe, datos ya migrados o no hay datos que migrar")
    
    # Para motivos: crear un motivo genérico para datos existentes
    op.execute("""
        INSERT INTO vecindapp.motivo_solicitud (motivo, grupo, descripcion, activo) 
        VALUES ('Motivo no especificado', 'Otros casos prácticos', 'Motivo de solicitud previo a la implementación de catálogo', true)
        ON CONFLICT (motivo) DO NOTHING
    """)
    
    if 'motivo_solicitud' in cert_columns:
        try:
            op.execute("""
                UPDATE vecindapp.certificado_pedido 
                SET id_motivo = (SELECT id_motivo FROM vecindapp.motivo_solicitud WHERE motivo = 'Motivo no especificado')
                WHERE motivo_solicitud IS NOT NULL AND id_motivo IS NULL
            """)
            print("✅ Datos de motivo_solicitud migrados a id_motivo en certificado_pedido")
        except Exception as e:
            print(f"ℹ️  No se pudieron migrar datos de motivo_solicitud (puede que ya estén migrados): {e}")
    else:
        print("ℹ️  Columna motivo_solicitud no existe, datos ya migrados o no hay datos que migrar")
    
    # Hacer las columnas NOT NULL después de migrar (solo si no son ya NOT NULL)
    cert_columns_info = {col['name']: col for col in inspector.get_columns('certificado_pedido', schema='vecindapp')}
    
    if 'id_estado' in cert_columns_info and cert_columns_info['id_estado'].get('nullable', True):
        op.alter_column('certificado_pedido', 'id_estado', nullable=False, schema='vecindapp')
        print("✅ Columna id_estado cambiada a NOT NULL")
    
    if 'id_motivo' in cert_columns_info and cert_columns_info['id_motivo'].get('nullable', True):
        op.alter_column('certificado_pedido', 'id_motivo', nullable=False, schema='vecindapp')
        print("✅ Columna id_motivo cambiada a NOT NULL")
    # Alter column solo si es necesario (idempotente)
    if 'valor_certificado' in cert_columns_info:
        try:
            op.alter_column('certificado_pedido', 'valor_certificado',
                       existing_type=sa.NUMERIC(precision=10, scale=2),
                       server_default=None,
                       existing_nullable=False,
                       schema='vecindapp')
        except Exception as e:
            print(f"ℹ️  No se pudo alterar valor_certificado (puede que ya esté configurado): {e}")
    
    # Drop y create index (idempotente)
    indexes = [idx['name'] for idx in inspector.get_indexes('certificado_pedido', schema='vecindapp')]
    if 'ix_cert_pedido_estado' in indexes:
        try:
            op.drop_index('ix_cert_pedido_estado', table_name='certificado_pedido', schema='vecindapp')
        except Exception:
            pass  # Puede que el índice ya no exista o tenga otro nombre
    
    # Verificar si el nuevo índice ya existe
    if 'ix_cert_pedido_estado' not in indexes or True:  # Siempre crear el nuevo índice
        try:
            op.create_index('ix_cert_pedido_estado', 'certificado_pedido', ['id_junta', 'id_estado'], unique=False, schema='vecindapp')
            print("✅ Índice ix_cert_pedido_estado creado")
        except Exception as e:
            print(f"ℹ️  Índice ix_cert_pedido_estado ya existe o no se pudo crear: {e}")
    
    # Crear foreign keys (idempotente)
    cert_fks = inspector.get_foreign_keys('certificado_pedido', schema='vecindapp')
    has_fk_estado = any(fk.get('referred_table') == 'estado_certificado' for fk in cert_fks)
    has_fk_motivo = any(fk.get('referred_table') == 'motivo_solicitud' for fk in cert_fks)
    
    if not has_fk_estado:
        try:
            op.create_foreign_key('fk_cert_pedido_estado', 'certificado_pedido', 'estado_certificado', ['id_estado'], ['id_estado'], source_schema='vecindapp', referent_schema='vecindapp', ondelete='RESTRICT')
            print("✅ Foreign key a estado_certificado creada")
        except Exception as e:
            print(f"ℹ️  Foreign key a estado_certificado ya existe o no se pudo crear: {e}")
    else:
        print("ℹ️  Foreign key a estado_certificado ya existe")
    
    if not has_fk_motivo:
        try:
            op.create_foreign_key('fk_cert_pedido_motivo', 'certificado_pedido', 'motivo_solicitud', ['id_motivo'], ['id_motivo'], source_schema='vecindapp', referent_schema='vecindapp', ondelete='RESTRICT')
            print("✅ Foreign key a motivo_solicitud creada")
        except Exception as e:
            print(f"ℹ️  Foreign key a motivo_solicitud ya existe o no se pudo crear: {e}")
    else:
        print("ℹ️  Foreign key a motivo_solicitud ya existe")
    
    # Drop columns solo si existen (idempotente)
    if 'estado' in cert_columns:
        try:
            op.drop_column('certificado_pedido', 'estado', schema='vecindapp')
            print("✅ Columna estado eliminada de certificado_pedido")
        except Exception as e:
            print(f"ℹ️  No se pudo eliminar columna estado: {e}")
    
    if 'motivo_solicitud' in cert_columns:
        try:
            op.drop_column('certificado_pedido', 'motivo_solicitud', schema='vecindapp')
            print("✅ Columna motivo_solicitud eliminada de certificado_pedido")
        except Exception as e:
            print(f"ℹ️  No se pudo eliminar columna motivo_solicitud: {e}")
    # Agregar nueva columna como nullable primero (idempotente)
    espacio_columns = [col['name'] for col in inspector.get_columns('espacio', schema='vecindapp')]
    
    if 'id_tipo' not in espacio_columns:
        op.add_column('espacio', sa.Column('id_tipo', sa.BigInteger(), nullable=True), schema='vecindapp')
        print("✅ Columna id_tipo agregada a espacio")
    else:
        print("ℹ️  Columna id_tipo ya existe en espacio")
    
    # Migrar tipos de espacio existentes (solo si la columna tipo existe)
    if 'tipo' in espacio_columns:
        try:
            op.execute("""
                UPDATE vecindapp.espacio 
                SET id_tipo = (
                    CASE 
                        WHEN tipo = 'cancha' THEN 1
                        WHEN tipo = 'sala' THEN 2
                        WHEN tipo = 'plaza' THEN 3
                        WHEN tipo = 'otro' THEN 4
                        ELSE 4  -- otro por defecto
                    END
                )
                WHERE id_tipo IS NULL
            """)
            print("✅ Datos de tipo migrados a id_tipo en espacio")
        except Exception as e:
            print(f"ℹ️  No se pudieron migrar datos de tipo (puede que ya estén migrados): {e}")
    else:
        print("ℹ️  Columna tipo no existe, datos ya migrados o no hay datos que migrar")
    
    # Hacer la columna NOT NULL después de migrar (solo si no es ya NOT NULL)
    espacio_columns_info = {col['name']: col for col in inspector.get_columns('espacio', schema='vecindapp')}
    
    if 'id_tipo' in espacio_columns_info and espacio_columns_info['id_tipo'].get('nullable', True):
        op.alter_column('espacio', 'id_tipo', nullable=False, schema='vecindapp')
        print("✅ Columna id_tipo cambiada a NOT NULL en espacio")
    # Crear foreign key (idempotente)
    espacio_fks = inspector.get_foreign_keys('espacio', schema='vecindapp')
    has_fk_tipo = any(fk.get('referred_table') == 'tipo_espacio' for fk in espacio_fks)
    
    if not has_fk_tipo:
        try:
            op.create_foreign_key('fk_espacio_tipo', 'espacio', 'tipo_espacio', ['id_tipo'], ['id_tipo'], source_schema='vecindapp', referent_schema='vecindapp', ondelete='RESTRICT')
            print("✅ Foreign key a tipo_espacio creada en espacio")
        except Exception as e:
            print(f"ℹ️  Foreign key a tipo_espacio ya existe o no se pudo crear: {e}")
    else:
        print("ℹ️  Foreign key a tipo_espacio ya existe")
    
    # Drop column solo si existe (idempotente)
    if 'tipo' in espacio_columns:
        try:
            op.drop_column('espacio', 'tipo', schema='vecindapp')
            print("✅ Columna tipo eliminada de espacio")
        except Exception as e:
            print(f"ℹ️  No se pudo eliminar columna tipo: {e}")
    # Agregar nueva columna como nullable primero (idempotente)
    reserva_columns = [col['name'] for col in inspector.get_columns('reserva', schema='vecindapp')]
    
    if 'id_estado' not in reserva_columns:
        op.add_column('reserva', sa.Column('id_estado', sa.BigInteger(), nullable=True), schema='vecindapp')
        print("✅ Columna id_estado agregada a reserva")
    else:
        print("ℹ️  Columna id_estado ya existe en reserva")
    
    # Migrar estados de reserva existentes (solo si la columna estado existe)
    if 'estado' in reserva_columns:
        try:
            op.execute("""
                UPDATE vecindapp.reserva 
                SET id_estado = (
                    CASE 
                        WHEN estado = 'pendiente' THEN 1
                        WHEN estado = 'pagada' THEN 2
                        WHEN estado = 'aprobada' THEN 3
                        WHEN estado = 'rechazada' THEN 4
                        WHEN estado = 'cancelada' THEN 5
                        WHEN estado = 'confirmada' THEN 6
                        ELSE 1  -- pendiente por defecto
                    END
                )
                WHERE id_estado IS NULL
            """)
            print("✅ Datos de estado migrados a id_estado en reserva")
        except Exception as e:
            print(f"ℹ️  No se pudieron migrar datos de estado (puede que ya estén migrados): {e}")
    else:
        print("ℹ️  Columna estado no existe, datos ya migrados o no hay datos que migrar")
    
    # Hacer la columna NOT NULL después de migrar (solo si no es ya NOT NULL)
    reserva_columns_info = {col['name']: col for col in inspector.get_columns('reserva', schema='vecindapp')}
    
    if 'id_estado' in reserva_columns_info and reserva_columns_info['id_estado'].get('nullable', True):
        op.alter_column('reserva', 'id_estado', nullable=False, schema='vecindapp')
        print("✅ Columna id_estado cambiada a NOT NULL en reserva")
    # Alter column solo si es necesario (idempotente)
    if 'valor_reserva' in reserva_columns_info:
        try:
            op.alter_column('reserva', 'valor_reserva',
                       existing_type=sa.NUMERIC(precision=10, scale=2),
                       server_default=None,
                       existing_nullable=False,
                       schema='vecindapp')
        except Exception as e:
            print(f"ℹ️  No se pudo alterar valor_reserva (puede que ya esté configurado): {e}")
    
    # Drop y create index (idempotente)
    reserva_indexes = [idx['name'] for idx in inspector.get_indexes('reserva', schema='vecindapp')]
    if 'ix_reserva_estado' in reserva_indexes:
        try:
            op.drop_index('ix_reserva_estado', table_name='reserva', schema='vecindapp')
        except Exception:
            pass  # Puede que el índice ya no exista o tenga otro nombre
    
    # Verificar si el nuevo índice ya existe
    if 'ix_reserva_estado' not in reserva_indexes or True:  # Siempre crear el nuevo índice
        try:
            op.create_index('ix_reserva_estado', 'reserva', ['id_junta', 'id_estado'], unique=False, schema='vecindapp')
            print("✅ Índice ix_reserva_estado creado")
        except Exception as e:
            print(f"ℹ️  Índice ix_reserva_estado ya existe o no se pudo crear: {e}")
    
    # Crear foreign key (idempotente)
    reserva_fks = inspector.get_foreign_keys('reserva', schema='vecindapp')
    has_fk_reserva_estado = any(fk.get('referred_table') == 'estado_reserva' for fk in reserva_fks)
    
    if not has_fk_reserva_estado:
        try:
            op.create_foreign_key('fk_reserva_estado', 'reserva', 'estado_reserva', ['id_estado'], ['id_estado'], source_schema='vecindapp', referent_schema='vecindapp', ondelete='RESTRICT')
            print("✅ Foreign key a estado_reserva creada en reserva")
        except Exception as e:
            print(f"ℹ️  Foreign key a estado_reserva ya existe o no se pudo crear: {e}")
    else:
        print("ℹ️  Foreign key a estado_reserva ya existe")
    
    # Drop column solo si existe (idempotente)
    if 'estado' in reserva_columns:
        try:
            op.drop_column('reserva', 'estado', schema='vecindapp')
            print("✅ Columna estado eliminada de reserva")
        except Exception as e:
            print(f"ℹ️  No se pudo eliminar columna estado: {e}")
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('reserva', sa.Column('estado', sa.TEXT(), autoincrement=False, nullable=False), schema='vecindapp')
    op.drop_constraint(None, 'reserva', schema='vecindapp', type_='foreignkey')
    op.drop_index('ix_reserva_estado', table_name='reserva', schema='vecindapp')
    op.create_index(op.f('ix_reserva_estado'), 'reserva', ['id_junta', 'estado'], unique=False, schema='vecindapp')
    op.alter_column('reserva', 'valor_reserva',
               existing_type=sa.NUMERIC(precision=10, scale=2),
               server_default=sa.text('0.00'),
               existing_nullable=False,
               schema='vecindapp')
    op.drop_column('reserva', 'id_estado', schema='vecindapp')
    op.add_column('espacio', sa.Column('tipo', sa.TEXT(), autoincrement=False, nullable=False), schema='vecindapp')
    op.drop_constraint(None, 'espacio', schema='vecindapp', type_='foreignkey')
    op.drop_column('espacio', 'id_tipo', schema='vecindapp')
    op.add_column('certificado_pedido', sa.Column('motivo_solicitud', sa.TEXT(), autoincrement=False, nullable=True), schema='vecindapp')
    op.add_column('certificado_pedido', sa.Column('estado', sa.TEXT(), autoincrement=False, nullable=False), schema='vecindapp')
    op.drop_constraint(None, 'certificado_pedido', schema='vecindapp', type_='foreignkey')
    op.drop_constraint(None, 'certificado_pedido', schema='vecindapp', type_='foreignkey')
    op.drop_index('ix_cert_pedido_estado', table_name='certificado_pedido', schema='vecindapp')
    op.create_index(op.f('ix_cert_pedido_estado'), 'certificado_pedido', ['id_junta', 'estado'], unique=False, schema='vecindapp')
    op.alter_column('certificado_pedido', 'valor_certificado',
               existing_type=sa.NUMERIC(precision=10, scale=2),
               server_default=sa.text('2000.00'),
               existing_nullable=False,
               schema='vecindapp')
    op.drop_column('certificado_pedido', 'id_motivo', schema='vecindapp')
    op.drop_column('certificado_pedido', 'id_estado', schema='vecindapp')
    op.drop_table('tipo_espacio', schema='vecindapp')
    op.drop_table('motivo_solicitud', schema='vecindapp')
    op.drop_table('estado_reserva', schema='vecindapp')
    op.drop_table('estado_certificado', schema='vecindapp')
    # ### end Alembic commands ###
