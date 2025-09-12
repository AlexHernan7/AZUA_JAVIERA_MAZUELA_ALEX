"""Modelo DetalleTransaccion."""

from sqlalchemy import Column, BigInteger, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from src.database import Base


class DetalleTransaccion(Base):
    """Detalle de líneas de una transacción."""
    
    __tablename__ = "detalle_transaccion"
    __table_args__ = {"schema": "vecindapp"}
    
    id_detalle = Column(BigInteger, primary_key=True, autoincrement=True)
    id_transaccion = Column(BigInteger, ForeignKey("vecindapp.transaccion.id_transaccion", ondelete="CASCADE"), nullable=False)
    etiqueta = Column(Text)
    valor = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    # Relaciones
    transaccion = relationship("Transaccion", back_populates="detalles")
    
    def __repr__(self) -> str:
        return f"<DetalleTransaccion(id_detalle={self.id_detalle}, etiqueta='{self.etiqueta}', id_transaccion={self.id_transaccion})>"
