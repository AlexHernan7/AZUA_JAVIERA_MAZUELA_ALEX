#!/usr/bin/env python3
"""
Script para resetear completamente la base de datos VecindApp.

ADVERTENCIA: Este script eliminará el esquema completo y lo recreará.
Solo usar en entornos de desarrollo/pruebas.

Uso:
    poetry run python reset_database.py

Después ejecutar:
    poetry run alembic upgrade head
"""

import sys
import os
from sqlalchemy import create_engine, text
import logging

# Agregar el directorio src al path para importar módulos
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.core.config import settings

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reset_database():
    """
    Resetea completamente la base de datos eliminando y recreando el esquema.
    """
    try:
        # Crear engine de base de datos (usando URL síncrona)
        engine = create_engine(settings.database.sync_url)
        
        with engine.connect() as connection:
            # Iniciar transacción
            trans = connection.begin()
            
            try:
                logger.info("🔥 Iniciando reset completo de la base de datos...")
                
                # 1. Eliminar el esquema completo si existe
                logger.info("🗑️  Eliminando esquema 'vecindApp' si existe...")
                connection.execute(text("DROP SCHEMA IF EXISTS vecindApp CASCADE"))
                logger.info("   ✅ Esquema 'vecindApp' eliminado")
                
                # 2. Recrear el esquema
                logger.info("🏗️  Creando esquema 'vecindApp'...")
                connection.execute(text("CREATE SCHEMA vecindApp"))
                logger.info("   ✅ Esquema 'vecindApp' creado")
                
                # 3. Eliminar tabla de versiones de Alembic si existe
                logger.info("🔄 Limpiando tabla de versiones de Alembic...")
                connection.execute(text("DROP TABLE IF EXISTS alembic_version"))
                logger.info("   ✅ Tabla de versiones de Alembic eliminada")
                
                # Confirmar transacción
                trans.commit()
                logger.info("✅ ¡Reset de base de datos completado exitosamente!")
                
                # Mostrar resumen
                logger.info("\n📊 RESUMEN:")
                logger.info("- Esquema 'vecindApp' eliminado y recreado")
                logger.info("- Tabla de versiones de Alembic limpiada")
                logger.info("- La base de datos está lista para migraciones")
                
                return True
                
            except Exception as e:
                # Rollback en caso de error
                trans.rollback()
                logger.error(f"❌ Error durante el reset: {e}")
                raise
                
    except Exception as e:
        logger.error(f"💥 Error conectando a la base de datos: {e}")
        logger.error("Verifica que:")
        logger.error("1. La base de datos esté ejecutándose")
        logger.error("2. Las credenciales sean correctas")
        logger.error("3. Tengas permisos de administrador")
        return False

def confirm_reset():
    """
    Solicita confirmación del usuario antes de proceder con el reset.
    """
    print("\n" + "="*60)
    print("🚨 ADVERTENCIA: RESET COMPLETO DE BASE DE DATOS 🚨")
    print("="*60)
    print("Este script eliminará el esquema 'vecindApp' COMPLETO.")
    print("Esta acción es IRREVERSIBLE.")
    print("\nLo que se eliminará:")
    print("- TODO el esquema 'vecindApp' y todas sus tablas")
    print("- Todos los datos existentes")
    print("- Historial de migraciones de Alembic")
    print("\nLo que se creará:")
    print("- Esquema 'vecindApp' vacío")
    print("="*60)
    
    response = input("\n¿Estás seguro de que quieres continuar? (escribe 'RESET CONFIRMO' para proceder): ")
    
    if response.strip().upper() != "RESET CONFIRMO":
        print("❌ Operación cancelada por el usuario.")
        return False
    
    print("✅ Confirmación recibida. Procediendo con el reset...")
    return True

if __name__ == "__main__":
    # Solicitar confirmación
    if not confirm_reset():
        sys.exit(0)
    
    # Ejecutar reset
    if reset_database():
        print("\n🎉 ¡Reset completado!")
        print("\n📝 PRÓXIMOS PASOS:")
        print("1. Ejecuta las migraciones:")
        print("   poetry run alembic upgrade head")
        print("\n2. Si tienes datos iniciales, ejecútalos:")
        print("   poetry run python create_initial_data.py")
    else:
        print("\n❌ Reset falló. Revisa los errores anteriores.")
        sys.exit(1)
