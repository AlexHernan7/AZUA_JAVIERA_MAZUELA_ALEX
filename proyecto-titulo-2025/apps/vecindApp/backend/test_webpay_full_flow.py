#!/usr/bin/env python3
"""
Script de prueba para el endpoint de certificados con Webpay.

Este script simula el flujo completo desde el frontend.
"""

import asyncio
import httpx
from sqlalchemy.ext.asyncio import create_async_engine
from src.core.config import get_settings


async def test_webpay_certificate_endpoint():
    """Prueba el endpoint /solicitar-con-webpay."""
    print("🚀 === PRUEBA ENDPOINT CERTIFICADO CON WEBPAY ===")
    
    # 1. Configuración
    settings = get_settings()
    base_url = "http://localhost:8000/api"
    
    # 2. Datos de login (usa tus credenciales)
    login_data = {
        "email": "aaaa@gmail.com",  # Usuario con perfil de vecino
        "password": "Alex5341708+"  # Contraseña correcta
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # 3. Login para obtener token
            print("🔐 Haciendo login...")
            login_response = await client.post(f"{base_url}/auth/login", json=login_data)
            
            if login_response.status_code != 200:
                print(f"❌ Error en login: {login_response.status_code}")
                print(f"📋 Respuesta: {login_response.text}")
                return False
            
            login_result = login_response.json()
            token = login_result["access_token"]
            print(f"✅ Login exitoso, token: {token[:20]}...")
            
            # 4. Solicitar certificado con Webpay
            print("\n📄 Solicitando certificado con Webpay...")
            
            headers = {"Authorization": f"Bearer {token}"}
            certificate_data = {
                "motivo_solicitud": "Prueba de certificado con Webpay Plus"
            }
            
            cert_response = await client.post(
                f"{base_url}/certificados/webpay-payment",
                json=certificate_data,
                headers=headers
            )
            
            if cert_response.status_code != 201:
                print(f"❌ Error solicitando certificado: {cert_response.status_code}")
                print(f"📋 Respuesta: {cert_response.text}")
                return False
            
            cert_result = cert_response.json()
            
            print(f"✅ ¡Certificado con Webpay creado exitosamente!")
            print(f"📋 Pedido ID: {cert_result['pedido']['id_pedido']}")
            print(f"💳 Payment Intent ID: {cert_result['payment_intent']['id_payment_intent']}")
            print(f"💰 Monto: ${cert_result['payment_intent']['amount']} CLP")
            print(f"🔗 URL de pago: {cert_result['payment_url']}")
            print(f"🏦 Proveedor: {cert_result['provider']}")
            
            # Mostrar extra_data para ver el token
            print(f"\n🔍 EXTRA DATA:")
            extra_data = cert_result['payment_intent'].get('extra_data', {})
            for key, value in extra_data.items():
                if key == 'webpay_token':
                    print(f"   🔑 {key}: {str(value)[:50]}...")
                else:
                    print(f"   📋 {key}: {value}")
            
            print(f"\n📋 RESPUESTA COMPLETA:")
            import json
            print(json.dumps(cert_result, indent=2))
            
            print(f"\n🎯 PARA COMPLETAR EL PAGO:")
            print(f"1. Abre esta URL en tu navegador:")
            print(f"   {cert_result['payment_url']}")
            print(f"\n2. Usa estas tarjetas de prueba:")
            print(f"   🔸 VISA: 4051 8856 0000 0020")
            print(f"   🔸 MASTERCARD: 5186 0595 5959 0568")
            print(f"   🔸 CVV: 123")
            print(f"   🔸 Fecha: 12/25")
            print(f"   🔸 RUT: 11.111.111-1")
            
            return True
            
        except Exception as e:
            print(f"❌ Error en la prueba: {str(e)}")
            return False


async def main():
    """Función principal."""
    print("🧪 Iniciando prueba completa de Webpay...")
    
    success = await test_webpay_certificate_endpoint()
    
    print(f"\n📊 === RESULTADO FINAL ===")
    if success:
        print("🎉 ¡Endpoint funcionando correctamente!")
        print("🔄 Ahora puedes actualizar el frontend para usar Webpay")
    else:
        print("❌ El endpoint falló")
        print("💡 Verifica que el servidor esté corriendo y la configuración sea correcta")


if __name__ == "__main__":
    asyncio.run(main())
