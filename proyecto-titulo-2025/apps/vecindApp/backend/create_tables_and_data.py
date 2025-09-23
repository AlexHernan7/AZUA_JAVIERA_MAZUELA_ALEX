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
            
            # 2. Crear regiones principales
            await conn.execute(text("""
                INSERT INTO vecindapp.region (nombre, codigo) VALUES
                ('Región Metropolitana de Santiago', 'RM'),
                ('Región de Valparaíso', 'V'),
                ('Región del Biobío', 'VIII'),
                ('Región de Antofagasta', 'II'),
                ('Región de Atacama', 'III'),
                ('Región de Coquimbo', 'IV'),
                ('Región del Libertador General Bernardo O''Higgins', 'VI'),
                ('Región del Maule', 'VII'),
                ('Región de La Araucanía', 'IX'),
                ('Región de Los Lagos', 'X'),
                ('Región Aysén del General Carlos Ibáñez del Campo', 'XI'),
                ('Región de Magallanes y de la Antártica Chilena', 'XII'),
                ('Región de Arica y Parinacota', 'XV'),
                ('Región de Tarapacá', 'I'),
                ('Región de Los Ríos', 'XIV'),
                ('Región de Ñuble', 'XVI')
                ON CONFLICT (codigo) DO NOTHING
            """))
            print("✅ Regiones creadas")
            
            # 3. Crear todas las comunas usando los datos completos de Chile
            regiones_comunas = {
                "XV": ["Arica", "Camarones", "Putre", "General Lagos"],
                "I": ["Iquique", "Alto Hospicio", "Pozo Almonte", "Camiña", "Colchane", "Huara", "Pica"],
                "II": ["Antofagasta", "Mejillones", "Sierra Gorda", "Taltal", "Calama", "Ollagüe", "San Pedro de Atacama", "Tocopilla", "María Elena"],
                "III": ["Copiapó", "Caldera", "Tierra Amarilla", "Chañaral", "Diego de Almagro", "Vallenar", "Alto del Carmen", "Freirina", "Huasco"],
                "IV": ["La Serena", "Coquimbo", "Andacollo", "La Higuera", "Paiguano", "Vicuña", "Illapel", "Canela", "Los Vilos", "Salamanca", "Ovalle", "Combarbalá", "Monte Patria", "Punitaqui", "Río Hurtado"],
                "V": ["Valparaíso", "Viña del Mar", "Concón", "Quintero", "Puchuncaví", "Casablanca", "Juan Fernández", "Quilpué", "Villa Alemana", "Limache", "Olmué", "Quillota", "La Calera", "Hijuelas", "La Cruz", "Nogales", "San Antonio", "Cartagena", "El Quisco", "El Tabo", "Algarrobo", "Santo Domingo", "San Felipe", "Llay-Llay", "Catemu", "Panquehue", "Putaendo", "Santa María", "Los Andes", "Calle Larga", "Rinconada", "San Esteban", "Isla de Pascua"],
                "RM": ["Santiago", "Cerrillos", "Cerro Navia", "Conchalí", "El Bosque", "Estación Central", "Huechuraba", "Independencia", "La Cisterna", "La Florida", "La Granja", "La Pintana", "La Reina", "Las Condes", "Lo Barnechea", "Lo Espejo", "Lo Prado", "Macul", "Maipú", "Ñuñoa", "Pedro Aguirre Cerda", "Peñalolén", "Providencia", "Pudahuel", "Quilicura", "Quinta Normal", "Recoleta", "Renca", "San Joaquín", "San Miguel", "San Ramón", "Vitacura", "Puente Alto", "Pirque", "San José de Maipo", "Colina", "Lampa", "Tiltil", "Buin", "Paine", "San Bernardo", "Calera de Tango", "Talagante", "El Monte", "Isla de Maipo", "Padre Hurtado", "Peñaflor", "Melipilla", "Alhué", "Curacaví", "María Pinto", "San Pedro"],
                "VI": ["Rancagua", "Codegua", "Coinco", "Coltauco", "Doñihue", "Graneros", "Las Cabras", "Machalí", "Malloa", "Mostazal", "Olivar", "Peumo", "Pichidegua", "Quinta de Tilcoco", "Rengo", "Requínoa", "San Vicente", "Pichilemu", "La Estrella", "Litueche", "Marchihue", "Navidad", "Paredones", "San Fernando", "Chépica", "Chimbarongo", "Lolol", "Nancagua", "Palmilla", "Peralillo", "Placilla", "Pumanque", "Santa Cruz"],
                "VII": ["Talca", "Constitución", "Curepto", "Empedrado", "Maule", "Pelarco", "Pencahue", "Río Claro", "San Clemente", "San Rafael", "Linares", "Colbún", "Longaví", "Parral", "Retiro", "San Javier", "Villa Alegre", "Yerbas Buenas", "Cauquenes", "Chanco", "Pelluhue", "Curicó", "Hualañé", "Licantén", "Molina", "Rauco", "Romeral", "Sagrada Familia", "Teno", "Vichuquén"],
                "XVI": ["Chillán", "Chillán Viejo", "Coihueco", "Pinto", "San Ignacio", "El Carmen", "Pemuco", "Yungay", "Quillón", "Bulnes", "San Nicolás", "San Carlos", "Ñiquén", "San Fabián", "Coelemu", "Ránquil", "Trehuaco", "Cobquecura"],
                "VIII": ["Concepción", "Coronel", "Chiguayante", "Florida", "Hualqui", "Lota", "Penco", "San Pedro de la Paz", "Santa Juana", "Talcahuano", "Tomé", "Hualpén", "Lebu", "Arauco", "Cañete", "Contulmo", "Curanilahue", "Los Álamos", "Tirúa", "Los Ángeles", "Antuco", "Cabrero", "Laja", "Mulchén", "Nacimiento", "Negrete", "Quilaco", "Quilleco", "San Rosendo", "Santa Bárbara", "Tucapel", "Yumbel", "Alto Biobío"],
                "IX": ["Temuco", "Carahue", "Cholchol", "Cunco", "Curarrehue", "Freire", "Galvarino", "Gorbea", "Lautaro", "Loncoche", "Melipeuco", "Nueva Imperial", "Padre Las Casas", "Perquenco", "Pitrufquén", "Pucón", "Saavedra", "Teodoro Schmidt", "Toltén", "Vilcún", "Villarrica", "Angol", "Collipulli", "Curacautín", "Ercilla", "Lonquimay", "Los Sauces", "Lumaco", "Purén", "Renaico", "Traiguén", "Victoria"],
                "XIV": ["Valdivia", "Corral", "Lanco", "Los Lagos", "Máfil", "Mariquina", "Paillaco", "Panguipulli", "La Unión", "Futrono", "Lago Ranco", "Río Bueno"],
                "X": ["Puerto Montt", "Calbuco", "Cochamó", "Fresia", "Frutillar", "Los Muermos", "Llanquihue", "Maullín", "Puerto Varas", "Castro", "Ancud", "Chonchi", "Curaco de Vélez", "Dalcahue", "Puqueldón", "Queilén", "Quellón", "Quemchi", "Quinchao", "Osorno", "Puerto Octay", "Puyehue", "Río Negro", "San Juan de la Costa", "San Pablo", "Chaitén", "Futaleufú", "Hualaihué", "Palena"],
                "XI": ["Coyhaique", "Lago Verde", "Aysén", "Cisnes", "Guaitecas", "Cochrane", "O'Higgins", "Tortel", "Chile Chico", "Río Ibáñez"],
                "XII": ["Punta Arenas", "Laguna Blanca", "Río Verde", "San Gregorio", "Cabo de Hornos (Puerto Williams)", "Antártica", "Porvenir", "Primavera", "Timaukel", "Natales", "Torres del Paine"]
            }
            
            # Insertar comunas por cada región
            total_comunas = 0
            for codigo_region, comunas in regiones_comunas.items():
                # Obtener el ID de la región
                result = await conn.execute(text("SELECT id_region FROM vecindapp.region WHERE codigo = :codigo"), {"codigo": codigo_region})
                id_region = result.scalar()
                
                if id_region:
                    # Insertar todas las comunas de esta región
                    for comuna in comunas:
                        await conn.execute(text("""
                            INSERT INTO vecindapp.comuna (id_region, nombre) 
                            VALUES (:id_region, :nombre)
                            ON CONFLICT (id_region, nombre) DO NOTHING
                        """), {"id_region": id_region, "nombre": comuna})
                        total_comunas += 1
            
            print(f"✅ {total_comunas} comunas creadas")
            
            # 4. Crear usuario administrador (sin junta específica)
            admin_password_hash = hash_password("admin")
            await conn.execute(text("""
                INSERT INTO vecindapp.usuario (id_junta, email, pass_hash, activo) 
                SELECT NULL, 'admin@admin.cl', :password_hash, true
                WHERE NOT EXISTS (
                    SELECT 1 FROM vecindapp.usuario WHERE email = 'admin@admin.cl'
                )
            """), {"password_hash": admin_password_hash})
            
            # 5. Asignar rol de admin al usuario
            await conn.execute(text("""
                INSERT INTO vecindapp.usuario_rol (id_usuario, id_rol) 
                SELECT u.id_usuario, r.id_rol 
                FROM vecindapp.usuario u, vecindapp.rol r 
                WHERE u.email = 'admin@admin.cl' AND r.codigo = 'admin'
                ON CONFLICT DO NOTHING
            """))
            print("✅ Usuario administrador creado: admin@admin.cl / admin")
            
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
