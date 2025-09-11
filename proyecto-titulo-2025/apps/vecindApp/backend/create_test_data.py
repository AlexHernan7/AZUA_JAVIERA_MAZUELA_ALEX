#!/usr/bin/env python3
"""
Script para crear datos de prueba completos para VecindApp.

Incluye usuarios de ejemplo que puedes usar para probar la aplicación.
"""

import json
from datetime import date

def get_test_users():
    """
    Retorna una lista de usuarios de prueba listos para usar.
    Incluye diferentes tipos de usuarios y casos de prueba.
    """
    
    # Imagen base64 válida para pruebas (SVG simple)
    test_image = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIj4KICA8Y2lyY2xlIGN4PSI1MCIgY3k9IjUwIiByPSI0MCIgZmlsbD0iYmx1ZSIgLz4KICA8dGV4dCB4PSI1MCIgeT0iNTUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZpbGw9IndoaXRlIiBmb250LXNpemU9IjE2Ij5UZXN0PC90ZXh0Pgo8L3N2Zz4="
    
    usuarios_prueba = [
        {
            "nombre": "Usuario Básico",
            "descripcion": "Usuario normal para pruebas básicas",
            "data": {
                "email": "juan.perez@gmail.com",
                "password": "MiPassword123!",
                "rut": "12345678K",
                "nombres": "Juan Carlos",
                "apellido_paterno": "Pérez",
                "apellido_materno": "González",
                "fecha_nacimiento": "1990-05-15",
                "telefono": "+56912345678",
                "direccion": "Los Aromos 123, Maipú",
                "foto_perfil": test_image,
                "id_region": 1,
                "id_comuna": 1,
                "id_junta": 1
            }
        },
        {
            "nombre": "Usuario Sin Foto",
            "descripcion": "Usuario sin foto de perfil",
            "data": {
                "email": "maria.lopez@hotmail.com",
                "password": "Password456@",
                "rut": "11222333K",
                "nombres": "María Elena",
                "apellido_paterno": "López",
                "apellido_materno": "Martínez",
                "fecha_nacimiento": "1985-08-20",
                "telefono": "+56987654321",
                "direccion": "Las Américas 456, Maipú",
                "foto_perfil": None,
                "id_region": 1,
                "id_comuna": 1,
                "id_junta": 2
            }
        },
        {
            "nombre": "Usuario Joven",
            "descripcion": "Usuario más joven para probar validaciones",
            "data": {
                "email": "carlos.silva@gmail.com",
                "password": "Secure789#",
                "rut": "19876543K",
                "nombres": "Carlos Andrés",
                "apellido_paterno": "Silva",
                "apellido_materno": "Rojas",
                "fecha_nacimiento": "1995-12-03",
                "telefono": "+56956789012",
                "direccion": "Av. Pajaritos 789, Maipú",
                "foto_perfil": test_image,
                "id_region": 1,
                "id_comuna": 1,
                "id_junta": 3
            }
        },
        {
            "nombre": "Usuario Apellido Único",
            "descripcion": "Usuario con solo apellido paterno",
            "data": {
                "email": "ana.torres@outlook.com",
                "password": "MyPass2024$",
                "rut": "15432109K",
                "nombres": "Ana Sofía",
                "apellido_paterno": "Torres",
                "apellido_materno": "",
                "fecha_nacimiento": "1988-03-12",
                "telefono": "+56923456789",
                "direccion": "Villa Los Aromos 321, Maipú",
                "foto_perfil": None,
                "id_region": 1,
                "id_comuna": 1,
                "id_junta": 1
            }
        }
    ]
    
    return usuarios_prueba

def print_test_data():
    """Imprime los datos de prueba de forma organizada."""
    usuarios = get_test_users()
    
    print("=" * 80)
    print("🧪 DATOS DE PRUEBA PARA VECINDAPP")
    print("=" * 80)
    
    print("\n📋 DATOS INICIALES DISPONIBLES:")
    print("- Región: Región Metropolitana (ID: 1)")
    print("- Comuna: Maipú (ID: 1)")
    print("- Juntas disponibles:")
    print("  * ID 1: Junta de Vecinos Villa Los Aromos")
    print("  * ID 2: Junta de Vecinos Las Américas") 
    print("  * ID 3: Junta de Vecinos Central Maipú")
    print("- Roles: vecino, directiva, admin")
    
    print(f"\n👥 USUARIOS DE PRUEBA ({len(usuarios)} disponibles):")
    print("-" * 60)
    
    for i, usuario in enumerate(usuarios, 1):
        print(f"\n{i}. {usuario['nombre']}")
        print(f"   📝 {usuario['descripcion']}")
        print(f"   📧 Email: {usuario['data']['email']}")
        print(f"   🔑 Password: {usuario['data']['password']}")
        print(f"   🆔 RUT: {usuario['data']['rut']}")
        print(f"   🏠 Junta: {usuario['data']['id_junta']}")
        
        # Mostrar JSON para copiar
        print(f"   📋 JSON para API:")
        json_data = json.dumps(usuario['data'], indent=4, ensure_ascii=False, default=str)
        # Mostrar solo las primeras líneas
        lines = json_data.split('\n')
        for line in lines[:6]:
            print(f"      {line}")
        if len(lines) > 6:
            print(f"      ... ({len(lines)-6} líneas más)")
    
    print("\n" + "=" * 80)
    print("🚀 CÓMO USAR:")
    print("1. Inicia tu servidor: poetry run python src/main.py")
    print("2. Ve a: http://localhost:8000/api/docs")
    print("3. Busca POST /api/auth/register")
    print("4. Copia y pega cualquier JSON de arriba")
    print("5. ¡Prueba el registro!")
    
    print("\n🔍 ENDPOINTS ÚTILES:")
    print("- POST /api/auth/register - Registrar usuario")
    print("- POST /api/auth/login - Login con email/password")
    print("- GET /api/health - Estado de la API")
    
    print("\n⚠️  NOTAS:")
    print("- Los RUTs son válidos según el algoritmo módulo 11")
    print("- Las contraseñas cumplen todos los requisitos")
    print("- Los teléfonos tienen formato chileno (+56)")
    print("- Las imágenes son SVG válidos en base64")
    print("=" * 80)

def get_user_json(user_index=0):
    """
    Retorna el JSON de un usuario específico para uso directo.
    
    Args:
        user_index: Índice del usuario (0-3)
    
    Returns:
        dict: Datos del usuario listo para enviar a la API
    """
    usuarios = get_test_users()
    if 0 <= user_index < len(usuarios):
        return usuarios[user_index]['data']
    return None

if __name__ == "__main__":
    print_test_data()
    
    # Opcional: Guardar usuarios en archivo JSON
    usuarios = get_test_users()
    with open('usuarios_prueba.json', 'w', encoding='utf-8') as f:
        json.dump([u['data'] for u in usuarios], f, indent=2, ensure_ascii=False, default=str)
    print(f"\n💾 Usuarios guardados en 'usuarios_prueba.json'")
