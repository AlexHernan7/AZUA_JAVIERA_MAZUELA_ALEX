"""
Script de prueba para el endpoint de firma y timbre.
Ejecutar: python test_firma_timbre_endpoint.py
"""

import requests
import json
import sys

# Configuración
BASE_URL = "http://localhost:8000"
ENDPOINT = f"{BASE_URL}/api/juntas/1/firma-timbre"

# Datos de prueba (imagen base64 mínima - 1x1 pixel PNG transparente)
TEST_FIRMA = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
TEST_TIMBRE = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

def test_endpoint(token=None):
    """Prueba el endpoint de firma-timbre"""
    
    print("=" * 60)
    print("🧪 PRUEBA DE ENDPOINT: PATCH /api/juntas/1/firma-timbre")
    print("=" * 60)
    
    # Preparar headers
    headers = {
        "Content-Type": "application/json"
    }
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
        print(f"✅ Token proporcionado: {token[:20]}...")
    else:
        print("⚠️  No se proporcionó token - el endpoint debería retornar 401")
    
    # Preparar datos
    data = {
        "firma_presidente": TEST_FIRMA,
        "timbre": TEST_TIMBRE
    }
    
    print(f"\n📤 Enviando petición a: {ENDPOINT}")
    print(f"📦 Datos: firma_presidente={'presente' if TEST_FIRMA else 'None'}, timbre={'presente' if TEST_TIMBRE else 'None'}")
    
    try:
        # Hacer la petición
        response = requests.patch(
            ENDPOINT,
            headers=headers,
            json=data,
            timeout=10
        )
        
        print(f"\n📥 Respuesta recibida:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        try:
            response_json = response.json()
            print(f"   Body: {json.dumps(response_json, indent=2)}")
        except:
            print(f"   Body (text): {response.text[:500]}")
        
        # Análisis de la respuesta
        print(f"\n📊 Análisis:")
        if response.status_code == 200:
            print("   ✅ ÉXITO: Endpoint funcionando correctamente")
        elif response.status_code == 401:
            print("   ⚠️  NO AUTORIZADO: Necesitas un token válido")
        elif response.status_code == 403:
            print("   ⚠️  PROHIBIDO: El usuario no tiene permisos de presidente")
        elif response.status_code == 404:
            print("   ❌ NO ENCONTRADO: El endpoint no existe o la ruta no coincide")
        elif response.status_code == 422:
            print("   ⚠️  VALIDACIÓN: Error en los datos enviados")
        else:
            print(f"   ❌ ERROR: Status code {response.status_code}")
        
        return response.status_code == 200
        
    except requests.exceptions.ConnectionError:
        print(f"\n❌ ERROR: No se pudo conectar a {BASE_URL}")
        print("   Asegúrate de que el servidor esté corriendo:")
        print("   poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Si se proporciona un token como argumento, usarlo
    token = sys.argv[1] if len(sys.argv) > 1 else None
    
    if not token:
        print("\n💡 Para probar con autenticación, proporciona un token:")
        print("   python test_firma_timbre_endpoint.py <tu_token_jwt>")
        print("\n   Obtén el token haciendo login en:")
        print(f"   POST {BASE_URL}/api/auth/login")
        print()
    
    success = test_endpoint(token)
    
    print("\n" + "=" * 60)
    if success:
        print("✅ PRUEBA EXITOSA")
    else:
        print("❌ PRUEBA FALLIDA - Revisa los logs del servidor")
    print("=" * 60)
    
    sys.exit(0 if success else 1)

