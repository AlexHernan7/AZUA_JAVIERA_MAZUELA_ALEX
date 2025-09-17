"""Modelo PagoExterno - Pagos externos."""

from sqlalchemy import Column, BigInteger, Text, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from src.database import Base


class PagoExterno(Base):
    """Pago procesado por sistema externo."""

    __tablename__ = "pago_externo"
    __table_args__ = (
        UniqueConstraint("id_transaccion", name="ux_pagoext_tx"),
        {"schema": "vecindapp"},
    )

    id_pago_externo = Column(BigInteger, primary_key=True, autoincrement=True)
    id_transaccion = Column(
        BigInteger,
        ForeignKey("vecindapp.transaccion.id_transaccion", ondelete="CASCADE"),
        nullable=False,
    )
    codigo_respuesta = Column(Text)
    estado_pago = Column(Text)
    payload = Column(JSONB)
    fecha_respuesta = Column(DateTime(timezone=True))

    # Relaciones
    transaccion = relationship("Transaccion", back_populates="pago_externo")

    def __repr__(self) -> str:
        return f"<PagoExterno(id_pago_externo={self.id_pago_externo}, id_transaccion={self.id_transaccion})>"
