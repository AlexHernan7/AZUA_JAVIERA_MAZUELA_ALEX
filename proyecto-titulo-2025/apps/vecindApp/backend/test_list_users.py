#!/usr/bin/env python3
"""
Script para listar usuarios existentes en la base de datos
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from src.database.models.usuario import Usuario
from src.database.models.vecino import Vecino
from src.core.config import get_settings

async def list_users():
    print("👥 Listando usuarios existentes...")
    
    settings = get_settings()
    
    # Crear engine y sesión
    engine = create_async_engine(
        settings.database.async_url,
        echo=False
    )
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            # Obtener usuarios con sus vecinos
            result = await session.execute(
                select(Usuario, Vecino)
                .outerjoin(Vecino, Usuario.id_usuario == Vecino.id_usuario)
                .limit(10)
            )
            
            users_data = result.all()
            
            if not users_data:
                print("❌ No se encontraron usuarios en la base de datos")
                return
            
            print(f"📋 Encontrados {len(users_data)} usuarios:")
            print("-" * 80)
            
            for usuario, vecino in users_data:
                print(f"📧 Email: {usuario.email}")
                print(f"🆔 ID: {usuario.id_usuario}")
                # print(f"👤 Tipo: {usuario.user_type}")  # Comentado por error
                if vecino:
                    print(f"🏠 Vecino: {vecino.nombres} {vecino.apellido_paterno}")
                    print(f"📍 RUT: {vecino.rut}")
                else:
                    print("🏠 Sin perfil de vecino")
                print("-" * 40)
                
        except Exception as e:
            print(f"💥 Error consultando usuarios: {str(e)}")
        finally:
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(list_users())
