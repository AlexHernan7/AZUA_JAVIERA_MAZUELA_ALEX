"""
Script simple para probar el endpoint y ver los logs.
El token está expirado, pero podemos verificar que el endpoint responde.
"""

import requests
import json

BASE_URL = "http://localhost:8000"
ENDPOINT = f"{BASE_URL}/api/juntas/1/firma-timbre"

# Token expirado (pero sirve para verificar que el endpoint existe)
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwiZW1haWwiOiJhbGlzb25AZ21haWwuY29tIiwibm9tYnJlcyI6IkFsaXNvbiIsImFwZWxsaWRvX3BhdGVybm8iOiJNYXp1ZWxhIiwiYXBlbGxpZG9fbWF0ZXJubyI6IlZhbGRlcyIsInJvbGVzIjpbImRpcmVjdGl2YSJdLCJleHAiOjE3NjQ4MDg2NTh9.cXrLEAqmyMbG68R3HJmp1Wa9HtfHA4ZKBg7vLcv4hFw"

TEST_FIRMA = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

print("=" * 60)
print("🧪 PRUEBA CON TOKEN (puede estar expirado)")
print("=" * 60)
print(f"📤 Enviando PATCH a: {ENDPOINT}")
print("   (Revisa los logs del servidor para ver si aparece [REQUEST] y [FIRMA-TIMBRE])")
print()

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

data = {
    "firma_presidente": TEST_FIRMA
}

response = requests.patch(ENDPOINT, headers=headers, json=data)

print(f"📥 Status Code: {response.status_code}")
print(f"📥 Response: {json.dumps(response.json(), indent=2)}")
print()
print("✅ Si ves Status 401/403, el endpoint EXISTE y está funcionando")
print("   El problema es solo el token o los permisos")
print("=" * 60)

