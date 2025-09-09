"""
Modelo DetalleTransaccion para la tabla detalle_transaccion.

Representa los detalles de las transacciones en el sistema VecindApp.
"""

from sqlalchemy import Column, BigInteger, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from src.database import Base


class DetalleTransaccion(Base):
    """
    Modelo que representa un detalle de transacción.
    
    Attributes:
        id_detalle: Identificador único del detalle (BIGSERIAL PRIMARY KEY)
        id_transaccion: ID de la transacción (BIGINT NOT NULL REFERENCES transaccion)
        etiqueta: Etiqueta del detalle (TEXT)
        valor: Valor del detalle (TEXT)
        created_at: Fecha de creación (TIMESTAMPTZ NOT NULL DEFAULT now())
        transaccion: Relación con la transacción
    """
    
    __tablename__ = "detalle_transaccion"
    __table_args__ = {"schema": "vecindApp"}
    
    id_detalle = Column(BigInteger, primary_key=True, autoincrement=True)
    id_transaccion = Column(BigInteger, ForeignKey("vecindApp.transaccion.id_transaccion", ondelete="CASCADE"), nullable=False)
    etiqueta = Column(Text)
    valor = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    # Relaciones
    transaccion = relationship("Transaccion", back_populates="detalles")
    
    def __repr__(self) -> str:
        return f"<DetalleTransaccion(id_detalle={self.id_detalle}, etiqueta='{self.etiqueta}', id_transaccion={self.id_transaccion})>"
