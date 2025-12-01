"""
Script para generar 50 usuarios de prueba en distintas juntas de vecinos.
"""

import asyncio
import random
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from src.database.session import get_transaction_session
from src.core.security import hash_password


# Datos de prueba realistas chilenos
NOMBRES_MASCULINOS = [
    "Juan", "Pedro", "Carlos", "Miguel", "Jose", "Francisco", "Luis", "Jorge", 
    "Roberto", "Diego", "Manuel", "Andres", "Ricardo", "Pablo", "Sergio",
    "Fernando", "Javier", "Raul", "Eduardo", "Mario", "Gonzalo", "Rodrigo"
]

NOMBRES_FEMENINOS = [
    "Maria", "Carmen", "Ana", "Isabel", "Rosa", "Patricia", "Laura", "Francisca",
    "Claudia", "Monica", "Soledad", "Teresa", "Gabriela", "Carolina", "Daniela",
    "Alejandra", "Veronica", "Andrea", "Marcela", "Paulina", "Lorena", "Beatriz"
]

APELLIDOS = [
    "Gonzalez", "Muñoz", "Rojas", "Diaz", "Perez", "Soto", "Contreras", "Silva",
    "Martinez", "Sepulveda", "Morales", "Rodriguez", "Lopez", "Fuentes", "Hernandez",
    "Torres", "Araya", "Flores", "Espinoza", "Valenzuela", "Pizarro", "Castillo",
    "Reyes", "Gutierrez", "Ramirez", "Mendoza", "Vargas", "Nunez", "Rivera", "Vega"
]

DIRECCIONES = [
    "Avenida Libertador", "Calle Los Aromos", "Pasaje Las Rosas", "Avenida Principal",
    "Calle San Martin", "Pasaje Los Olivos", "Avenida Los Carrera", "Calle O'Higgins",
    "Pasaje Los Robles", "Calle Arturo Prat", "Avenida Bernardo O'Higgins", "Calle Bulnes",
    "Pasaje Los Pinos", "Avenida Grecia", "Calle Manuel Rodriguez"
]


def generar_rut():
    """Genera un RUT chileno valido."""
    numero = random.randint(5000000, 25000000)
    
    # Calcular digito verificador
    multiplicador = 2
    suma = 0
    temp_numero = numero
    while temp_numero > 0:
        suma += (temp_numero % 10) * multiplicador
        temp_numero //= 10
        multiplicador += 1
        if multiplicador > 7:
            multiplicador = 2
    
    resto = suma % 11
    dv = 11 - resto
    
    if dv == 11:
        dv = '0'
    elif dv == 10:
        dv = 'K'
    else:
        dv = str(dv)
    
    return f"{numero}-{dv}"


def generar_telefono():
    """Genera un numero de telefono chileno."""
    numero = random.randint(10000000, 99999999)
    return f"+569{numero}"


def generar_fecha_nacimiento():
    """Genera una fecha de nacimiento entre 18 y 80 años atras."""
    hoy = datetime.now()
    años_atras = random.randint(18, 80)
    dias_aleatorios = random.randint(0, 365)
    fecha = hoy - timedelta(days=años_atras*365 + dias_aleatorios)
    return fecha.date()


