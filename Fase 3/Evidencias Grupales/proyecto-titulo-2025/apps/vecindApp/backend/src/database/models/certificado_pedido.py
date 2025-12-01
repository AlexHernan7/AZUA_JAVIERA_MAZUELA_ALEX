"""Modelo CertificadoPedido."""

from sqlalchemy import (
    Column,
    BigInteger,
    Text,
    ForeignKey,
    DateTime,
    CheckConstraint,
    Index,
    Numeric,
    func,
)
from sqlalchemy.orm import relationship
from src.database import Base


class CertificadoPedido(Base):
    """Solicitud de certificado de vecino."""

    __tablename__ = "certificado_pedido"
    __table_args__ = (
        CheckConstraint("valor_certificado > 0", name="ck_cert_pedido_valor_positivo"),
        Index("ix_cert_pedido_estado", "id_junta", "id_estado"),
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
    id_estado = Column(
        BigInteger,
        ForeignKey("vecindapp.estado_certificado.id_estado", ondelete="RESTRICT"),
        nullable=False,
    )
    id_motivo = Column(
        BigInteger,
        ForeignKey("vecindapp.motivo_solicitud.id_motivo", ondelete="RESTRICT"),
        nullable=False,
    )
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    valor_certificado = Column(
        Numeric(10, 2), nullable=False, default=2000.00
    )

    # Relaciones
    junta = relationship("Junta", back_populates="certificados_pedidos")
    vecino = relationship("Vecino", back_populates="certificados_pedidos")
    creado_por_usuario = relationship(
        "Usuario", back_populates="certificados_pedidos", foreign_keys=[creado_por]
    )
    estado = relationship("EstadoCertificado", back_populates="certificados_pedidos")
    motivo = relationship("MotivoSolicitud", back_populates="certificados_pedidos")
    certificado = relationship("Certificado", back_populates="pedido", uselist=False)

    def __repr__(self) -> str:
        return f"<CertificadoPedido(id_pedido={self.id_pedido}, id_vecino={self.id_vecino}, estado='{self.estado}', valor={self.valor_certificado})>"
