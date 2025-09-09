"""
Modelo PagoExterno para la tabla pago_externo.

Representa los pagos externos en el sistema VecindApp.
"""

from sqlalchemy import Column, BigInteger, Text, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from src.database import Base


class PagoExterno(Base):
    """
    Modelo que representa un pago externo.
    
    Attributes:
        id_pago_externo: Identificador único del pago externo (BIGSERIAL PRIMARY KEY)
        id_transaccion: ID de la transacción asociada (BIGINT NOT NULL REFERENCES transaccion)
        codigo_respuesta: Código de respuesta del proveedor (TEXT)
        estado_pago: Estado del pago según el proveedor (TEXT)
        payload: Datos adicionales del proveedor (JSONB)
        fecha_respuesta: Fecha de respuesta del proveedor (TIMESTAMPTZ)
        transaccion: Relación con la transacción
    """
    
    __tablename__ = "pago_externo"
    __table_args__ = (
        UniqueConstraint("id_transaccion", name="ux_pagoext_tx"),
        {"schema": "vecindApp"}
    )
    
    id_pago_externo = Column(BigInteger, primary_key=True, autoincrement=True)
    id_transaccion = Column(BigInteger, ForeignKey("vecindApp.transaccion.id_transaccion", ondelete="CASCADE"), nullable=False)
    codigo_respuesta = Column(Text)
    estado_pago = Column(Text)
    payload = Column(JSONB)
    fecha_respuesta = Column(DateTime(timezone=True))
    
    # Relaciones
    transaccion = relationship("Transaccion", back_populates="pago_externo")
    
    def __repr__(self) -> str:
        return f"<PagoExterno(id_pago_externo={self.id_pago_externo}, id_transaccion={self.id_transaccion})>"
