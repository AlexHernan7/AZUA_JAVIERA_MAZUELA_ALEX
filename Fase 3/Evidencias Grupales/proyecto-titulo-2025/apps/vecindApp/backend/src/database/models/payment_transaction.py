"""
Modelo PaymentTransaction - Registro de transacciones de pago reales.

Este modelo registra cada transacción real con el proveedor de pagos,
permitiendo auditoría completa y manejo de webhooks.
"""

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


class PaymentTransactionStatus(Enum):
    """Estados de una transacción de pago."""
    CREATED = "created"           # Transacción creada
    PENDING = "pending"           # Pendiente en proveedor
    IN_PROCESS = "in_process"     # En proceso
    APPROVED = "approved"         # Aprobada
    REJECTED = "rejected"         # Rechazada
    CANCELLED = "cancelled"       # Cancelada
    REFUNDED = "refunded"         # Reembolsada
    CHARGED_BACK = "charged_back" # Contracargo


class PaymentTransaction(Base):
    """
    Registro de transacciones reales con el proveedor de pagos.
    
    Cada PaymentIntent puede tener múltiples transacciones
    (reintentos, webhooks duplicados, etc.)
    """

    __tablename__ = "payment_transaction"
    __table_args__ = (
        CheckConstraint(
            "status = ANY (ARRAY['created'::text, 'pending'::text, 'in_process'::text, 'approved'::text, 'rejected'::text, 'cancelled'::text, 'refunded'::text, 'charged_back'::text])",
            name="ck_payment_transaction_status"
        ),
        CheckConstraint(
            "provider = ANY (ARRAY['mercadopago'::text, 'stripe'::text, 'webpay'::text])",
            name="ck_payment_transaction_provider"
        ),
        CheckConstraint("amount > 0", name="ck_payment_transaction_amount_positive"),
        {"schema": "vecindapp"}
    )

    id_payment_transaction = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # Referencia al PaymentIntent
    id_payment_intent = Column(
        BigInteger,
        ForeignKey("vecindapp.payment_intent.id_payment_intent", ondelete="CASCADE"),
        nullable=False
    )
    
    # Datos del proveedor
    provider = Column(Text, nullable=False)  # 'mercadopago', 'stripe', etc.
    external_id = Column(Text)               # ID en el proveedor (payment_id de MP)
    external_reference = Column(Text)        # Referencia externa
    
    # Datos de la transacción
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(Text, nullable=False, default="CLP")
    status = Column(Text, nullable=False, default=PaymentTransactionStatus.CREATED.value)
    
    # Detalles del pago
    payment_method_id = Column(Text)         # visa, master, etc.
    payment_type_id = Column(Text)           # credit_card, debit_card, etc.
    installments = Column(BigInteger)        # Número de cuotas
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True))  # Cuando se procesó en el proveedor
    
    # Datos completos del webhook/respuesta (para debug)
    raw_data = Column(JSON)                  # Respuesta completa del proveedor
    
    # Información adicional
    payer_email = Column(Text)
    payer_identification_type = Column(Text)
    payer_identification_number = Column(Text)
    
    # Relaciones
    payment_intent = relationship("PaymentIntent", back_populates="transactions")

    def is_successful(self) -> bool:
        """Verifica si la transacción fue exitosa."""
        return self.status == PaymentTransactionStatus.APPROVED.value

    def is_final_status(self) -> bool:
        """Verifica si el estado es final (no cambiará más)."""
        return self.status in [
            PaymentTransactionStatus.APPROVED.value,
            PaymentTransactionStatus.REJECTED.value,
            PaymentTransactionStatus.CANCELLED.value,
            PaymentTransactionStatus.REFUNDED.value,
            PaymentTransactionStatus.CHARGED_BACK.value
        ]

    def __repr__(self) -> str:
        return f"<PaymentTransaction(id={self.id_payment_transaction}, provider='{self.provider}', external_id='{self.external_id}', status='{self.status}', amount={self.amount})>"
