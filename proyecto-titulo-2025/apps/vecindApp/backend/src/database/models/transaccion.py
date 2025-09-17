"""Modelo Transaccion - Transacciones del sistema."""

from sqlalchemy import (
    Column,
    BigInteger,
    Text,
    ForeignKey,
    Numeric,
    DateTime,
    CheckConstraint,
    Index,
    func,
)
from sqlalchemy.orm import relationship
from src.database import Base


class Transaccion(Base):
    """Transacción financiera del sistema."""

    __tablename__ = "transaccion"
    __table_args__ = (
        CheckConstraint(
            "origen_tipo IN ('certificado_pedido','reserva')", name="ck_tx_origen_tipo"
        ),
        CheckConstraint(
            "proveedor IN ('webpay','mercadopago','paypal')", name="ck_tx_proveedor"
        ),
        CheckConstraint("monto >= 0", name="ck_tx_monto"),
        CheckConstraint(
            "estado IN ('iniciado','autorizado','rechazado','anulado')",
            name="ck_tx_estado",
        ),
        Index("ix_tx_origen", "id_junta", "origen_tipo", "origen_id"),
        {"schema": "vecindapp"},
    )

    id_transaccion = Column(BigInteger, primary_key=True, autoincrement=True)
    id_junta = Column(
        BigInteger,
        ForeignKey("vecindapp.junta.id_junta", ondelete="CASCADE"),
        nullable=False,
    )
    id_usuario = Column(
        BigInteger,
        ForeignKey("vecindapp.usuario.id_usuario", ondelete="RESTRICT"),
        nullable=False,
    )
    origen_tipo = Column(Text, nullable=False)
    origen_id = Column(BigInteger, nullable=False)
    proveedor = Column(Text, nullable=False)
    monto = Column(Numeric(14, 2), nullable=False)
    moneda = Column(Text, nullable=False, default="CLP")
    estado = Column(Text, nullable=False)
    external_id = Column(Text)
    creado_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    autorizado_at = Column(DateTime(timezone=True))
    anulado_at = Column(DateTime(timezone=True))

    # Relaciones
    junta = relationship("Junta", back_populates="transacciones")
    usuario = relationship("Usuario", back_populates="transacciones")
    pago_externo = relationship(
        "PagoExterno", back_populates="transaccion", uselist=False
    )
    detalles = relationship(
        "DetalleTransaccion", back_populates="transaccion", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Transaccion(id_transaccion={self.id_transaccion}, monto={self.monto}, estado='{self.estado}')>"
