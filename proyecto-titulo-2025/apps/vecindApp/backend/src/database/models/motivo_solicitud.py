"""Modelo MotivoSolicitud - Motivos de solicitud de certificados."""

from sqlalchemy import Column, BigInteger, Text, Boolean
from sqlalchemy.orm import relationship
from src.database import Base


class MotivoSolicitud(Base):
    """Motivos predefinidos para solicitudes de certificados."""

    __tablename__ = "motivo_solicitud"
    __table_args__ = {"schema": "vecindapp"}

    id_motivo = Column(BigInteger, primary_key=True, autoincrement=True)
    motivo = Column(Text, nullable=False, unique=True)
    grupo = Column(Text, nullable=False)  # Grupo al que pertenece el motivo
    descripcion = Column(Text)
    activo = Column(Boolean, nullable=False, default=True)

    # Relaciones
    certificados_pedidos = relationship("CertificadoPedido", back_populates="motivo")

    def __repr__(self) -> str:
        return f"<MotivoSolicitud(id_motivo={self.id_motivo}, motivo='{self.motivo}', grupo='{self.grupo}')>"
