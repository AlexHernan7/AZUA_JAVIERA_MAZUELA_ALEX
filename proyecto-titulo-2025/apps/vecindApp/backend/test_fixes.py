#!/usr/bin/env python3
"""
Script de prueba para verificar las correcciones:
1. Email se almacena correctamente (no NULL)
2. Teléfono se almacena sin +56

Instrucciones:
1. Ejecutar el servidor: poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
2. Ir a http://localhost:8000/api/docs
3. Usar el endpoint POST /api/auth/register con estos datos de prueba
4. Verificar en la base de datos que el email y teléfono se almacenan correctamente
"""

# Datos de prueba 1: Con +56 en teléfono
test_data_1 = {
    "email": "maria.test@gmail.com",
    "password": "TestPassword123",
    "nombres": "María José",
    "apellidos": "González López",
    "fecha_nacimiento": "1985-03-20",
    "telefono": "+56987654321",  # Debe almacenarse como 987654321
    "direccion": "Los Pinos 456",
    "id_comuna": 1,
    "id_junta": 1
}

# Datos de prueba 2: Con 56 (sin +)
test_data_2 = {
    "email": "carlos.test@gmail.com",
    "password": "TestPassword456",
    "nombres": "Carlos Eduardo",
    "apellidos": "Ramírez Silva",
    "fecha_nacimiento": "1992-07-10",
    "telefono": "56923456789",  # Debe almacenarse como 923456789
    "direccion": "Las Flores 789",
    "id_comuna": 1,
    "id_junta": 1
}

# Datos de prueba 3: Solo 9 dígitos
test_data_3 = {
    "email": "ana.test@gmail.com",
    "password": "TestPassword789",
    "nombres": "Ana Sofía",
    "apellidos": "Morales Vega",
    "fecha_nacimiento": "1988-11-25",
    "telefono": "945678901",  # Debe almacenarse como 945678901
    "direccion": "El Bosque 321",
    "id_comuna": 1,
    "id_junta": 1
}

print("=== DATOS DE PRUEBA ===")
print("\n1. Teléfono con +56:")
print(f"   Input: {test_data_1['telefono']}")
print(f"   Esperado en DB: 987654321")

print("\n2. Teléfono con 56:")
print(f"   Input: {test_data_2['telefono']}")
print(f"   Esperado en DB: 923456789")

print("\n3. Teléfono solo 9 dígitos:")
print(f"   Input: {test_data_3['telefono']}")
print(f"   Esperado en DB: 945678901")

print("\n=== VERIFICAR ===")
print("✅ Email NO debe ser NULL")
print("✅ Teléfono debe almacenarse SIN +56")
print("\nUsa estos datos en Swagger UI: http://localhost:8000/api/docs")
