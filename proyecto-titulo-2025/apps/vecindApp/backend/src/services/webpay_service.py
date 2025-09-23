"""
Servicio para integración con Webpay Plus (Transbank).

Este servicio encapsula toda la lógica específica de Webpay Plus,
manteniendo el resto del sistema agnóstico al proveedor de pagos.
"""

import logging
from typing import Dict, Any, Tuple
from decimal import Decimal

from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.integration_type import IntegrationType
from transbank.common.options import WebpayOptions

from src.core.config import get_settings

logger = logging.getLogger(__name__)


class WebpayService:
    """
    Servicio para operaciones con Webpay Plus.
    
    Encapsula toda la lógica específica de Webpay Plus manteniendo
    una interfaz limpia hacia el resto del sistema.
    """
    
    def __init__(self):
        """Inicializa el servicio con la configuración."""
        self.settings = get_settings()
        self.webpay_settings = self.settings.webpay
        
        # Configurar opciones de Webpay
        if self.webpay_settings.environment == "integration":
            # Usar credenciales de integración por defecto
            self.options = WebpayOptions(
                commerce_code=self.webpay_settings.commerce_code,
                api_key=self.webpay_settings.api_key,
                integration_type=IntegrationType.TEST
            )
            logger.info("🧪 Webpay configurado en modo INTEGRACIÓN")
        else:
            # Configuración de producción
            self.options = WebpayOptions(
                commerce_code=self.webpay_settings.commerce_code,
                api_key=self.webpay_settings.api_key,
                integration_type=IntegrationType.LIVE
            )
            logger.info("🏦 Webpay configurado en modo PRODUCCIÓN")

    def create_transaction(
        self,
        payment_intent_id: int,
        amount: Decimal,
        order_id: str
    ) -> Tuple[str, str]:
        """
        Crea una transacción en Webpay Plus.
        
        Args:
            payment_intent_id: ID de la intención de pago
            amount: Monto del pago en CLP
            order_id: ID único de la orden
            
        Returns:
            Tupla (token, url) donde:
            - token: Token de la transacción
            - url: URL para redirigir al usuario
            
        Raises:
            ValueError: Si hay error al crear la transacción
        """
        try:
            # Convertir amount a entero (Webpay requiere centavos)
            amount_cents = int(amount)
            
            logger.info(f"🔄 Creando transacción Webpay para payment_intent {payment_intent_id}")
            logger.info(f"💰 Monto: ${amount} CLP ({amount_cents} centavos)")
            logger.info(f"🆔 Order ID: {order_id}")
            
            # Crear transacción en Webpay
            transaction = Transaction(self.options)
            response = transaction.create(
                buy_order=order_id,
                session_id=f"session_{payment_intent_id}",
                amount=amount_cents,
                return_url=self.webpay_settings.return_url
            )
            
            token = response.get('token')
            url = response.get('url')
            
            if not token or not url:
                logger.error(f"❌ Respuesta inválida de Webpay: {response}")
                raise ValueError(f"Respuesta inválida de Webpay: {response}")
            
            logger.info(f"✅ Transacción Webpay creada exitosamente")
            logger.info(f"🔗 Token: {token[:20]}...")
            logger.info(f"🌐 URL: {url}")
            
            return token, url
            
        except Exception as e:
            logger.error(f"💥 Error creando transacción Webpay: {str(e)}")
            raise ValueError(f"Error creando transacción Webpay: {str(e)}")

    def confirm_transaction(self, token: str) -> Dict[str, Any]:
        """
        Confirma una transacción usando el token.
        
        Args:
            token: Token de la transacción
            
        Returns:
            Datos de la transacción confirmada
            
        Raises:
            ValueError: Si hay error al confirmar la transacción
        """
        try:
            logger.info(f"🔄 Confirmando transacción Webpay con token: {token[:20]}...")
            
            transaction = Transaction(self.options)
            response = transaction.commit(token)
            
            logger.info(f"✅ Transacción Webpay confirmada")
            logger.debug(f"📋 Respuesta: {response}")
            
            return response
            
        except Exception as e:
            logger.error(f"💥 Error confirmando transacción Webpay: {str(e)}")
            raise ValueError(f"Error confirmando transacción Webpay: {str(e)}")

    def get_transaction_status(self, token: str) -> Dict[str, Any]:
        """
        Obtiene el estado de una transacción.
        
        Args:
            token: Token de la transacción
            
        Returns:
            Estado de la transacción
        """
        try:
            logger.info(f"🔍 Consultando estado de transacción: {token[:20]}...")
            
            transaction = Transaction(self.options)
            response = transaction.status(token)
            
            logger.info(f"📊 Estado obtenido exitosamente")
            logger.debug(f"📋 Estado: {response}")
            
            return response
            
        except Exception as e:
            logger.error(f"💥 Error consultando estado: {str(e)}")
            raise ValueError(f"Error consultando estado: {str(e)}")

    def is_transaction_approved(self, transaction_data: Dict[str, Any]) -> bool:
        """
        Verifica si una transacción fue aprobada.
        
        Args:
            transaction_data: Datos de la transacción
            
        Returns:
            True si la transacción fue aprobada
        """
        response_code = transaction_data.get('response_code')
        status = transaction_data.get('status')
        
        # En Webpay, response_code = 0 significa aprobado
        # status = "AUTHORIZED" también indica aprobación
        is_approved = (
            response_code == 0 or 
            response_code == "0" or 
            status == "AUTHORIZED"
        )
        
        logger.info(f"💳 Transacción aprobada: {is_approved} (response_code: {response_code}, status: {status})")
        
        return is_approved

    def get_transaction_amount(self, transaction_data: Dict[str, Any]) -> Decimal:
        """
        Obtiene el monto de una transacción.
        
        Args:
            transaction_data: Datos de la transacción
            
        Returns:
            Monto de la transacción en CLP
        """
        amount = transaction_data.get('amount', 0)
        # Webpay devuelve el monto en centavos, convertir a pesos
        return Decimal(amount)

    def get_buy_order(self, transaction_data: Dict[str, Any]) -> str:
        """
        Obtiene el buy_order de una transacción.
        
        Args:
            transaction_data: Datos de la transacción
            
        Returns:
            Buy order de la transacción
        """
        return transaction_data.get('buy_order', '')

    def get_authorization_code(self, transaction_data: Dict[str, Any]) -> str:
        """
        Obtiene el código de autorización de una transacción.
        
        Args:
            transaction_data: Datos de la transacción
            
        Returns:
            Código de autorización
        """
        return transaction_data.get('authorization_code', '')

    def format_transaction_for_log(self, transaction_data: Dict[str, Any]) -> str:
        """
        Formatea los datos de transacción para logging.
        
        Args:
            transaction_data: Datos de la transacción
            
        Returns:
            String formateado para logging
        """
        buy_order = self.get_buy_order(transaction_data)
        amount = self.get_transaction_amount(transaction_data)
        auth_code = self.get_authorization_code(transaction_data)
        response_code = transaction_data.get('response_code')
        
        return f"Buy Order: {buy_order}, Amount: ${amount}, Auth: {auth_code}, Code: {response_code}"
