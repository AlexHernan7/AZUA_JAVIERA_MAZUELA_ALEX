"""
Script de prueba para el endpoint de registro.

Ejecuta este script para probar el endpoint de registro de usuarios.
"""

import asyncio
import json
from datetime import date

# Datos de prueba para registrar un usuario
test_user_data = {
    "email": "juan.perez@gmail.com",
    "password": "MiPassword123",
    "nombres": "Juan Carlos",
    "apellidos": "Pérez González", 
    "fecha_nacimiento": "1990-05-15",
    "telefono": "+56912345678",
    "direccion": "Los Aromos 123",
    "id_comuna": 1,
    "id_junta": 1
}

print("=== DATOS DE PRUEBA PARA EL ENDPOINT DE REGISTRO ===")
print(json.dumps(test_user_data, indent=2, ensure_ascii=False))
print("\n=== INSTRUCCIONES ===")
print("1. Inicia el servidor: python src/main.py")
print("2. Ve a: http://localhost:8000/api/docs")
print("3. Busca el endpoint POST /api/auth/register")
print("4. Usa los datos de arriba para probar")
print("\n=== ENDPOINTS DISPONIBLES ===")
print("- POST /api/auth/register - Registrar usuario")
print("- GET /api/auth/comunas - Listar comunas")
print("- GET /api/auth/juntas/{comuna_id} - Listar juntas por comuna")
print("- GET /api/users/vecino/{vecino_id} - Obtener vecino por ID")
print("- GET /api/health - Estado de la API")

print("\n=== NOTAS IMPORTANTES ===")
print("- Asegúrate de tener datos en las tablas region, comuna y junta")
print("- Asegúrate de tener el rol 'vecino' en la tabla rol")
print("- La base de datos debe estar corriendo y las migraciones aplicadas")
