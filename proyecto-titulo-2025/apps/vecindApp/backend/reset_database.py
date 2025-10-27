#!/usr/bin/env python3
"""
Script completo para resetear la base de datos y cargar datos iniciales.
"""

import asyncio
import sys
import os
from pathlib import Path

# Agregar el directorio actual y src al path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / "src"))

# Importar funciones de otros scripts
from reset_schema import reset_schema


async def reset_database():
    """Función principal que ejecuta todo el proceso de reset."""
    print("=" * 60)
    print("RESET COMPLETO DE BASE DE DATOS - VECINDAPP")
    print("=" * 60)
    print("\n⚠️  ADVERTENCIA: Este proceso eliminará TODOS los datos existentes!\n")
    
    try:
        # Paso 1: Resetear esquema (borra todo)
        print("[1/2] Eliminando esquema y tablas existentes...")
        await reset_schema()
        print("✅ Esquema eliminado\n")
        
        # Paso 2: Inicializar desde cero ejecutando el script init_database
        print("[2/2] Inicializando base de datos desde cero...\n")
        
        # Importar e ejecutar la función de init_database
        from init_database import init_database
        await init_database()
        
        print("\n" + "=" * 60)
        print("✅ RESET COMPLETADO EXITOSAMENTE")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error durante el reset de la base de datos: {e}")
        raise


async def main():
    """Función principal con manejo de errores."""
    try:
        await reset_database()
    except KeyboardInterrupt:
        print("\nProceso cancelado por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\nError fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Verificar que estamos en el directorio correcto
    if not os.path.exists("src"):
        print("❌ Error: Este script debe ejecutarse desde el directorio backend/")
        print(f"   Directorio actual: {os.getcwd()}")
        print("   Ejecuta: cd apps/vecindApp/backend && poetry run python reset_database.py")
        sys.exit(1)
    
    asyncio.run(main())
