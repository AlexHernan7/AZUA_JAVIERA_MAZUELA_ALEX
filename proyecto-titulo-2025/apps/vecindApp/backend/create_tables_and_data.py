"""
Script para crear todas las tablas y datos iniciales incluyendo usuario admin.
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from src.core.config import settings
from src.database import Base
from src.database.models import *  # Importar todos los modelos
from src.core.security import hash_password


async def create_tables_and_initial_data():
    """Crear todas las tablas y datos iniciales."""
    
    # Crear engine
    engine = create_async_engine(settings.database.async_url)
    
    try:
        async with engine.begin() as conn:
            # Crear el schema si no existe
            await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {settings.database.db_schema}"))
            
            # Crear todas las tablas
            await conn.run_sync(Base.metadata.create_all)
            print("✅ Todas las tablas creadas exitosamente")
            
            # Insertar datos iniciales
            
            # 1. Crear roles
            await conn.execute(text("""
                INSERT INTO vecindapp.rol (codigo, nombre, descripcion) VALUES
                ('admin', 'Administrador', 'Administrador del sistema'),
                ('directiva', 'Directiva', 'Miembro de la directiva de junta de vecinos'),
                ('vecino', 'Vecino', 'Vecino registrado en la junta')
                ON CONFLICT (codigo) DO NOTHING
            """))
            print("✅ Roles creados")
            
            # 2. Crear región de ejemplo
            await conn.execute(text("""
                INSERT INTO vecindapp.region (nombre, codigo) VALUES
                ('Región Metropolitana', 'RM')
                ON CONFLICT (codigo) DO NOTHING
            """))
            
            # 3. Crear comuna de ejemplo
            await conn.execute(text("""
                INSERT INTO vecindapp.comuna (id_region, nombre) VALUES
                (1, 'Santiago')
                ON CONFLICT (id_region, nombre) DO NOTHING
            """))
            
            # 4. Crear junta de ejemplo
            await conn.execute(text("""
                INSERT INTO vecindapp.junta (id_comuna, nombre, direccion, telefono, email, descripcion) 
                SELECT 1, 'Junta de Vecinos Barrio Oeste', 'Av. Siempre Viva 1234', '+56987654321', 'contacto@juntabarrioeste.cl', 'Junta de vecinos del Barrio Oeste'
                WHERE NOT EXISTS (
                    SELECT 1 FROM vecindapp.junta WHERE nombre = 'Junta de Vecinos Barrio Oeste'
                )
            """))
            print("✅ Datos geográficos y junta admin creados")
            
            # 5. Crear usuario administrador
            admin_password_hash = hash_password("admin")
            await conn.execute(text("""
                INSERT INTO vecindapp.usuario (id_junta, email, pass_hash, activo) VALUES
                (1, 'admin@admin.cl', :password_hash, true)
                ON CONFLICT (id_junta, email) DO NOTHING
            """), {"password_hash": admin_password_hash})
            
            # 6. Asignar rol de admin al usuario
            await conn.execute(text("""
                INSERT INTO vecindapp.usuario_rol (id_usuario, id_rol) 
                SELECT u.id_usuario, r.id_rol 
                FROM vecindapp.usuario u, vecindapp.rol r 
                WHERE u.email = 'admin@admin.cl' AND r.codigo = 'admin'
                ON CONFLICT DO NOTHING
            """))
            print("✅ Usuario administrador creado: admin@admin.cl / admin")
            
            # 7. Crear algunas regiones y comunas adicionales para pruebas
            await conn.execute(text("""
                INSERT INTO vecindapp.region (nombre, codigo) VALUES
                ('Región de Valparaíso', 'V'),
                ('Región del Biobío', 'VIII')
                ON CONFLICT (codigo) DO NOTHING
            """))
            
            await conn.execute(text("""
                INSERT INTO vecindapp.comuna (id_region, nombre) VALUES
                (1, 'Las Condes'),
                (1, 'Providencia'),
                (1, 'Ñuñoa'),
                (2, 'Valparaíso'),
                (2, 'Viña del Mar'),
                (3, 'Concepción'),
                (3, 'Talcahuano')
                ON CONFLICT (id_region, nombre) DO NOTHING
            """))
            print("✅ Regiones y comunas adicionales creadas")
            
            # 8. Crear algunas juntas de ejemplo adicionales
            juntas_adicionales = [
                (2, 'Junta de Vecinos Las Condes Centro', 'Av. Apoquindo 1234', '+56987654321', 'contacto@jvlascondes.cl'),
                (3, 'Junta de Vecinos Providencia Norte', 'Av. Providencia 5678', '+56976543210', 'info@jvprovidencia.cl'),
                (4, 'Junta de Vecinos Ñuñoa Sur', 'Av. Irarrázaval 9012', '+56965432109', 'contacto@jvnunoa.cl')
            ]
            
            for id_comuna, nombre, direccion, telefono, email in juntas_adicionales:
                await conn.execute(text("""
                    INSERT INTO vecindapp.junta (id_comuna, nombre, direccion, telefono, email) 
                    SELECT :id_comuna, :nombre, :direccion, :telefono, :email
                    WHERE NOT EXISTS (
                        SELECT 1 FROM vecindapp.junta WHERE nombre = :nombre
                    )
                """), {
                    "id_comuna": id_comuna,
                    "nombre": nombre, 
                    "direccion": direccion,
                    "telefono": telefono,
                    "email": email
                })
            print("✅ Juntas de ejemplo creadas")
            
        print("\n🎉 ¡Base de datos inicializada correctamente!")
        print("📧 Usuario admin: admin@admin.cl")
        print("🔑 Contraseña: admin")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_tables_and_initial_data())
