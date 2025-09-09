"""
Modelo Transaccion para la tabla transaccion.

Representa las transacciones de pago en el sistema VecindApp.
"""

from sqlalchemy import Column, BigInteger, Text, ForeignKey, Numeric, DateTime, CheckConstraint, Index, func
from sqlalchemy.orm import relationship
from src.database import Base


class Transaccion(Base):
    """
    Modelo que representa una transacción de pago.
    
    Attributes:
        id_transaccion: Identificador único de la transacción (BIGSERIAL PRIMARY KEY)
        id_junta: ID de la junta (BIGINT NOT NULL REFERENCES junta)
        id_usuario: ID del usuario que realiza la transacción (BIGINT NOT NULL REFERENCES usuario)
        origen_tipo: Tipo de origen ('certificado_pedido' o 'reserva') (TEXT NOT NULL)
        origen_id: ID del pedido o reserva (BIGINT NOT NULL)
        proveedor: Proveedor de pago (TEXT NOT NULL)
        monto: Monto de la transacción (NUMERIC(14,2) NOT NULL)
        moneda: Moneda de la transacción (TEXT NOT NULL DEFAULT 'CLP')
        estado: Estado de la transacción (TEXT NOT NULL)
        external_id: ID externo del proveedor (TEXT)
        creado_at: Fecha de creación (TIMESTAMPTZ NOT NULL DEFAULT now())
        autorizado_at: Fecha de autorización (TIMESTAMPTZ)
        anulado_at: Fecha de anulación (TIMESTAMPTZ)
        junta: Relación con la junta
        usuario: Relación con el usuario
        pago_externo: Relación con el pago externo
        detalles: Relación con los detalles de la transacción
    """
    
    __tablename__ = "transaccion"
    __table_args__ = (
        CheckConstraint("origen_tipo IN ('certificado_pedido','reserva')", name="ck_tx_origen_tipo"),
        CheckConstraint("proveedor IN ('webpay','mercadopago','paypal')", name="ck_tx_proveedor"),
        CheckConstraint("monto >= 0", name="ck_tx_monto"),
        CheckConstraint("estado IN ('iniciado','autorizado','rechazado','anulado')", name="ck_tx_estado"),
        Index("ix_tx_origen", "id_junta", "origen_tipo", "origen_id"),
        {"schema": "vecindApp"}
    )
    
    id_transaccion = Column(BigInteger, primary_key=True, autoincrement=True)
    id_junta = Column(BigInteger, ForeignKey("vecindApp.junta.id_junta", ondelete="CASCADE"), nullable=False)
    id_usuario = Column(BigInteger, ForeignKey("vecindApp.usuario.id_usuario", ondelete="RESTRICT"), nullable=False)
    origen_tipo = Column(Text, nullable=False)
    origen_id = Column(BigInteger, nullable=False)
    proveedor = Column(Text, nullable=False)
    monto = Column(Numeric(14, 2), nullable=False)
    moneda = Column(Text, nullable=False, default="CLP")
    estado = Column(Text, nullable=False)
    external_id = Column(Text)
    creado_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    autorizado_at = Column(DateTime(timezone=True))
    anulado_at = Column(DateTime(timezone=True))
    
    # Relaciones
    junta = relationship("Junta", back_populates="transacciones")
    usuario = relationship("Usuario", back_populates="transacciones")
    pago_externo = relationship("PagoExterno", back_populates="transaccion", uselist=False)
    detalles = relationship("DetalleTransaccion", back_populates="transaccion", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Transaccion(id_transaccion={self.id_transaccion}, monto={self.monto}, estado='{self.estado}')>"