async def generate_test_users():
    """Genera 50 usuarios de prueba distribuidos en las juntas existentes."""
    
    async with get_transaction_session() as session:
        try:
            print("=" * 60)
            print("GENERACION DE USUARIOS DE PRUEBA")
            print("=" * 60)
            
            # 1. Obtener juntas existentes
            result = await session.execute(text("""
                SELECT j.id_junta, j.nombre, j.id_comuna, c.nombre as comuna_nombre
                FROM "vecindapp".junta j
                JOIN "vecindapp".comuna c ON j.id_comuna = c.id_comuna
                WHERE j.activa = true
            """))
            juntas = result.all()
            
            if not juntas:
                print("[ERROR] No hay juntas activas en la base de datos")
                return
            
            print(f"[INFO] Encontradas {len(juntas)} juntas activas")
            for junta in juntas:
                print(f"  - {junta.nombre} (Comuna: {junta.comuna_nombre})")
            
            # 2. Obtener ID del rol vecino
            result = await session.execute(text("""
                SELECT id_rol FROM "vecindapp".rol WHERE codigo = 'vecino'
            """))
            rol_vecino_id = result.scalar()
            
            if not rol_vecino_id:
                print("[ERROR] No se encontro el rol 'vecino'")
                return
            
            # 3. Obtener ID del rol directiva
            result = await session.execute(text("""
                SELECT id_rol FROM "vecindapp".rol WHERE codigo = 'directiva'
            """))
            rol_directiva_id = result.scalar()
            
            print(f"\n[INFO] Generando 50 usuarios de prueba...")
            
            usuarios_creados = 0
            ruts_usados = set()
            
            for i in range(50):
                try:
                    # Seleccionar junta aleatoria
                    junta = random.choice(juntas)
                    
                    # Generar datos del usuario
                    es_masculino = random.choice([True, False])
                    nombre = random.choice(NOMBRES_MASCULINOS if es_masculino else NOMBRES_FEMENINOS)
                    apellido_paterno = random.choice(APELLIDOS)
                    apellido_materno = random.choice(APELLIDOS)
                    
                    # Generar RUT unico
                    while True:
                        rut = generar_rut()
                        if rut not in ruts_usados:
                            ruts_usados.add(rut)
                            break
                    
                    email = f"usuario{i+1}@test.cl"
                    telefono = generar_telefono()
                    fecha_nacimiento = generar_fecha_nacimiento()
                    direccion = f"{random.choice(DIRECCIONES)} {random.randint(100, 9999)}"
                    
                    # Contraseña por defecto
                    password_hash = hash_password("test123")
                    
                    # Decidir si sera directiva (20% de probabilidad)
                    es_directiva = random.random() < 0.2 and rol_directiva_id
                    
                    # Crear usuario
                    result = await session.execute(text("""
                        INSERT INTO "vecindapp".usuario (id_junta, email, pass_hash, activo)
                        VALUES (:id_junta, :email, :pass_hash, true)
                        RETURNING id_usuario
                    """), {
                        "id_junta": junta.id_junta,
                        "email": email,
                        "pass_hash": password_hash
                    })
                    id_usuario = result.scalar()
                    
                    # Asignar rol vecino
                    await session.execute(text("""
                        INSERT INTO "vecindapp".usuario_rol (id_usuario, id_rol)
                        VALUES (:id_usuario, :id_rol)
                    """), {
                        "id_usuario": id_usuario,
                        "id_rol": rol_vecino_id
                    })
                    
                    # Crear perfil de vecino
                    await session.execute(text("""
                        INSERT INTO "vecindapp".vecino (
                            id_junta, id_usuario, rut, nombres, apellido_paterno, apellido_materno,
                            fecha_nacimiento, telefono, email, direccion, id_comuna
                        )
                        VALUES (
                            :id_junta, :id_usuario, :rut, :nombres, :apellido_paterno, :apellido_materno,
                            :fecha_nacimiento, :telefono, :email, :direccion, :id_comuna
                        )
                    """), {
                        "id_junta": junta.id_junta,
                        "id_usuario": id_usuario,
                        "rut": rut,
                        "nombres": nombre,
                        "apellido_paterno": apellido_paterno,
                        "apellido_materno": apellido_materno,
                        "fecha_nacimiento": fecha_nacimiento,
                        "telefono": telefono,
                        "email": email,
                        "direccion": direccion,
                        "id_comuna": junta.id_comuna
                    })
                    
                    # Si es directiva, crear perfil adicional
                    if es_directiva:
                        cargos = ["presidente", "vicepresidente", "secretario", "tesorero", "director", "vocal"]
                        cargo = random.choice(cargos)
                        fecha_inicio = datetime.now() - timedelta(days=random.randint(30, 730))
                        
                        await session.execute(text("""
                            INSERT INTO "vecindapp".directiva (
                                id_junta, id_usuario, rut, nombres, apellido_paterno, apellido_materno,
                                telefono, email, cargo, fecha_inicio_cargo
                            )
                            VALUES (
                                :id_junta, :id_usuario, :rut, :nombres, :apellido_paterno, :apellido_materno,
                                :telefono, :email, :cargo, :fecha_inicio_cargo
                            )
                        """), {
                            "id_junta": junta.id_junta,
                            "id_usuario": id_usuario,
                            "rut": rut,
                            "nombres": nombre,
                            "apellido_paterno": apellido_paterno,
                            "apellido_materno": apellido_materno,
                            "telefono": telefono,
                            "email": email,
                            "cargo": cargo,
                            "fecha_inicio_cargo": fecha_inicio.date()
                        })
                        
                        # Asignar rol directiva
                        await session.execute(text("""
                            INSERT INTO "vecindapp".usuario_rol (id_usuario, id_rol)
                            VALUES (:id_usuario, :id_rol)
                        """), {
                            "id_usuario": id_usuario,
                            "id_rol": rol_directiva_id
                        })
                    
                    usuarios_creados += 1
                    if (usuarios_creados) % 10 == 0:
                        print(f"[PROGRESO] {usuarios_creados}/50 usuarios creados...")
                    
                except Exception as e:
                    print(f"[ERROR] Error al crear usuario {i+1}: {e}")
                    continue
            
            # Confirmar cambios
            await session.commit()
            
            print(f"\n[SUCCESS] Se crearon {usuarios_creados} usuarios de prueba exitosamente")
            print("\n[INFO] Credenciales de prueba:")
            print("  Email: usuario1@test.cl hasta usuario50@test.cl")
            print("  Password: test123")
            print("\n[INFO] Usuarios distribuidos en las siguientes juntas:")
            
            # Mostrar resumen por junta
            for junta in juntas:
                result = await session.execute(text("""
                    SELECT COUNT(*) FROM "vecindapp".vecino WHERE id_junta = :id_junta
                """), {"id_junta": junta.id_junta})
                total_vecinos = result.scalar()
                
                result = await session.execute(text("""
                    SELECT COUNT(*) FROM "vecindapp".directiva WHERE id_junta = :id_junta
                """), {"id_junta": junta.id_junta})
                total_directivos = result.scalar()
                
                print(f"  - {junta.nombre}: {total_vecinos} vecinos, {total_directivos} directivos")
            
            print("\n[INFO] Puedes eliminar este archivo manualmente cuando quieras")
            
        except Exception as e:
            await session.rollback()
            print(f"[ERROR] Error durante la generacion: {e}")
            raise


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("INICIANDO GENERACION DE USUARIOS DE PRUEBA")
    print("=" * 60 + "\n")
    asyncio.run(generate_test_users())

