#!/usr/bin/env python3
"""
Script completo para resetear la base de datos y cargar datos iniciales.
"""

import asyncio
import sys
import os
from pathlib import Path

# Agregar el directorio src al path para importar módulos
sys.path.append(str(Path(__file__).parent / "src"))

from reset_schema import reset_schema
from create_initial_data import create_initial_data


async def reset_database():
    """Función principal que ejecuta todo el proceso de reset."""
    print("Iniciando reset completo de la base de datos...")
    print("ADVERTENCIA: Este proceso eliminará TODOS los datos existentes!")
    print()
    
    try:
        # Paso 1: Resetear esquema y crear tablas
        await reset_schema()
        print()
        
        # Paso 2: Cargar datos iniciales
        print("Cargando datos iniciales...")
        await create_initial_data()
        print()
        
        print("Reset de base de datos completado exitosamente!")
        print()
        print("Credenciales de acceso:")
        print("   Email: admin@admin.cl")
        print("   Contraseña: admin")
        print()
        print("El sistema está listo para usar!")
        
    except Exception as e:
        print(f"Error durante el reset de la base de datos: {e}")
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
    print("=" * 60)
    print("RESET COMPLETO DE BASE DE DATOS - VECINDAPP")
    print("=" * 60)
    print()
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists("src"):
        print("Error: Este script debe ejecutarse desde el directorio backend/")
        print("Directorio actual:", os.getcwd())
        print("Ejecuta: cd apps/vecindApp/backend && python reset_database.py")
        sys.exit(1)
    
    asyncio.run(main())
