"""
Script para verificar y ajustar el estado de Alembic.
Si las tablas ya existen pero Alembic no tiene registro, marca la migración inicial como ejecutada.
"""

from sqlalchemy import create_engine, text, inspect
from src.core.config import settings


def check_and_fix_alembic_state():
    """Verifica el estado de Alembic y lo ajusta si es necesario."""
    
    engine = create_engine(settings.database.sync_url)
    
    try:
        with engine.connect() as conn:
            print("=" * 60)
            print("VERIFICANDO ESTADO DE ALEMBIC")
            print("=" * 60)
            
            # Verificar si existe la tabla alembic_version
            inspector = inspect(engine)
            tables = inspector.get_table_names(schema='vecindapp')
            
            # Verificar alembic_version en el schema vecindapp
            has_alembic_version = False
            try:
                alembic_tables = inspector.get_table_names(schema='vecindapp')
                has_alembic_version = 'alembic_version' in alembic_tables
            except:
                pass
            
            # También verificar en el schema público
            if not has_alembic_version:
                try:
                    public_tables = inspector.get_table_names(schema='public')
                    has_alembic_version = 'alembic_version' in public_tables
                except:
                    pass
            
            # Verificar si existe la tabla region (indicador de que las tablas ya fueron creadas)
            has_region = 'region' in tables
            
            print(f"\nTablas encontradas en schema vecindapp: {len(tables)}")
            print(f"Tabla alembic_version existe: {has_alembic_version}")
            print(f"Tabla region existe: {has_region}")
            
            # Si las tablas existen pero Alembic no tiene registro, marcar migración inicial
            if has_region and not has_alembic_version:
                print("\n⚠️  Las tablas existen pero Alembic no tiene registro")
                print("📝 Marcando migración inicial como ejecutada...")
                
                # Intentar crear tabla alembic_version en vecindapp primero
                try:
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS vecindapp.alembic_version (
                            version_num VARCHAR(32) NOT NULL,
                            CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
                        )
                    """))
                    conn.commit()
                    
                    # Insertar la migración inicial
                    conn.execute(text("""
                        INSERT INTO vecindapp.alembic_version (version_num)
                        VALUES ('371433ac8f3c')
                        ON CONFLICT (version_num) DO NOTHING
                    """))
                    conn.commit()
                    print("✅ Migración inicial marcada como ejecutada en schema vecindapp")
                except Exception as e:
                    # Si falla, intentar en schema público
                    print(f"⚠️  Error en vecindapp, intentando en schema público: {e}")
                    try:
                        conn.execute(text("""
                            CREATE TABLE IF NOT EXISTS alembic_version (
                                version_num VARCHAR(32) NOT NULL,
                                CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
                            )
                        """))
                        conn.commit()
                        
                        conn.execute(text("""
                            INSERT INTO alembic_version (version_num)
                            VALUES ('371433ac8f3c')
                            ON CONFLICT (version_num) DO NOTHING
                        """))
                        conn.commit()
                        print("✅ Migración inicial marcada como ejecutada en schema público")
                    except Exception as e2:
                        print(f"❌ Error al crear alembic_version: {e2}")
            elif has_region and has_alembic_version:
                # Verificar qué versión está registrada
                try:
                    result = conn.execute(text("SELECT version_num FROM vecindapp.alembic_version"))
                    version = result.scalar()
                    if version:
                        print(f"\n✅ Alembic tiene registro en vecindapp: versión {version}")
                    else:
                        result = conn.execute(text("SELECT version_num FROM alembic_version"))
                        version = result.scalar()
                        print(f"\n✅ Alembic tiene registro en público: versión {version}")
                except:
                    print("\n✅ Alembic tiene registro (no se pudo leer la versión)")
            else:
                print("\nℹ️  Base de datos nueva, Alembic creará las tablas")
            
            print("\n" + "=" * 60)
            print("✅ VERIFICACIÓN COMPLETADA")
            print("=" * 60)
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        # No lanzar excepción, solo registrar el error
        import traceback
        traceback.print_exc()
    finally:
        engine.dispose()


if __name__ == "__main__":
    print("\n🚀 Verificando estado de Alembic...\n")
    check_and_fix_alembic_state()

