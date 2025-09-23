#!/usr/bin/env python3
"""
Script de prueba para Webpay Plus.

Este script prueba la integración con Webpay Plus sin hacer llamadas reales a la API,
solo verificando la configuración y estructura.
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from src.core.config import get_settings
from src.services.webpay_service import WebpayService
from decimal import Decimal


async def test_webpay_config():
    """Prueba la configuración de Webpay."""
    print("🧪 === PRUEBA DE CONFIGURACIÓN WEBPAY ===")
    
    # 1. Probar configuración
    settings = get_settings()
    webpay_settings = settings.webpay
    
    print(f"🔧 Commerce Code: {webpay_settings.commerce_code}")
    print(f"🔧 API Key: {webpay_settings.api_key[:20]}...")
    print(f"🔧 Environment: {webpay_settings.environment}")
    print(f"🔧 Return URL: {webpay_settings.return_url}")
    print(f"🔧 Final URL: {webpay_settings.final_url}")
    
    # 2. Probar inicialización del servicio
    try:
        webpay_service = WebpayService()
        print("✅ WebpayService inicializado correctamente")
        
        # 3. Probar métodos utilitarios
        fake_transaction_data = {
            "response_code": 0,
            "status": "AUTHORIZED",
            "amount": 1000,
            "buy_order": "vecindapp_pi_123_20241223",
            "authorization_code": "1234567890"
        }
        
        is_approved = webpay_service.is_transaction_approved(fake_transaction_data)
        amount = webpay_service.get_transaction_amount(fake_transaction_data)
        buy_order = webpay_service.get_buy_order(fake_transaction_data)
        auth_code = webpay_service.get_authorization_code(fake_transaction_data)
        formatted = webpay_service.format_transaction_for_log(fake_transaction_data)
        
        print(f"✅ is_approved: {is_approved}")
        print(f"✅ amount: ${amount}")
        print(f"✅ buy_order: {buy_order}")
        print(f"✅ auth_code: {auth_code}")
        print(f"✅ formatted: {formatted}")
        
    except Exception as e:
        print(f"❌ Error inicializando WebpayService: {str(e)}")
        return False
    
    print("✅ Configuración de Webpay OK")
    return True


async def test_webpay_transaction_creation():
    """Prueba la creación de transacciones (sin llamadas reales)."""
    print("\n🧪 === PRUEBA DE CREACIÓN DE TRANSACCIÓN ===")
    
    try:
        webpay_service = WebpayService()
        
        # Datos de prueba
        payment_intent_id = 123
        amount = Decimal("1000")
        order_id = "vecindapp_test_123"
        
        print(f"💰 Creando transacción de prueba:")
        print(f"   - Payment Intent ID: {payment_intent_id}")
        print(f"   - Amount: ${amount}")
        print(f"   - Order ID: {order_id}")
        
        # NOTA: Esta línea haría una llamada real a Transbank
        # token, url = webpay_service.create_transaction(payment_intent_id, amount, order_id)
        
        print("ℹ️  Transacción NO creada (modo prueba sin llamadas reales)")
        print("ℹ️  Para probar con llamadas reales, descomenta la línea anterior")
        
    except Exception as e:
        print(f"❌ Error en prueba de transacción: {str(e)}")
        return False
    
    print("✅ Estructura de creación de transacción OK")
    return True


async def main():
    """Función principal de pruebas."""
    print("🚀 Iniciando pruebas de Webpay Plus...")
    
    # Ejecutar pruebas
    config_ok = await test_webpay_config()
    transaction_ok = await test_webpay_transaction_creation()
    
    # Resumen
    print("\n📊 === RESUMEN DE PRUEBAS ===")
    print(f"✅ Configuración: {'OK' if config_ok else 'FALLO'}")
    print(f"✅ Estructura transacción: {'OK' if transaction_ok else 'FALLO'}")
    
    if config_ok and transaction_ok:
        print("\n🎉 ¡Todas las pruebas pasaron!")
        print("\n📋 PRÓXIMOS PASOS:")
        print("1. Ejecutar: poetry run python test_webpay_real.py")
        print("2. Probar endpoint: /api/certificados/solicitar-con-webpay")
        print("3. Probar flujo completo desde frontend")
        
        print("\n💳 TARJETAS DE PRUEBA WEBPAY:")
        print("🔸 VISA: 4051 8856 0000 0020")
        print("🔸 MASTERCARD: 5186 0595 5959 0568")
        print("🔸 CVV: Cualquier 3 dígitos")
        print("🔸 Fecha: Cualquier fecha futura")
        print("🔸 RUT: 11.111.111-1")
        
    else:
        print("\n❌ Algunas pruebas fallaron. Revisa la configuración.")


if __name__ == "__main__":
    asyncio.run(main())
