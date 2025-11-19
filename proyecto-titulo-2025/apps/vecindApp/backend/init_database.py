"""
Script unificado para inicializar la base de datos.
Crea todas las tablas y datos iniciales necesarios para el sistema.
"""

import asyncio
import json
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from src.core.config import settings
from src.database import Base
from src.database.models import *  # Importar todos los modelos
from src.core.security import hash_password


async def init_database():
    """Inicializar base de datos: crear tablas y datos iniciales."""
    
    # Crear engine
    engine = create_async_engine(settings.database.async_url)
    
    try:
        async with engine.begin() as conn:
            print("=" * 60)
            print("INICIALIZANDO BASE DE DATOS VECINDAPP")
            print("=" * 60)
            
            # ========== 1. CREAR SCHEMA Y TABLAS ==========
            print("\n[1/7] Creando schema y tablas...")
            await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {settings.database.db_schema}"))
            await conn.run_sync(Base.metadata.create_all)
            print("✅ Schema y tablas creadas")
            
            # ========== 2. CREAR ROLES ==========
            print("\n[2/7] Creando roles del sistema...")
            roles = [
                ("admin", "Administrador", "Administrador del sistema"),
                ("directiva", "Directiva", "Miembro de la directiva de junta de vecinos"),
                ("vecino", "Vecino", "Vecino registrado en la junta")
            ]
            
            for codigo, nombre, descripcion in roles:
                # Verificar si el rol ya existe
                result = await conn.execute(text("""
                    SELECT id_rol FROM vecindapp.rol WHERE codigo = :codigo
                """), {"codigo": codigo})
                
                if not result.scalar():
                    await conn.execute(text("""
                        INSERT INTO vecindapp.rol (codigo, nombre, descripcion) 
                        VALUES (:codigo, :nombre, :descripcion)
                    """), {"codigo": codigo, "nombre": nombre, "descripcion": descripcion})
            
            print("✅ 3 roles creados: admin, directiva, vecino")
            
            # ========== 3. CARGAR REGIONES Y COMUNAS DESDE JSON ==========
            print("\n[3/7] Cargando regiones y comunas desde JSON...")
            
            # Buscar el archivo JSON (primero en backend/data, luego en frontend)
            json_path = Path(__file__).parent / "data" / "regiones-comunas.json"
            
            # Si no existe en backend, intentar con frontend (para desarrollo local)
            if not json_path.exists():
                json_path = Path(__file__).parent.parent / "frontend" / "public" / "data" / "regiones-comunas.json"
            
            if not json_path.exists():
                print(f"⚠️  Archivo JSON no encontrado en: {json_path}")
                print("⚠️  Continuando sin regiones y comunas...")
            else:
                with open(json_path, 'r', encoding='utf-8') as f:
                    regiones_data = json.load(f)
                
                print(f"   Procesando {len(regiones_data)} regiones...")
                total_comunas = 0
                
                for region_nombre, comunas_list in regiones_data.items():
                    # Verificar si la región ya existe
                    result = await conn.execute(text("""
                        SELECT id_region FROM vecindapp.region 
                        WHERE nombre = :nombre
                    """), {"nombre": region_nombre})
                    id_region = result.scalar()
                    
                    # Si no existe, insertarla
                    if not id_region:
                        await conn.execute(text("""
                            INSERT INTO vecindapp.region (nombre) 
                            VALUES (:nombre)
                        """), {"nombre": region_nombre})
                        
                        # Obtener el ID de la región recién creada
                        result = await conn.execute(text("""
                            SELECT id_region FROM vecindapp.region 
                            WHERE nombre = :nombre
                        """), {"nombre": region_nombre})
                        id_region = result.scalar()
                    
                    # Insertar comunas de esta región
                    for comuna_nombre in comunas_list:
                        # Verificar si la comuna ya existe
                        result = await conn.execute(text("""
                            SELECT id_comuna FROM vecindapp.comuna 
                            WHERE id_region = :id_region AND nombre = :nombre
                        """), {"id_region": id_region, "nombre": comuna_nombre})
                        
                        if not result.scalar():
                            await conn.execute(text("""
                                INSERT INTO vecindapp.comuna (id_region, nombre) 
                                VALUES (:id_region, :nombre)
                            """), {"id_region": id_region, "nombre": comuna_nombre})
                        total_comunas += 1
                
                result = await conn.execute(text("SELECT COUNT(*) FROM vecindapp.region"))
                total_regiones = result.scalar()
                result = await conn.execute(text("SELECT COUNT(*) FROM vecindapp.comuna"))
                total_comunas_db = result.scalar()
                
                print(f"✅ {total_regiones} regiones y {total_comunas_db} comunas cargadas desde JSON")
            
            # ========== 4. CREAR ESTADOS DE CERTIFICADO Y RESERVA ==========
            print("\n[4/7] Creando estados del sistema...")
            
            # Estados de certificado
            estados_certificado = [
                ("pendiente_pago", "Certificado pendiente de pago"),
                ("generado", "Certificado generado y listo"),
                ("entregado", "Certificado entregado al solicitante")
            ]
            
            for nombre_estado, descripcion in estados_certificado:
                # Verificar si el estado ya existe
                result = await conn.execute(text("""
                    SELECT id_estado FROM vecindapp.estado_certificado 
                    WHERE nombre_estado = :nombre_estado
                """), {"nombre_estado": nombre_estado})
                
                if not result.scalar():
                    await conn.execute(text("""
                        INSERT INTO vecindapp.estado_certificado (nombre_estado, descripcion, activo) 
                        VALUES (:nombre_estado, :descripcion, true)
                    """), {"nombre_estado": nombre_estado, "descripcion": descripcion})
            
            # Estados de reserva
            estados_reserva = [
                ("pendiente", "Reserva pendiente de confirmación"),
                ("pagada", "Reserva pagada"),
                ("aprobada", "Reserva aprobada por la junta"),
                ("rechazada", "Reserva rechazada"),
                ("cancelada", "Reserva cancelada"),
                ("confirmada", "Reserva confirmada y activa")
            ]
            
            for nombre_estado, descripcion in estados_reserva:
                # Verificar si el estado ya existe
                result = await conn.execute(text("""
                    SELECT id_estado FROM vecindapp.estado_reserva 
                    WHERE nombre_estado = :nombre_estado
                """), {"nombre_estado": nombre_estado})
                
                if not result.scalar():
                    await conn.execute(text("""
                        INSERT INTO vecindapp.estado_reserva (nombre_estado, descripcion, activo) 
                        VALUES (:nombre_estado, :descripcion, true)
                    """), {"nombre_estado": nombre_estado, "descripcion": descripcion})
            
            print(f"✅ {len(estados_certificado)} estados de certificado creados")
            print(f"✅ {len(estados_reserva)} estados de reserva creados")
            
            # ========== 5. CREAR TIPOS DE ESPACIO ==========
            print("\n[5/7] Creando tipos de espacio...")
            
            tipos_espacio = [
                ("Cancha", "Cancha deportiva"),
                ("Sala", "Sala de reuniones o eventos"),
                ("Plaza", "Plaza o espacio al aire libre"),
                ("Otro", "Otro tipo de espacio")
            ]
            
            for tipo, descripcion in tipos_espacio:
                # Verificar si el tipo ya existe
                result = await conn.execute(text("""
                    SELECT id_tipo FROM vecindapp.tipo_espacio 
                    WHERE tipo = :tipo
                """), {"tipo": tipo})
                
                if not result.scalar():
                    await conn.execute(text("""
                        INSERT INTO vecindapp.tipo_espacio (tipo, descripcion, activo) 
                        VALUES (:tipo, :descripcion, true)
                    """), {"tipo": tipo, "descripcion": descripcion})
            
            print(f"✅ {len(tipos_espacio)} tipos de espacio creados")
            
            # ========== 6. CREAR MOTIVOS DE SOLICITUD ==========
            print("\n[6/7] Creando motivos de solicitud...")
            
            motivos_solicitud = [
                ("Postulación a beneficios sociales (Registro Social de Hogares, subsidios habitacionales, bonos)", "Trámites ante instituciones públicas", "Para postular a beneficios sociales del estado"),
                ("Procesos en municipalidades (inscripción en juntas de vecinos, becas municipales o ayudas sociales)", "Trámites ante instituciones públicas", "Para trámites municipales"),
                ("Solicitudes en el SII o Tesorería para acreditar domicilio tributario", "Trámites ante instituciones públicas", "Para acreditar domicilio tributario"),
                ("Juicios civiles, laborales o de familia (para demostrar residencia)", "Procesos judiciales o notariales", "Para procesos judiciales"),
                ("Trámites de posesión efectiva, herencias o escrituras", "Procesos judiciales o notariales", "Para trámites notariales"),
                ("Cambio de domicilio en causas judiciales", "Procesos judiciales o notariales", "Para cambio de domicilio judicial"),
                ("Acreditar residencia ante el Servicio Nacional de Migraciones", "Trámites migratorios", "Para trámites migratorios"),
                ("Solicitudes de permanencia definitiva, visados o nacionalización", "Trámites migratorios", "Para permanencia definitiva"),
                ("Bancos o financieras (abrir cuentas, solicitar créditos)", "Instituciones privadas", "Para trámites bancarios"),
                ("Aseguradoras o instituciones educativas para validar dirección", "Instituciones privadas", "Para validar dirección"),
                ("Postulación a colegios con criterios de cercanía", "Otros casos prácticos", "Para postulación escolar"),
                ("Contratos de arriendo o servicios básicos sin boletas propias", "Otros casos prácticos", "Para contratos de servicios")
            ]
            
            for motivo, grupo, descripcion in motivos_solicitud:
                # Verificar si el motivo ya existe
                result = await conn.execute(text("""
                    SELECT id_motivo FROM vecindapp.motivo_solicitud 
                    WHERE motivo = :motivo
                """), {"motivo": motivo})
                
                if not result.scalar():
                    await conn.execute(text("""
                        INSERT INTO vecindapp.motivo_solicitud (motivo, grupo, descripcion, activo) 
                        VALUES (:motivo, :grupo, :descripcion, true)
                    """), {"motivo": motivo, "grupo": grupo, "descripcion": descripcion})
            
            print(f"✅ {len(motivos_solicitud)} motivos de solicitud creados")
            
            # ========== 7. CREAR USUARIO ADMINISTRADOR ==========
            print("\n[7/7] Creando usuario administrador...")
            
            admin_password_hash = hash_password("admin")
            
            # Verificar si ya existe
            result = await conn.execute(text("""
                SELECT id_usuario FROM vecindapp.usuario 
                WHERE email = 'admin@admin.cl'
            """))
            existing_admin = result.scalar()
            
            if not existing_admin:
                # Crear usuario admin (sin junta, es admin global)
                await conn.execute(text("""
                    INSERT INTO vecindapp.usuario (email, pass_hash, activo) 
                    VALUES ('admin@admin.cl', :password_hash, true)
                """), {"password_hash": admin_password_hash})
                
                # Asignar rol de admin
                await conn.execute(text("""
                    INSERT INTO vecindapp.usuario_rol (id_usuario, id_rol) 
                    SELECT u.id_usuario, r.id_rol 
                    FROM vecindapp.usuario u, vecindapp.rol r 
                    WHERE u.email = 'admin@admin.cl' AND r.codigo = 'admin'
                """))
                
                print("✅ Usuario administrador creado")
            else:
                print("✅ Usuario administrador ya existe")
            
            print("\n" + "=" * 60)
            print("✅ BASE DE DATOS INICIALIZADA CORRECTAMENTE")
            print("=" * 60)
            print("\n📊 RESUMEN:")
            
            # Contar registros finales
            result = await conn.execute(text("SELECT COUNT(*) FROM vecindapp.rol"))
            print(f"   • Roles: {result.scalar()}")
            
            result = await conn.execute(text("SELECT COUNT(*) FROM vecindapp.region"))
            print(f"   • Regiones: {result.scalar()}")
            
            result = await conn.execute(text("SELECT COUNT(*) FROM vecindapp.comuna"))
            print(f"   • Comunas: {result.scalar()}")
            
            result = await conn.execute(text("SELECT COUNT(*) FROM vecindapp.estado_certificado"))
            print(f"   • Estados de certificado: {result.scalar()}")
            
            result = await conn.execute(text("SELECT COUNT(*) FROM vecindapp.estado_reserva"))
            print(f"   • Estados de reserva: {result.scalar()}")
            
            result = await conn.execute(text("SELECT COUNT(*) FROM vecindapp.tipo_espacio"))
            print(f"   • Tipos de espacio: {result.scalar()}")
            
            result = await conn.execute(text("SELECT COUNT(*) FROM vecindapp.motivo_solicitud"))
            print(f"   • Motivos de solicitud: {result.scalar()}")
            
            print("\n🔐 CREDENCIALES DE ADMINISTRADOR:")
            print("   • Email: admin@admin.cl")
            print("   • Contraseña: admin")
            
            print("\n💡 PRÓXIMOS PASOS:")
            print("   1. Las juntas de vecinos se crean desde el frontend")
            print("   2. Los vecinos se registran desde el formulario público")
            print("   3. Los espacios se crean desde el panel de directiva")
            print("\n" + "=" * 60)
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    print("\n🚀 Iniciando inicialización de base de datos...\n")
    asyncio.run(init_database())

