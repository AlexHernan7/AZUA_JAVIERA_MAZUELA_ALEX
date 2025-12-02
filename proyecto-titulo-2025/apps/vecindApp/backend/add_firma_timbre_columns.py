"""
Script para agregar las columnas firma_presidente y timbre a la tabla junta.
Este script se ejecuta como respaldo si la migración de Alembic no se ejecuta correctamente.
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from src.core.config import settings


async def add_firma_timbre_columns():
    """Agrega las columnas firma_presidente y timbre si no existen."""
    
    engine = create_async_engine(settings.database.async_url)
    
    try:
        async with engine.begin() as conn:
            print("=" * 60)
            print("AGREGANDO COLUMNAS FIRMA_PRESIDENTE Y TIMBRE")
            print("=" * 60)
            
            # Verificar si las columnas ya existen
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_schema = 'vecindapp' 
                AND table_name = 'junta' 
                AND column_name IN ('firma_presidente', 'timbre')
            """)
            
            result = await conn.execute(check_query)
            existing_columns = [row[0] for row in result.fetchall()]
            
            print(f"\nColumnas existentes: {existing_columns}")
            
            # Agregar firma_presidente si no existe
            if 'firma_presidente' not in existing_columns:
                print("\n[1/2] Agregando columna firma_presidente...")
                await conn.execute(text("""
                    ALTER TABLE vecindapp.junta 
                    ADD COLUMN firma_presidente BYTEA
                """))
                print("✅ Columna firma_presidente agregada")
            else:
                print("ℹ️  Columna firma_presidente ya existe")
            
            # Agregar timbre si no existe
            if 'timbre' not in existing_columns:
                print("\n[2/2] Agregando columna timbre...")
                await conn.execute(text("""
                    ALTER TABLE vecindapp.junta 
                    ADD COLUMN timbre BYTEA
                """))
                print("✅ Columna timbre agregada")
            else:
                print("ℹ️  Columna timbre ya existe")
            
            print("\n" + "=" * 60)
            print("✅ PROCESO COMPLETADO")
            print("=" * 60)
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    print("\n🚀 Iniciando script de agregado de columnas...\n")
    asyncio.run(add_firma_timbre_columns())

