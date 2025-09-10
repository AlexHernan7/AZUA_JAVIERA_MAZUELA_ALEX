#!/usr/bin/env python3
"""
Script de prueba para el endpoint de login.

Instrucciones:
1. Ejecutar el servidor: poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
2. Ir a http://localhost:8000/api/docs
3. Usar el endpoint POST /api/auth/login con estos datos de prueba
4. Verificar que se obtiene un JWT token válido
"""

# Datos de prueba para login
# Usa los mismos datos que usaste en el registro anterior

test_login_data = {
    "email": "maria.test@gmail.com",
    "password": "TestPassword123"
}

print("=== DATOS DE PRUEBA PARA LOGIN ===")
print(f"Email: {test_login_data['email']}")
print(f"Password: {test_login_data['password']}")

print("\n=== INSTRUCCIONES ===")
print("1. Asegúrate que el servidor esté corriendo:")
print("   poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload")
print("\n2. Ve a Swagger UI: http://localhost:8000/api/docs")
print("\n3. Busca el endpoint POST /api/auth/login")
print("\n4. Usa estos datos de prueba:")
print(f"   {test_login_data}")

print("\n=== RESPUESTA ESPERADA ===")
print("✅ Status: 200 OK")
print("✅ access_token: JWT token (eyJhbGciOiJIUzI1NiIs...)")
print("✅ token_type: bearer")
print("✅ expires_in: 1440 (minutos)")
print("✅ user: Datos del usuario y vecino")

print("\n=== POSIBLES ERRORES ===")
print("❌ Status: 401 - Credenciales inválidas")
print("   → Verifica email y password")
print("❌ Status: 500 - Error interno")
print("   → Revisa los logs del servidor")

print("\n=== VERIFICAR JWT TOKEN ===")
print("Puedes decodificar el token en: https://jwt.io")
print("Debe contener: sub (user_id), email, nombres, apellidos, exp")
