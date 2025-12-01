"""
Modelo WebhookEvent - Registro de eventos de webhook para idempotencia.

Este modelo previene el procesamiento duplicado de webhooks
y permite auditoría completa de eventos.
"""

from enum import Enum
from sqlalchemy import (
    Column,
    BigInteger,
    Text,
    DateTime,
    CheckConstraint,
    func,
    JSON,
    Index,
)
from src.database import Base


class WebhookEventStatus(Enum):
    """Estados de procesamiento de un webhook."""
    RECEIVED = "received"       # Recibido, no procesado
    PROCESSING = "processing"   # En proceso
    PROCESSED = "processed"     # Procesado exitosamente
    FAILED = "failed"          # Falló el procesamiento
    IGNORED = "ignored"        # Ignorado (evento no relevante)


class WebhookEvent(Base):
    """
    Registro de eventos de webhook para garantizar idempotencia.
    
    Cada webhook recibido se registra aquí antes de procesar,
    evitando procesamientos duplicados.
    """

    __tablename__ = "webhook_event"
    __table_args__ = (
        CheckConstraint(
            "status = ANY (ARRAY['received'::text, 'processing'::text, 'processed'::text, 'failed'::text, 'ignored'::text])",
            name="ck_webhook_event_status"
        ),
        CheckConstraint(
            "provider = ANY (ARRAY['mercadopago'::text, 'stripe'::text, 'webpay'::text])",
            name="ck_webhook_event_provider"
        ),
        # Índice único para prevenir duplicados
        Index("ix_webhook_provider_external_id", "provider", "external_id", unique=True),
        {"schema": "vecindapp"}
    )

    id_webhook_event = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # Identificación del webhook
    provider = Column(Text, nullable=False)        # 'mercadopago', 'stripe', etc.
    external_id = Column(Text, nullable=False)     # ID único del webhook en el proveedor
    event_type = Column(Text, nullable=False)      # Tipo de evento (payment.updated, etc.)
    
    # Estado de procesamiento
    status = Column(Text, nullable=False, default=WebhookEventStatus.RECEIVED.value)
    
    # Timestamps
    received_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    processed_at = Column(DateTime(timezone=True))
    
    # Datos del webhook
    raw_payload = Column(JSON, nullable=False)     # Payload completo del webhook
    headers = Column(JSON)                         # Headers HTTP del webhook
    
    # Información de procesamiento
    processing_attempts = Column(BigInteger, default=0)
    last_error = Column(Text)                      # Último error si falló
    
    # Referencia a la transacción procesada (si aplica)
    id_payment_transaction = Column(BigInteger)    # FK soft a payment_transaction

    def mark_as_processing(self):
        """Marca el webhook como en procesamiento."""
        self.status = WebhookEventStatus.PROCESSING.value
        self.processing_attempts += 1

    def mark_as_processed(self, transaction_id: int = None):
        """Marca el webhook como procesado exitosamente."""
        self.status = WebhookEventStatus.PROCESSED.value
        self.processed_at = func.now()
        if transaction_id:
            self.id_payment_transaction = transaction_id

    def mark_as_failed(self, error_message: str):
        """Marca el webhook como fallido."""
        self.status = WebhookEventStatus.FAILED.value
        self.last_error = error_message
        self.processed_at = func.now()

    def mark_as_ignored(self, reason: str):
        """Marca el webhook como ignorado."""
        self.status = WebhookEventStatus.IGNORED.value
        self.last_error = reason
        self.processed_at = func.now()

    def can_retry(self) -> bool:
        """Verifica si se puede reintentar el procesamiento."""
        return (
            self.status == WebhookEventStatus.FAILED.value 
            and self.processing_attempts < 3
        )

    def __repr__(self) -> str:
        return f"<WebhookEvent(id={self.id_webhook_event}, provider='{self.provider}', external_id='{self.external_id}', event_type='{self.event_type}', status='{self.status}')>"
