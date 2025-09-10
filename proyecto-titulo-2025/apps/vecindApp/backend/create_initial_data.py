"""
Script para crear datos iniciales en la base de datos.

Ejecuta este script DESPUÉS de las migraciones para tener datos base.
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from src.database.session import get_transaction_session


async def create_initial_data():
    """Crea los datos iniciales necesarios para que funcione el sistema usando SQL directo."""
    
    async with get_transaction_session() as session:
        try:
            print("🔧 Creando datos iniciales...")
            
            # 1. Crear Región Metropolitana
            await session.execute(text("""
                INSERT INTO "vecindApp".region (nombre) 
                VALUES ('Región Metropolitana de Santiago')
                ON CONFLICT (nombre) DO NOTHING
            """))
            
            # Obtener ID de la región
            result = await session.execute(text("""
                SELECT id_region FROM "vecindApp".region 
                WHERE nombre = 'Región Metropolitana de Santiago'
            """))
            id_region = result.scalar()
            print(f"✅ Región: Región Metropolitana (ID: {id_region})")
            
            # 2. Crear Comuna de Maipú
            await session.execute(text("""
                INSERT INTO "vecindApp".comuna (id_region, nombre) 
                VALUES (:id_region, 'Maipú')
                ON CONFLICT (id_region, nombre) DO NOTHING
            """), {"id_region": id_region})
            
            # Obtener ID de la comuna
            result = await session.execute(text("""
                SELECT id_comuna FROM "vecindApp".comuna 
                WHERE nombre = 'Maipú' AND id_region = :id_region
            """), {"id_region": id_region})
            id_comuna = result.scalar()
            print(f"✅ Comuna: Maipú (ID: {id_comuna})")
            
            # 3. Crear juntas de ejemplo
            juntas = [
                ("Junta de Vecinos Villa Los Aromos", "Los Aromos 100, Maipú", "+56228901234", "contacto@villalosaromos.cl", "Junta de vecinos del sector Villa Los Aromos"),
                ("Junta de Vecinos Las Américas", "Las Américas 200, Maipú", "+56228905678", "info@lasamericas.cl", "Junta de vecinos del sector Las Américas"),
                ("Junta de Vecinos Central Maipú", "Av. Pajaritos 300, Maipú", "+56228909012", "central@maipu.cl", "Junta de vecinos del centro de Maipú")
            ]
            
            for nombre, direccion, telefono, email, descripcion in juntas:
                await session.execute(text("""
                    INSERT INTO "vecindApp".junta (id_comuna, nombre, direccion, telefono, email, descripcion) 
                    VALUES (:id_comuna, :nombre, :direccion, :telefono, :email, :descripcion)
                    ON CONFLICT DO NOTHING
                """), {
                    "id_comuna": id_comuna,
                    "nombre": nombre,
                    "direccion": direccion,
                    "telefono": telefono,
                    "email": email,
                    "descripcion": descripcion
                })
                print(f"✅ Junta creada: {nombre}")
            
            # 4. Crear roles del sistema
            roles = [
                ("vecino", "Vecino", "Rol básico para vecinos registrados"),
                ("directiva", "Directiva", "Miembro de la directiva de la junta"),
                ("admin", "Administrador", "Administrador del sistema")
            ]
            
            for codigo, nombre, descripcion in roles:
                await session.execute(text("""
                    INSERT INTO "vecindApp".rol (codigo, nombre, descripcion) 
                    VALUES (:codigo, :nombre, :descripcion)
                    ON CONFLICT (codigo) DO NOTHING
                """), {
                    "codigo": codigo,
                    "nombre": nombre,
                    "descripcion": descripcion
                })
                print(f"✅ Rol creado: {nombre} (código: {codigo})")
            
            # Confirmar todos los cambios
            await session.commit()
            print("\n🎉 ¡Datos iniciales creados exitosamente!")
            
            # Mostrar resumen con IDs reales
            result = await session.execute(text("SELECT COUNT(*) FROM \"vecindApp\".junta WHERE id_comuna = :id_comuna"), {"id_comuna": id_comuna})
            total_juntas = result.scalar()
            
            print("\n📋 RESUMEN:")
            print(f"- 1 Región: Región Metropolitana (ID: {id_region})")
            print(f"- 1 Comuna: Maipú (ID: {id_comuna})")
            print(f"- {total_juntas} Juntas de vecinos en Maipú")
            print(f"- 3 Roles: vecino, directiva, admin")
            
            print("\n🚀 Ya puedes probar el endpoint de registro!")
            print("Usa estos datos de prueba:")
            print(f"- id_comuna: {id_comuna}")
            print("- id_junta: 1, 2 o 3 (cualquiera de las juntas creadas)")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error creando datos iniciales: {e}")
            raise


if __name__ == "__main__":
    print("🔄 Iniciando creación de datos iniciales...")
    asyncio.run(create_initial_data())
