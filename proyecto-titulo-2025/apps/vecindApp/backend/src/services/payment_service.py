"""
Servicio orquestador de pagos.

Este servicio coordina todas las operaciones de pago, manteniéndose
agnóstico al proveedor específico (MercadoPago, Stripe, etc.).
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Tuple, Dict, Any
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from src.database.models.payment_intent import PaymentIntent, PaymentIntentStatus
from src.database.models.payment_transaction import PaymentTransaction, PaymentTransactionStatus
from src.database.models.usuario import Usuario
from src.database.models.vecino import Vecino
from src.services.webpay_service import WebpayService
from src.schemas.payment_schemas import (
    PaymentIntentResponse,
    PaymentStatusResponse,
    PaymentTransactionResponse
)


logger = logging.getLogger(__name__)


class PaymentService:
    """
    Servicio orquestador de pagos.
    
    Coordina la creación de intenciones de pago, transacciones
    y mantiene el estado consistente independientemente del proveedor.
    """
    
    def __init__(self, db: AsyncSession):
        """Inicializa el servicio con la sesión de base de datos."""
        self.db = db
        self.webpay_service = WebpayService()

    async def create_payment_intent(
        self,
        user_id: int,
        entity_type: str,
        entity_id: int,
        amount: Decimal,
        description: str,
        extra_data: Optional[dict] = None
    ) -> PaymentIntentResponse:
        """
        Crea una nueva intención de pago.
        
        Args:
            user_id: ID del usuario
            entity_type: Tipo de entidad (certificado, reserva)
            entity_id: ID de la entidad
            amount: Monto del pago
            description: Descripción del pago
            extra_data: Metadata adicional
            
        Returns:
            Respuesta con la intención de pago creada
            
        Raises:
            ValueError: Si hay error en los datos o ya existe una intención activa
        """
        try:
            # 1. Verificar que el usuario existe
            user = await self._get_user_with_vecino(user_id)
            if not user:
                raise ValueError("Usuario no encontrado")
            
            # 2. Verificar si ya existe una intención activa para esta entidad
            existing_intent = await self._get_active_payment_intent(entity_type, entity_id)
            if existing_intent:
                logger.info(f"♻️ Reutilizando intención de pago activa: {existing_intent.id_payment_intent}")
                return PaymentIntentResponse.from_payment_intent(existing_intent)
            
            # 3. Crear nueva intención de pago
            payment_intent = PaymentIntent(
                id_usuario=user_id,
                entity_type=entity_type,
                entity_id=entity_id,
                amount=amount,
                description=description,
                extra_data=extra_data or {}
            )
            
            self.db.add(payment_intent)
            await self.db.flush()  # Para obtener el ID
            
            logger.info(f"💳 Intención de pago creada: {payment_intent.id_payment_intent}")
            
            # 4. Crear preferencia en MercadoPago
            try:
                user_email = user.vecino.email if user.vecino else user.email
                
                preference_id, init_point, sandbox_init_point = await self._create_mp_preference(
                    payment_intent, user_email
                )
                
                # 5. Actualizar intención con datos de MercadoPago
                payment_intent.mp_preference_id = preference_id
                payment_intent.mp_init_point = init_point
                payment_intent.mp_sandbox_init_point = sandbox_init_point
                
                await self.db.commit()
                
                logger.info(f"✅ Intención de pago configurada con MP: {preference_id}")
                
            except Exception as mp_error:
                await self.db.rollback()
                logger.error(f"❌ Error configurando MercadoPago: {str(mp_error)}")
                raise ValueError(f"Error creando preferencia de pago: {str(mp_error)}")
            
            # 6. Refrescar y retornar
            await self.db.refresh(payment_intent)
            return PaymentIntentResponse.from_payment_intent(payment_intent)
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"💥 Error creando intención de pago: {str(e)}")
            raise

    async def create_webpay_payment_intent(
        self,
        user_id: int,
        entity_type: str,
        entity_id: int,
        amount: Decimal,
        description: str,
        extra_data: Optional[dict] = None
    ) -> Tuple[PaymentIntentResponse, str, str]:
        """
        Crea una nueva intención de pago usando Webpay Plus.
        
        Returns:
            Tupla (PaymentIntentResponse, webpay_url, webpay_token)
        """
        try:
            # 1. Verificar que el usuario existe
            user = await self._get_user_with_vecino(user_id)
            if not user:
                raise ValueError("Usuario no encontrado")
            
            # 2. Crear la intención de pago en la base de datos
            payment_intent = PaymentIntent(
                id_usuario=user_id,
                entity_type=entity_type,
                entity_id=entity_id,
                amount=amount,
                description=description,
                extra_data=extra_data or {}
            )
            
            self.db.add(payment_intent)
            await self.db.flush()  # Para obtener el ID
            
            # 3. Crear transacción en Webpay
            # buy_order máximo 26 caracteres
            timestamp = datetime.now(timezone.utc).strftime('%m%d%H%M%S')
            order_id = f"pi{payment_intent.id_payment_intent}_{timestamp}"
            
            token, webpay_url = self.webpay_service.create_transaction(
                payment_intent_id=payment_intent.id_payment_intent,
                amount=amount,
                order_id=order_id
            )
            
            # 4. Actualizar la intención de pago con los datos de Webpay
            payment_intent.extra_data = payment_intent.extra_data or {}
            payment_intent.extra_data.update({
                "webpay_token": token,
                "webpay_order_id": order_id,
                "provider": "webpay"
            })
            
            await self.db.commit()
            await self.db.refresh(payment_intent)
            
            logger.info(f"✅ PaymentIntent con Webpay creado: {payment_intent.id_payment_intent}")
            logger.info(f"🔍 Extra data después del commit: {payment_intent.extra_data}")
            
            payment_response = PaymentIntentResponse.from_payment_intent(payment_intent)
            logger.info(f"🔍 Extra data en respuesta: {payment_response.extra_data}")
            
            return payment_response, webpay_url, token
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"💥 Error creando intención de pago Webpay: {str(e)}")
            raise

    async def update_payment_intent_status(
        self,
        payment_intent_id: int,
        new_status: PaymentIntentStatus,
        external_id: Optional[str] = None,
        response_payload: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Actualiza el estado de una intención de pago.
        
        Args:
            payment_intent_id: ID de la intención de pago
            new_status: Nuevo estado
            external_id: ID externo del proveedor
            response_payload: Datos de respuesta del proveedor
        """
        try:
            # Obtener la intención de pago
            result = await self.db.execute(
                select(PaymentIntent).where(PaymentIntent.id_payment_intent == payment_intent_id)
            )
            payment_intent = result.scalar_one_or_none()
            
            if not payment_intent:
                logger.error(f"❌ PaymentIntent {payment_intent_id} no encontrado")
                return
            
            # Actualizar estado
            payment_intent.status = new_status.value
            payment_intent.updated_at = datetime.now(timezone.utc)
            
            # Crear transacción si es necesario
            if external_id and response_payload:
                transaction = PaymentTransaction(
                    id_payment_intent=payment_intent_id,
                    provider="webpay",
                    external_id=external_id,
                    amount=payment_intent.amount,
                    currency=payment_intent.currency,
                    status=PaymentTransactionStatus.APPROVED.value if new_status == PaymentIntentStatus.COMPLETED else PaymentTransactionStatus.REJECTED.value,
                    processed_at=datetime.now(timezone.utc),
                    raw_data=response_payload  # Cambiar response_payload por raw_data
                )
                self.db.add(transaction)
            
            await self.db.commit()
            logger.info(f"✅ PaymentIntent {payment_intent_id} actualizado a {new_status.value}")
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"💥 Error actualizando PaymentIntent: {str(e)}")
            raise

    async def get_payment_intent(self, payment_intent_id: int) -> Optional[PaymentIntentResponse]:
        """
        Obtiene una intención de pago por ID.
        
        Args:
            payment_intent_id: ID de la intención de pago
            
        Returns:
            Intención de pago o None si no existe
        """
        result = await self.db.execute(
            select(PaymentIntent)
            .where(PaymentIntent.id_payment_intent == payment_intent_id)
        )
        payment_intent = result.scalar_one_or_none()
        
        if not payment_intent:
            return None
        
        return PaymentIntentResponse.from_payment_intent(payment_intent)

    async def get_payment_status(self, payment_intent_id: int) -> Optional[PaymentStatusResponse]:
        """
        Obtiene el estado completo de un pago.
        
        Args:
            payment_intent_id: ID de la intención de pago
            
        Returns:
            Estado completo del pago o None si no existe
        """
        # Obtener intención con transacciones
        result = await self.db.execute(
            select(PaymentIntent)
            .options(selectinload(PaymentIntent.transactions))
            .where(PaymentIntent.id_payment_intent == payment_intent_id)
        )
        payment_intent = result.scalar_one_or_none()
        
        if not payment_intent:
            return None
        
        # Convertir transacciones a response
        transactions = [
            PaymentTransactionResponse.from_attributes(transaction)
            for transaction in payment_intent.transactions
        ]
        
        # Obtener última transacción
        latest_transaction = None
        if transactions:
            latest_transaction = max(transactions, key=lambda t: t.created_at)
        
        return PaymentStatusResponse(
            payment_intent=PaymentIntentResponse.from_payment_intent(payment_intent),
            transactions=transactions,
            latest_transaction=latest_transaction
        )

    async def retry_payment(self, payment_intent_id: int) -> PaymentIntentResponse:
        """
        Reintenta un pago fallido o expirado.
        
        Args:
            payment_intent_id: ID de la intención de pago
            
        Returns:
            Intención de pago actualizada
            
        Raises:
            ValueError: Si no se puede reintentar
        """
        # Obtener intención
        result = await self.db.execute(
            select(PaymentIntent)
            .where(PaymentIntent.id_payment_intent == payment_intent_id)
        )
        payment_intent = result.scalar_one_or_none()
        
        if not payment_intent:
            raise ValueError("Intención de pago no encontrada")
        
        if not payment_intent.can_retry():
            raise ValueError(f"No se puede reintentar el pago en estado: {payment_intent.status}")
        
        try:
            # Obtener datos del usuario
            user = await self._get_user_with_vecino(payment_intent.id_usuario)
            user_email = user.vecino.email if user.vecino else user.email
            
            # Crear nueva preferencia en MercadoPago
            preference_id, init_point, sandbox_init_point = await self._create_mp_preference(
                payment_intent, user_email
            )
            
            # Actualizar intención
            payment_intent.mp_preference_id = preference_id
            payment_intent.mp_init_point = init_point
            payment_intent.mp_sandbox_init_point = sandbox_init_point
            payment_intent.status = PaymentIntentStatus.PENDING.value
            payment_intent.expires_at = datetime.now() + timedelta(minutes=30)
            
            await self.db.commit()
            
            logger.info(f"🔄 Pago reintentado: {payment_intent_id}")
            
            return PaymentIntentResponse.from_payment_intent(payment_intent)
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"💥 Error reintentando pago: {str(e)}")
            raise ValueError(f"Error reintentando pago: {str(e)}")

    async def cancel_payment_intent(self, payment_intent_id: int) -> bool:
        """
        Cancela una intención de pago.
        
        Args:
            payment_intent_id: ID de la intención de pago
            
        Returns:
            True si se canceló exitosamente
        """
        result = await self.db.execute(
            select(PaymentIntent)
            .where(PaymentIntent.id_payment_intent == payment_intent_id)
        )
        payment_intent = result.scalar_one_or_none()
        
        if not payment_intent:
            return False
        
        if payment_intent.status in [PaymentIntentStatus.COMPLETED.value]:
            raise ValueError("No se puede cancelar un pago completado")
        
        payment_intent.status = PaymentIntentStatus.CANCELLED.value
        await self.db.commit()
        
        logger.info(f"❌ Intención de pago cancelada: {payment_intent_id}")
        return True

    async def expire_old_payment_intents(self) -> int:
        """
        Expira intenciones de pago antiguas.
        
        Returns:
            Número de intenciones expiradas
        """
        result = await self.db.execute(
            select(PaymentIntent)
            .where(
                and_(
                    PaymentIntent.status == PaymentIntentStatus.PENDING.value,
                    PaymentIntent.expires_at < datetime.now()
                )
            )
        )
        expired_intents = result.scalars().all()
        
        count = 0
        for intent in expired_intents:
            intent.status = PaymentIntentStatus.EXPIRED.value
            count += 1
        
        if count > 0:
            await self.db.commit()
            logger.info(f"⏰ {count} intenciones de pago expiradas")
        
        return count

    async def get_user_payment_intents(
        self,
        user_id: int,
        entity_type: Optional[str] = None,
        limit: int = 10
    ) -> List[PaymentIntentResponse]:
        """
        Obtiene las intenciones de pago de un usuario.
        
        Args:
            user_id: ID del usuario
            entity_type: Filtrar por tipo de entidad (opcional)
            limit: Límite de resultados
            
        Returns:
            Lista de intenciones de pago
        """
        query = select(PaymentIntent).where(PaymentIntent.id_usuario == user_id)
        
        if entity_type:
            query = query.where(PaymentIntent.entity_type == entity_type)
        
        query = query.order_by(PaymentIntent.created_at.desc()).limit(limit)
        
        result = await self.db.execute(query)
        payment_intents = result.scalars().all()
        
        return [
            PaymentIntentResponse.from_payment_intent(intent)
            for intent in payment_intents
        ]

    # ========================================================================
    # Métodos privados
    # ========================================================================

    async def _get_user_with_vecino(self, user_id: int) -> Optional[Usuario]:
        """Obtiene usuario con datos de vecino."""
        result = await self.db.execute(
            select(Usuario)
            .options(selectinload(Usuario.vecino))
            .where(Usuario.id_usuario == user_id)
        )
        return result.scalar_one_or_none()

    async def _get_active_payment_intent(
        self,
        entity_type: str,
        entity_id: int
    ) -> Optional[PaymentIntent]:
        """Obtiene intención de pago activa para una entidad."""
        result = await self.db.execute(
            select(PaymentIntent)
            .where(
                and_(
                    PaymentIntent.entity_type == entity_type,
                    PaymentIntent.entity_id == entity_id,
                    or_(
                        PaymentIntent.status == PaymentIntentStatus.PENDING.value,
                        PaymentIntent.status == PaymentIntentStatus.PROCESSING.value
                    ),
                    PaymentIntent.expires_at > datetime.now(timezone.utc)
                )
            )
        )
        return result.scalar_one_or_none()

    async def _create_mp_preference(
        self,
        payment_intent: PaymentIntent,
        user_email: str
    ) -> Tuple[str, str, Optional[str]]:
        """Crea preferencia en MercadoPago."""
        return self.mp_service.create_preference(
            payment_intent_id=payment_intent.id_payment_intent,
            amount=payment_intent.amount,
            description=payment_intent.description,
            user_email=user_email,
            extra_data=payment_intent.extra_data
        )
