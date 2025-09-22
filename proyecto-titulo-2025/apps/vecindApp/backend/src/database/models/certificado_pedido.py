"""Modelo CertificadoPedido."""

from sqlalchemy import (
    Column,
    BigInteger,
    Text,
    ForeignKey,
    DateTime,
    CheckConstraint,
    Index,
    func,
)
from sqlalchemy.orm import relationship
from src.database import Base


class CertificadoPedido(Base):
    """Solicitud de certificado de vecino."""

    __tablename__ = "certificado_pedido"
    __table_args__ = (
        CheckConstraint(
            "estado IN ('iniciado','emitido','rechazado')",
            name="ck_cert_pedido_estado",
        ),
        Index("ix_cert_pedido_estado", "id_junta", "estado"),
        {"schema": "vecindapp"},
    )

    id_pedido = Column(BigInteger, primary_key=True, autoincrement=True)
    id_junta = Column(
        BigInteger,
        ForeignKey("vecindapp.junta.id_junta", ondelete="CASCADE"),
        nullable=False,
    )
    id_vecino = Column(
        BigInteger,
        ForeignKey("vecindapp.vecino.id_vecino", ondelete="CASCADE"),
        nullable=False,
    )
    creado_por = Column(
        BigInteger,
        ForeignKey("vecindapp.usuario.id_usuario", ondelete="RESTRICT"),
        nullable=False,
    )
    estado = Column(Text, nullable=False, default="iniciado")
    motivo_solicitud = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relaciones
    junta = relationship("Junta", back_populates="certificados_pedidos")
    vecino = relationship("Vecino", back_populates="certificados_pedidos")
    creado_por_usuario = relationship(
        "Usuario", back_populates="certificados_pedidos", foreign_keys=[creado_por]
    )
    certificado = relationship("Certificado", back_populates="pedido", uselist=False)

    def __repr__(self) -> str:
        return f"<CertificadoPedido(id_pedido={self.id_pedido}, id_vecino={self.id_vecino}, estado='{self.estado}')>"
