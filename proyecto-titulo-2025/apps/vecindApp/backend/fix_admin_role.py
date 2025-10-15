"""
Script para verificar y asignar el rol admin al usuario admin@admin.cl
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from src.database.session import get_transaction_session


async def fix_admin_role():
    """Verifica y asigna el rol admin si falta."""
    
    async with get_transaction_session() as session:
        try:
            print("[INFO] Verificando usuario admin...")
            
            # 1. Verificar que existe el usuario admin
            result = await session.execute(text("""
                SELECT id_usuario FROM "vecindapp".usuario 
                WHERE email = 'admin@admin.cl'
            """))
            admin_user_id = result.scalar()
            
            if not admin_user_id:
                print("[ERROR] Usuario admin@admin.cl no existe!")
                print("   Ejecuta: poetry run python create_initial_data.py")
                return
            
            print(f"[OK] Usuario admin existe (ID: {admin_user_id})")
            
            # 2. Verificar que existe el rol admin
            result = await session.execute(text("""
                SELECT id_rol FROM "vecindapp".rol 
                WHERE codigo = 'admin'
            """))
            admin_role_id = result.scalar()
            
            if not admin_role_id:
                print("[ERROR] Rol 'admin' no existe en la base de datos!")
                print("   Ejecuta: poetry run python create_initial_data.py")
                return
            
            print(f"[OK] Rol admin existe (ID: {admin_role_id})")
            
            # 3. Verificar si el usuario tiene el rol asignado
            result = await session.execute(text("""
                SELECT ur.id_usuario, ur.id_rol 
                FROM "vecindapp".usuario_rol ur
                WHERE ur.id_usuario = :user_id AND ur.id_rol = :role_id
            """), {"user_id": admin_user_id, "role_id": admin_role_id})
            existing_assignment = result.first()
            
            if existing_assignment:
                print("[OK] El usuario admin YA TIENE el rol admin asignado correctamente")
                print(f"   usuario_id: {admin_user_id}, rol_id: {admin_role_id}")
                
                # Mostrar todos los roles del usuario
                result = await session.execute(text("""
                    SELECT r.codigo, r.nombre 
                    FROM "vecindapp".rol r
                    JOIN "vecindapp".usuario_rol ur ON r.id_rol = ur.id_rol
                    WHERE ur.id_usuario = :user_id
                """), {"user_id": admin_user_id})
                roles = result.all()
                print(f"   Roles asignados: {[r[0] for r in roles]}")
                
            else:
                print("[WARNING] El usuario admin NO tiene el rol admin asignado")
                print("   Asignando rol...")
                
                await session.execute(text("""
                    INSERT INTO "vecindapp".usuario_rol (id_usuario, id_rol) 
                    VALUES (:user_id, :role_id)
                """), {"user_id": admin_user_id, "role_id": admin_role_id})
                
                await session.commit()
                print("[OK] Rol admin asignado exitosamente!")
            
            print("\n[SUCCESS] Todo esta configurado correctamente")
            
        except Exception as e:
            await session.rollback()
            print(f"[ERROR] Error: {e}")
            raise


if __name__ == "__main__":
    print("=" * 60)
    print("Script para verificar/arreglar rol admin")
    print("=" * 60)
    asyncio.run(fix_admin_role())

