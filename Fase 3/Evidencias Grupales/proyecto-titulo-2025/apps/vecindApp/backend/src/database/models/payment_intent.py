"""
Modelo PaymentIntent - Intención de pago separada del objeto de negocio.

Este modelo representa la intención de realizar un pago, independiente del
certificado o reserva. Permite reintentos y manejo de estados limpio.
"""

from datetime import datetime, timedelta, timezone
from enum import Enum
from sqlalchemy import (
    Column,
    BigInteger,
    Text,
    Numeric,
    DateTime,
    CheckConstraint,
    ForeignKey,
    func,
    JSON,
)
from sqlalchemy.orm import relationship
from src.database import Base


class PaymentIntentStatus(Enum):
    """Estados posibles de una intención de pago."""
    PENDING = "pending"        # Creado, esperando pago
    PROCESSING = "processing"  # En proceso en MercadoPago
    COMPLETED = "completed"    # Pago completado exitosamente
    FAILED = "failed"         # Pago falló
    EXPIRED = "expired"       # Expiró por timeout
    CANCELLED = "cancelled"   # Cancelado por usuario


class PaymentIntent(Base):
    """
    Intención de pago independiente del objeto de negocio.
    
    Permite múltiples intentos de pago para el mismo certificado/reserva
    sin bloquear el objeto de negocio.
    """

    __tablename__ = "payment_intent"
    __table_args__ = (
        CheckConstraint(
            "status = ANY (ARRAY['pending'::text, 'processing'::text, 'completed'::text, 'failed'::text, 'expired'::text, 'cancelled'::text])",
            name="ck_payment_intent_status"
        ),
        CheckConstraint(
            "entity_type = ANY (ARRAY['certificado'::text, 'reserva'::text])",
            name="ck_payment_intent_entity_type"
        ),
        CheckConstraint("amount > 0", name="ck_payment_intent_amount_positive"),
        {"schema": "vecindapp"}
    )

    id_payment_intent = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # Referencia al usuario que inicia el pago
    id_usuario = Column(
        BigInteger,
        ForeignKey("vecindapp.usuario.id_usuario", ondelete="CASCADE"),
        nullable=False
    )
    
    # Referencia al objeto de negocio (certificado, reserva, etc.)
    entity_type = Column(Text, nullable=False)  # 'certificado', 'reserva'
    entity_id = Column(BigInteger, nullable=False)  # ID del certificado/reserva
    
    # Datos del pago
    amount = Column(Numeric(10, 2), nullable=False)  # Monto en CLP
    currency = Column(Text, nullable=False, default="CLP")
    description = Column(Text, nullable=False)
    
    # Estado y timestamps
    status = Column(Text, nullable=False, default=PaymentIntentStatus.PENDING.value)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    # Datos específicos de MercadoPago
    mp_preference_id = Column(Text)  # ID de preferencia en MercadoPago
    mp_init_point = Column(Text)     # URL para iniciar pago
    mp_sandbox_init_point = Column(Text)  # URL sandbox
    
    # Metadata adicional (JSON)
    extra_data = Column(JSON, default=dict)
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="payment_intents")
    transactions = relationship("PaymentTransaction", back_populates="payment_intent", cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        """Inicializa PaymentIntent con expiración automática."""
        super().__init__(**kwargs)
        if not self.expires_at:
            # Expira en 30 minutos por defecto
            self.expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)

    def is_expired(self) -> bool:
        """Verifica si la intención de pago ha expirado."""
        return datetime.now(timezone.utc) > self.expires_at

    def can_retry(self) -> bool:
        """Verifica si se puede reintentar el pago."""
        return self.status in [
            PaymentIntentStatus.FAILED.value,
            PaymentIntentStatus.EXPIRED.value,
            PaymentIntentStatus.CANCELLED.value
        ]

    def is_active(self) -> bool:
        """Verifica si la intención de pago está activa."""
        return (
            self.status in [PaymentIntentStatus.PENDING.value, PaymentIntentStatus.PROCESSING.value]
            and not self.is_expired()
        )

    def __repr__(self) -> str:
        return f"<PaymentIntent(id={self.id_payment_intent}, entity={self.entity_type}:{self.entity_id}, status='{self.status}', amount={self.amount})>"
