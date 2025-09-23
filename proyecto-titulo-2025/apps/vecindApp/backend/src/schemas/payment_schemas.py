"""
Schemas para el sistema de pagos.

Define los DTOs (Data Transfer Objects) para requests y responses
del sistema de pagos con MercadoPago.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator


# ============================================================================
# Request Schemas
# ============================================================================

class PaymentIntentCreateRequest(BaseModel):
    """Request para crear una intención de pago."""
    
    entity_type: str = Field(..., description="Tipo de entidad (certificado, reserva)")
    entity_id: int = Field(..., description="ID de la entidad")
    amount: Decimal = Field(..., gt=0, description="Monto del pago en CLP")
    description: str = Field(..., min_length=1, max_length=255, description="Descripción del pago")
    extra_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Metadata adicional")

    @validator('entity_type')
    def validate_entity_type(cls, v):
        allowed_types = ['certificado', 'reserva']
        if v not in allowed_types:
            raise ValueError(f'entity_type debe ser uno de: {allowed_types}')
        return v


class PaymentRetryRequest(BaseModel):
    """Request para reintentar un pago."""
    
    payment_intent_id: int = Field(..., description="ID de la intención de pago a reintentar")


# ============================================================================
# Response Schemas
# ============================================================================

class PaymentIntentResponse(BaseModel):
    """Response con datos de una intención de pago."""
    
    id_payment_intent: int
    entity_type: str
    entity_id: int
    amount: Decimal
    currency: str
    description: str
    status: str
    created_at: datetime
    updated_at: datetime
    expires_at: datetime
    
    # URLs de MercadoPago
    mp_preference_id: Optional[str] = None
    mp_init_point: Optional[str] = None
    mp_sandbox_init_point: Optional[str] = None
    
    # Estado calculado
    is_expired: bool
    is_active: bool
    can_retry: bool
    
    extra_data: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_payment_intent(cls, payment_intent):
        """Crea la respuesta desde un modelo PaymentIntent."""
        return cls(
            id_payment_intent=payment_intent.id_payment_intent,
            entity_type=payment_intent.entity_type,
            entity_id=payment_intent.entity_id,
            amount=payment_intent.amount,
            currency=payment_intent.currency,
            description=payment_intent.description,
            status=payment_intent.status,
            created_at=payment_intent.created_at,
            updated_at=payment_intent.updated_at,
            expires_at=payment_intent.expires_at,
            mp_preference_id=payment_intent.mp_preference_id,
            mp_init_point=payment_intent.mp_init_point,
            mp_sandbox_init_point=payment_intent.mp_sandbox_init_point,
            is_expired=payment_intent.is_expired(),
            is_active=payment_intent.is_active(),
            can_retry=payment_intent.can_retry(),
            extra_data=payment_intent.extra_data
        )


class PaymentTransactionResponse(BaseModel):
    """Response con datos de una transacción de pago."""
    
    id_payment_transaction: int
    id_payment_intent: int
    provider: str
    external_id: Optional[str]
    amount: Decimal
    currency: str
    status: str
    payment_method_id: Optional[str]
    payment_type_id: Optional[str]
    installments: Optional[int]
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime]
    payer_email: Optional[str]

    class Config:
        from_attributes = True


class PaymentStatusResponse(BaseModel):
    """Response con el estado completo de un pago."""
    
    payment_intent: PaymentIntentResponse
    transactions: List[PaymentTransactionResponse] = []
    latest_transaction: Optional[PaymentTransactionResponse] = None

    class Config:
        from_attributes = True


class WebhookEventResponse(BaseModel):
    """Response con datos de un evento de webhook."""
    
    id_webhook_event: int
    provider: str
    external_id: str
    event_type: str
    status: str
    received_at: datetime
    processed_at: Optional[datetime]
    processing_attempts: int
    last_error: Optional[str]

    class Config:
        from_attributes = True


# ============================================================================
# MercadoPago Specific Schemas
# ============================================================================

class MercadoPagoPreferenceItem(BaseModel):
    """Item para preferencia de MercadoPago."""
    
    id: str
    title: str
    quantity: int = 1
    unit_price: float
    currency_id: str = "CLP"


class MercadoPagoPreferenceRequest(BaseModel):
    """Request para crear preferencia en MercadoPago."""
    
    items: List[MercadoPagoPreferenceItem]
    external_reference: str
    notification_url: Optional[str] = None
    back_urls: Optional[Dict[str, str]] = None
    auto_return: str = "approved"
    
    # Configuraciones adicionales
    expires: bool = True
    expiration_date_from: Optional[str] = None
    expiration_date_to: Optional[str] = None


class MercadoPagoWebhookPayload(BaseModel):
    """Payload de webhook de MercadoPago."""
    
    id: int
    live_mode: bool
    type: str
    date_created: str
    application_id: int
    user_id: int
    version: int
    api_version: str
    action: str
    data: Dict[str, Any]


# ============================================================================
# Error Schemas
# ============================================================================

class PaymentErrorResponse(BaseModel):
    """Response de error en pagos."""
    
    error: str
    detail: str
    payment_intent_id: Optional[int] = None
    provider_error: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


# ============================================================================
# Debug Schemas
# ============================================================================

class PaymentDebugResponse(BaseModel):
    """Response para debug de pagos (desarrollo)."""
    
    payment_intent: PaymentIntentResponse
    transactions: List[PaymentTransactionResponse]
    webhook_events: List[WebhookEventResponse]
    
    # Información adicional para debug
    total_attempts: int
    last_error: Optional[str]
    mp_preference_data: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
