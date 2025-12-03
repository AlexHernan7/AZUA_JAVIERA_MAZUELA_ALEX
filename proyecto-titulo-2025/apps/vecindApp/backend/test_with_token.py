"""
Script para probar el endpoint con un token real.
Primero necesitas hacer login y obtener un token.
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def login_and_test(email, password):
    """Hace login y luego prueba el endpoint"""
    
    print("=" * 60)
    print("🔐 PASO 1: Haciendo login...")
    print("=" * 60)
    
    # Login
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": email, "password": password}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Error en login: {login_response.status_code}")
        print(login_response.json())
        return False
    
    token = login_response.json()["access_token"]
    print(f"✅ Login exitoso. Token obtenido: {token[:30]}...")
    
    # Ahora probar el endpoint
    print("\n" + "=" * 60)
    print("🧪 PASO 2: Probando endpoint de firma-timbre...")
    print("=" * 60)
    
    # Imagen base64 mínima
    TEST_FIRMA = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "firma_presidente": TEST_FIRMA
    }
    
    response = requests.patch(
        f"{BASE_URL}/api/juntas/1/firma-timbre",
        headers=headers,
        json=data
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code in [200, 403]  # 200 = éxito, 403 = no es presidente (esperado)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python test_with_token.py <email> <password>")
        print("Ejemplo: python test_with_token.py presidente@example.com password123")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    
    success = login_and_test(email, password)
    sys.exit(0 if success else 1)

