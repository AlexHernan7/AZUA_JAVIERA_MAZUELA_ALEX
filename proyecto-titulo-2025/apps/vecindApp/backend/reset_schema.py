#!/usr/bin/env python3
"""
Script simple para resetear el esquema vecindapp y recrearlo.
"""

import asyncio
import sys
import os
from pathlib import Path

# Agregar el directorio src al path para importar módulos
sys.path.append(str(Path(__file__).parent / "src"))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from src.database.session import get_transaction_session, engine
from src.database import Base
from src.database.models import *  # Importar todos los modelos


async def reset_schema():
    """Elimina el esquema vecindapp y lo recrea con todas las tablas."""
    print("Reseteando esquema vecindapp...")
    
    async with get_transaction_session() as session:
        try:
            # 1. Eliminar esquema completo (esto elimina todas las tablas)
            print("Eliminando esquema vecindapp...")
            await session.execute(text('DROP SCHEMA IF EXISTS "vecindapp" CASCADE;'))
            print("Esquema eliminado")
            
            # 2. Crear esquema nuevamente
            print("Creando esquema vecindapp...")
            await session.execute(text('CREATE SCHEMA "vecindapp";'))
            print("Esquema creado")
            
            await session.commit()
            
        except Exception as e:
            await session.rollback()
            print(f"Error reseteando esquema: {e}")
            raise
    
    # 3. Crear todas las tablas usando SQLAlchemy
    print("Creando todas las tablas...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Todas las tablas creadas")
    except Exception as e:
        print(f"Error creando tablas: {e}")
        raise


async def main():
    """Función principal."""
    try:
        print("RESET DE ESQUEMA - VECINDAPP")
        print("=" * 40)
        print()
        
        await reset_schema()
        
        print()
        print("Reset completado exitosamente!")
        print("Ahora ejecuta: python create_initial_data.py")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Verificar que estamos en el directorio correcto
    if not os.path.exists("src"):
        print("Error: Este script debe ejecutarse desde el directorio backend/")
        print("Ejecuta: cd apps/vecindApp/backend && python reset_schema.py")
        sys.exit(1)
    
    asyncio.run(main())
