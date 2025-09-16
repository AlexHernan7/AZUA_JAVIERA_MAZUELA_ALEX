#!/usr/bin/env python3
"""
Script de prueba para el endpoint de actualización de perfil con foto.
"""

import requests
import json
import base64

# URL del endpoint (ajusta según tu configuración)
BASE_URL = "http://localhost:8000"
ENDPOINT = f"{BASE_URL}/users/vecino/1/profile"

def create_test_image_base64():
    """
    Crea una imagen de prueba en base64 (1x1 pixel PNG transparente).
    """
    # PNG de 1x1 pixel transparente
    png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
    base64_data = base64.b64encode(png_data).decode('utf-8')
    return f"data:image/png;base64,{base64_data}"

def test_update_profile():
    """
    Prueba la actualización de perfil con diferentes combinaciones de datos.
    """
    print("🧪 Iniciando pruebas del endpoint de actualización de perfil...")
    
    # Caso 1: Solo actualizar email
    print("\n📧 Caso 1: Actualizar solo email")
    payload = {
        "email": "nuevo_email@test.com"
    }
    
    try:
        response = requests.patch(ENDPOINT, json=payload)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Email actualizado: {data.get('email')}")
            print(f"Mensaje: {data.get('mensaje')}")
        else:
            print(f"❌ Error: {response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor. ¿Está corriendo el backend?")
        return
    
    # Caso 2: Solo actualizar teléfono
    print("\n📱 Caso 2: Actualizar solo teléfono")
    payload = {
        "telefono": "+56987654321"
    }
    
    try:
        response = requests.patch(ENDPOINT, json=payload)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Teléfono actualizado: {data.get('telefono')}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Caso 3: Solo actualizar foto de perfil
    print("\n🖼️ Caso 3: Actualizar solo foto de perfil")
    payload = {
        "foto_perfil": create_test_image_base64()
    }
    
    try:
        response = requests.patch(ENDPOINT, json=payload)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            foto_perfil = data.get('foto_perfil')
            if foto_perfil:
                print(f"✅ Foto de perfil actualizada (longitud: {len(foto_perfil)} caracteres)")
                print(f"Formato: {foto_perfil[:50]}...")
            else:
                print("✅ Foto de perfil actualizada (sin datos en respuesta)")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Caso 4: Actualizar todo
    print("\n🔄 Caso 4: Actualizar email, teléfono y foto")
    payload = {
        "email": "completo@test.com",
        "telefono": "+56912345678",
        "foto_perfil": create_test_image_base64()
    }
    
    try:
        response = requests.patch(ENDPOINT, json=payload)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Todos los datos actualizados:")
            print(f"  Email: {data.get('email')}")
            print(f"  Teléfono: {data.get('telefono')}")
            print(f"  Foto: {'Sí' if data.get('foto_perfil') else 'No'}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Caso 5: Foto inválida
    print("\n❌ Caso 5: Foto inválida (formato incorrecto)")
    payload = {
        "foto_perfil": "imagen_invalida"
    }
    
    try:
        response = requests.patch(ENDPOINT, json=payload)
        print(f"Status: {response.status_code}")
        if response.status_code == 400:
            print("✅ Error de validación detectado correctamente")
            print(f"Detalle: {response.json().get('detail')}")
        else:
            print(f"❌ Se esperaba error 400, pero se obtuvo: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_update_profile()

