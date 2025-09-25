"""Crea datos iniciales en la base de datos."""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from src.database.session import get_transaction_session


async def create_initial_data():
    """Crea datos base: región, comuna, juntas y roles."""
    
    async with get_transaction_session() as session:
        try:
            print("🔧 Creando datos iniciales...")
            
            # 1. Crear Región Metropolitana
            # Verificar si ya existe
            result = await session.execute(text("""
                SELECT id_region FROM "vecindapp".region 
                WHERE nombre = 'Región Metropolitana de Santiago'
            """))
            existing_region = result.scalar()
            
            if not existing_region:
                await session.execute(text("""
                    INSERT INTO "vecindapp".region (nombre) 
                    VALUES ('Región Metropolitana de Santiago')
                """))
            
            # Obtener ID de la región
            result = await session.execute(text("""
                SELECT id_region FROM "vecindapp".region 
                WHERE nombre = 'Región Metropolitana de Santiago'
            """))
            id_region = result.scalar()
            print(f"✅ Región: Región Metropolitana (ID: {id_region})")
            
            # 2. Crear Comuna de Maipú
            # Verificar si ya existe
            result = await session.execute(text("""
                SELECT id_comuna FROM "vecindapp".comuna 
                WHERE nombre = 'Maipú' AND id_region = :id_region
            """), {"id_region": id_region})
            existing_comuna = result.scalar()
            
            if not existing_comuna:
                await session.execute(text("""
                    INSERT INTO "vecindapp".comuna (id_region, nombre) 
                    VALUES (:id_region, 'Maipú')
                """), {"id_region": id_region})
            
            # Obtener ID de la comuna
            result = await session.execute(text("""
                SELECT id_comuna FROM "vecindapp".comuna 
                WHERE nombre = 'Maipú' AND id_region = :id_region
            """), {"id_region": id_region})
            id_comuna = result.scalar()
            print(f"✅ Comuna: Maipú (ID: {id_comuna})")
            
            # 3. Crear juntas de ejemplo
            juntas = [
                ("Junta de Vecinos Barrio Oeste", "65123456-7", "Av. Siempre Viva 1234, Maipú", "+56987654321", "contacto@juntabarrioeste.cl", "Junta de vecinos del Barrio Oeste"),
                ("Junta de Vecinos Las Américas", "65234567-8", "Las Américas 200, Maipú", "+56228905678", "info@lasamericas.cl", "Junta de vecinos del sector Las Américas"),
                ("Junta de Vecinos Central Maipú", "65345678-9", "Av. Pajaritos 300, Maipú", "+56228909012", "central@maipu.cl", "Junta de vecinos del centro de Maipú")
            ]
            
            for nombre, rut, direccion, telefono, email, descripcion in juntas:
                # Verificar si ya existe
                result = await session.execute(text("""
                    SELECT id_junta FROM "vecindapp".junta 
                    WHERE nombre = :nombre AND id_comuna = :id_comuna
                """), {"nombre": nombre, "id_comuna": id_comuna})
                existing_junta = result.scalar()
                
                if not existing_junta:
                    await session.execute(text("""
                        INSERT INTO "vecindapp".junta (id_comuna, nombre, rut, direccion, telefono, email, descripcion) 
                        VALUES (:id_comuna, :nombre, :rut, :direccion, :telefono, :email, :descripcion)
                    """), {
                        "id_comuna": id_comuna,
                        "nombre": nombre,
                        "rut": rut,
                        "direccion": direccion,
                        "telefono": telefono,
                        "email": email,
                        "descripcion": descripcion
                    })
                    print(f"✅ Junta creada: {nombre} (RUT: {rut})")
                else:
                    print(f"ℹ️  Junta ya existe: {nombre}")
            
            # 4. Crear roles del sistema
            roles = [
                ("vecino", "Vecino", "Rol básico para vecinos registrados"),
                ("directiva", "Directiva", "Miembro de la directiva de la junta"),
                ("admin", "Administrador", "Administrador del sistema")
            ]
            
            for codigo, nombre, descripcion in roles:
                # Verificar si ya existe
                result = await session.execute(text("""
                    SELECT id_rol FROM "vecindapp".rol 
                    WHERE codigo = :codigo
                """), {"codigo": codigo})
                existing_rol = result.scalar()
                
                if not existing_rol:
                    await session.execute(text("""
                        INSERT INTO "vecindapp".rol (codigo, nombre, descripcion) 
                        VALUES (:codigo, :nombre, :descripcion)
                    """), {
                        "codigo": codigo,
                        "nombre": nombre,
                        "descripcion": descripcion
                    })
                    print(f"✅ Rol creado: {nombre} (código: {codigo})")
                else:
                    print(f"ℹ️  Rol ya existe: {nombre} (código: {codigo})")
            
            # 6. Crear usuario administrador
            from src.core.security import hash_password
            
            admin_password_hash = hash_password("admin")
            
            # Verificar si ya existe el usuario admin
            result = await session.execute(text("""
                SELECT id_usuario FROM "vecindapp".usuario 
                WHERE email = 'admin@admin.cl'
            """))
            existing_admin = result.scalar()
            
            if not existing_admin:
                # Crear usuario admin (sin junta específica, es administrador global)
                await session.execute(text("""
                    INSERT INTO "vecindapp".usuario (email, pass_hash, activo) 
                    VALUES ('admin@admin.cl', :password_hash, true)
                """), {"password_hash": admin_password_hash})
                
                # Obtener el ID del usuario recién creado
                result = await session.execute(text("""
                    SELECT id_usuario FROM "vecindapp".usuario 
                    WHERE email = 'admin@admin.cl'
                """))
                admin_user_id = result.scalar()
                
                # Obtener el ID del rol admin
                result = await session.execute(text("""
                    SELECT id_rol FROM "vecindapp".rol 
                    WHERE codigo = 'admin'
                """))
                admin_role_id = result.scalar()
                
                # Asignar rol admin al usuario
                await session.execute(text("""
                    INSERT INTO "vecindapp".usuario_rol (id_usuario, id_rol) 
                    VALUES (:id_usuario, :id_rol)
                """), {
                    "id_usuario": admin_user_id,
                    "id_rol": admin_role_id
                })
                
                print(f"✅ Usuario administrador creado: admin@admin.cl")
            else:
                print(f"ℹ️  Usuario administrador ya existe: admin@admin.cl")
            
            # Confirmar todos los cambios
            await session.commit()
            print("\n🎉 ¡Datos iniciales creados exitosamente!")
            
            # Mostrar resumen con IDs reales
            result = await session.execute(text("SELECT COUNT(*) FROM \"vecindapp\".junta WHERE id_comuna = :id_comuna"), {"id_comuna": id_comuna})
            total_juntas = result.scalar()
            
            print("\n📋 RESUMEN:")
            print(f"- 1 Región: Región Metropolitana (ID: {id_region})")
            print(f"- 1 Comuna: Maipú (ID: {id_comuna})")
            print(f"- {total_juntas} Juntas de vecinos en Maipú")
            print(f"- 3 Roles: vecino, directiva, admin")
            print(f"- 1 Usuario administrador: admin@admin.cl")
            
            print("\n🚀 Ya puedes probar el sistema!")
            print("📧 Usuario admin: admin@admin.cl")
            print("🔑 Contraseña: admin")
            print("\nDatos de prueba para registro:")
            print(f"- id_comuna: {id_comuna}")
            print("- id_junta: 1, 2 o 3 (cualquiera de las juntas creadas)")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error creando datos iniciales: {e}")
            raise


if __name__ == "__main__":
    print("🔄 Iniciando creación de datos iniciales...")
    asyncio.run(create_initial_data())
