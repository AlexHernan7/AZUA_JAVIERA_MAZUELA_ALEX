"""Crea datos iniciales en la base de datos."""

import asyncio
import json
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from src.database.session import get_transaction_session


async def create_initial_data():
    """Crea datos base: región, comuna, juntas y roles."""
    
    async with get_transaction_session() as session:
        try:
            print("Creando datos iniciales...")
            
            # 1. Cargar regiones y comunas desde JSON
            json_path = Path(__file__).parent.parent / "frontend" / "public" / "data" / "regiones-comunas.json"
            print(f"[INFO] Cargando regiones y comunas desde: {json_path}")
            
            with open(json_path, 'r', encoding='utf-8') as f:
                regiones_data = json.load(f)
            
            print(f"[INFO] Total regiones a crear: {len(regiones_data)}")
            total_comunas = sum(len(comunas) for comunas in regiones_data.values())
            print(f"[INFO] Total comunas a crear: {total_comunas}")
            
            # Crear todas las regiones y comunas
            for region_nombre, comunas_list in regiones_data.items():
                
                # Verificar si ya existe
                result = await session.execute(text("""
                    SELECT id_region FROM "vecindapp".region 
                    WHERE nombre = :nombre
                """), {"nombre": region_nombre})
                existing_region = result.scalar()
                
                if not existing_region:
                    await session.execute(text("""
                        INSERT INTO "vecindapp".region (nombre) 
                        VALUES (:nombre)
                    """), {"nombre": region_nombre})
                    print(f"[OK] Región creada: {region_nombre}")
                else:
                    print(f"[INFO] Región ya existe: {region_nombre}")
                
                # Obtener ID de la región
                result = await session.execute(text("""
                    SELECT id_region FROM "vecindapp".region 
                    WHERE nombre = :nombre
                """), {"nombre": region_nombre})
                id_region = result.scalar()
                
                # Crear comunas de esta región
                for comuna_nombre in comunas_list:
                    result = await session.execute(text("""
                        SELECT id_comuna FROM "vecindapp".comuna 
                        WHERE nombre = :nombre AND id_region = :id_region
                    """), {"nombre": comuna_nombre, "id_region": id_region})
                    existing_comuna = result.scalar()
                    
                    if not existing_comuna:
                        await session.execute(text("""
                            INSERT INTO "vecindapp".comuna (id_region, nombre) 
                            VALUES (:id_region, :nombre)
                        """), {"id_region": id_region, "nombre": comuna_nombre})
                        print(f"  [OK] Comuna creada: {comuna_nombre}")
                    else:
                        print(f"  [INFO] Comuna ya existe: {comuna_nombre}")
            
            print(f"\n[SUCCESS] Se procesaron todas las regiones y comunas")
            
            # 2. Obtener ID de Maipú para crear juntas de ejemplo (solo si existe)
            result = await session.execute(text("""
                SELECT c.id_comuna FROM "vecindapp".comuna c
                JOIN "vecindapp".region r ON c.id_region = r.id_region
                WHERE c.nombre = 'Maipú' 
                AND r.nombre = 'Región Metropolitana de Santiago'
            """))
            id_comuna = result.scalar()
            
            if not id_comuna:
                print("[WARNING] No se encontró la comuna de Maipú, usando la primera comuna disponible")
                result = await session.execute(text("""
                    SELECT id_comuna FROM "vecindapp".comuna LIMIT 1
                """))
                id_comuna = result.scalar()
            
            print(f"[INFO] Comuna seleccionada para juntas de ejemplo (ID: {id_comuna})")
            
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
                        INSERT INTO "vecindapp".junta (id_comuna, nombre, rut, direccion, telefono, email, descripcion, activa) 
                        VALUES (:id_comuna, :nombre, :rut, :direccion, :telefono, :email, :descripcion, :activa)
                    """), {
                        "id_comuna": id_comuna,
                        "nombre": nombre,
                        "rut": rut,
                        "direccion": direccion,
                        "telefono": telefono,
                        "email": email,
                        "descripcion": descripcion,
                        "activa": True
                    })
                    print(f"[OK] Junta creada: {nombre} (RUT: {rut})")
                else:
                    print(f"[INFO] Junta ya existe: {nombre}")
            
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
                    print(f"[OK] Rol creado: {nombre} (codigo: {codigo})")
                else:
                    print(f"[INFO] Rol ya existe: {nombre} (codigo: {codigo})")
            
            # 5. Crear tablas maestras
            print("\n[INFO] Creando tablas maestras...")
            
            # 5.1 Estados de certificado
            estados_certificado = [
                ("pendiente_pago", "Certificado pendiente de pago"),
                ("generado", "Certificado generado y listo"),
                ("entregado", "Certificado entregado al solicitante")
            ]
            
            for nombre_estado, descripcion in estados_certificado:
                result = await session.execute(text("""
                    SELECT id_estado FROM "vecindapp".estado_certificado 
                    WHERE nombre_estado = :nombre_estado
                """), {"nombre_estado": nombre_estado})
                existing_estado = result.scalar()
                
                if not existing_estado:
                    await session.execute(text("""
                        INSERT INTO "vecindapp".estado_certificado (nombre_estado, descripcion, activo) 
                        VALUES (:nombre_estado, :descripcion, true)
                    """), {
                        "nombre_estado": nombre_estado,
                        "descripcion": descripcion
                    })
                    print(f"[OK] Estado certificado creado: {nombre_estado}")
                else:
                    print(f"[INFO] Estado certificado ya existe: {nombre_estado}")
            
            # 5.2 Estados de reserva
            estados_reserva = [
                ("pendiente", "Reserva pendiente de confirmación"),
                ("pagada", "Reserva pagada"),
                ("aprobada", "Reserva aprobada por la junta"),
                ("rechazada", "Reserva rechazada"),
                ("cancelada", "Reserva cancelada"),
                ("confirmada", "Reserva confirmada y activa")
            ]
            
            for nombre_estado, descripcion in estados_reserva:
                result = await session.execute(text("""
                    SELECT id_estado FROM "vecindapp".estado_reserva 
                    WHERE nombre_estado = :nombre_estado
                """), {"nombre_estado": nombre_estado})
                existing_estado = result.scalar()
                
                if not existing_estado:
                    await session.execute(text("""
                        INSERT INTO "vecindapp".estado_reserva (nombre_estado, descripcion, activo) 
                        VALUES (:nombre_estado, :descripcion, true)
                    """), {
                        "nombre_estado": nombre_estado,
                        "descripcion": descripcion
                    })
                    print(f"[OK] Estado reserva creado: {nombre_estado}")
                else:
                    print(f"[INFO] Estado reserva ya existe: {nombre_estado}")
            
            # 5.3 Tipos de espacio
            tipos_espacio = [
                ("cancha", "Cancha deportiva"),
                ("sala", "Sala de reuniones o eventos"),
                ("plaza", "Plaza o espacio al aire libre"),
                ("otro", "Otro tipo de espacio")
            ]
            
            for tipo, descripcion in tipos_espacio:
                result = await session.execute(text("""
                    SELECT id_tipo FROM "vecindapp".tipo_espacio 
                    WHERE tipo = :tipo
                """), {"tipo": tipo})
                existing_tipo = result.scalar()
                
                if not existing_tipo:
                    await session.execute(text("""
                        INSERT INTO "vecindapp".tipo_espacio (tipo, descripcion, activo) 
                        VALUES (:tipo, :descripcion, true)
                    """), {
                        "tipo": tipo,
                        "descripcion": descripcion
                    })
                    print(f"[OK] Tipo espacio creado: {tipo}")
                else:
                    print(f"[INFO] Tipo espacio ya existe: {tipo}")
            
            # 5.4 Motivos de solicitud
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
                result = await session.execute(text("""
                    SELECT id_motivo FROM "vecindapp".motivo_solicitud 
                    WHERE motivo = :motivo
                """), {"motivo": motivo})
                existing_motivo = result.scalar()
                
                if not existing_motivo:
                    await session.execute(text("""
                        INSERT INTO "vecindapp".motivo_solicitud (motivo, grupo, descripcion, activo) 
                        VALUES (:motivo, :grupo, :descripcion, true)
                    """), {
                        "motivo": motivo,
                        "grupo": grupo,
                        "descripcion": descripcion
                    })
                    print(f"[OK] Motivo solicitud creado: {motivo[:50]}...")
                else:
                    print(f"[INFO] Motivo solicitud ya existe: {motivo[:50]}...")
            
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
                
                print(f"[OK] Usuario administrador creado: admin@admin.cl")
            else:
                print(f"[INFO] Usuario administrador ya existe: admin@admin.cl")
            
            # Confirmar todos los cambios
            await session.commit()
            print("\n[SUCCESS] Datos iniciales creados exitosamente!")
            
            # Mostrar resumen con IDs reales
            result = await session.execute(text("SELECT COUNT(*) FROM \"vecindapp\".junta WHERE id_comuna = :id_comuna"), {"id_comuna": id_comuna})
            total_juntas = result.scalar()
            
            # Contar registros de tablas maestras
            result = await session.execute(text("SELECT COUNT(*) FROM \"vecindapp\".estado_certificado"))
            total_estados_cert = result.scalar()
            
            result = await session.execute(text("SELECT COUNT(*) FROM \"vecindapp\".estado_reserva"))
            total_estados_res = result.scalar()
            
            result = await session.execute(text("SELECT COUNT(*) FROM \"vecindapp\".tipo_espacio"))
            total_tipos_esp = result.scalar()
            
            result = await session.execute(text("SELECT COUNT(*) FROM \"vecindapp\".motivo_solicitud"))
            total_motivos = result.scalar()
            
            # Contar totales finales
            result = await session.execute(text("SELECT COUNT(*) FROM \"vecindapp\".region"))
            total_regiones = result.scalar()
            
            result = await session.execute(text("SELECT COUNT(*) FROM \"vecindapp\".comuna"))
            total_comunas_final = result.scalar()
            
            print("\n[RESUMEN]:")
            print(f"- {total_regiones} Regiones cargadas desde JSON")
            print(f"- {total_comunas_final} Comunas cargadas desde JSON")
            print(f"- {total_juntas} Juntas de vecinos de ejemplo")
            print(f"- 3 Roles: vecino, directiva, admin")
            print(f"- {total_estados_cert} Estados de certificado")
            print(f"- {total_estados_res} Estados de reserva")
            print(f"- {total_tipos_esp} Tipos de espacio")
            print(f"- {total_motivos} Motivos de solicitud")
            print(f"- 1 Usuario administrador: admin@admin.cl")
            
            print("\n[READY] Ya puedes probar el sistema!")
            print("Usuario admin: admin@admin.cl")
            print("Contrasena: admin")
            print("\nDatos de prueba para registro:")
            print(f"- id_comuna: {id_comuna}")
            print("- id_junta: 1, 2 o 3 (cualquiera de las juntas creadas)")
            
        except Exception as e:
            await session.rollback()
            print(f"[ERROR] Error creando datos iniciales: {e}")
            raise


if __name__ == "__main__":
    print("Iniciando creacion de datos iniciales...")
    asyncio.run(create_initial_data())
