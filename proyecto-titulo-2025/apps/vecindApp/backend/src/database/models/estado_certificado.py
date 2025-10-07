"""Modelo EstadoCertificado - Estados de certificados."""

from sqlalchemy import Column, BigInteger, Text, Boolean
from sqlalchemy.orm import relationship
from src.database import Base


class EstadoCertificado(Base):
    """Estados posibles para certificados."""

    __tablename__ = "estado_certificado"
    __table_args__ = {"schema": "vecindapp"}

    id_estado = Column(BigInteger, primary_key=True, autoincrement=True)
    nombre_estado = Column(Text, nullable=False, unique=True)
    descripcion = Column(Text)
    activo = Column(Boolean, nullable=False, default=True)

    # Relaciones
    certificados_pedidos = relationship("CertificadoPedido", back_populates="estado")

    def __repr__(self) -> str:
        return f"<EstadoCertificado(id_estado={self.id_estado}, nombre_estado='{self.nombre_estado}')>"
