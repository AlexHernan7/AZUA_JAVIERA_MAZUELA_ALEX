"""
Modelo CertificadoPedido para la tabla certificado_pedido.

Representa los pedidos de certificados en el sistema VecindApp.
"""

from sqlalchemy import Column, BigInteger, Text, ForeignKey, DateTime, CheckConstraint, Index, func
from sqlalchemy.orm import relationship
from src.database import Base


class CertificadoPedido(Base):
    """
    Modelo que representa un pedido de certificado.
    
    Attributes:
        id_pedido: Identificador único del pedido (BIGSERIAL PRIMARY KEY)
        id_junta: ID de la junta (BIGINT NOT NULL REFERENCES junta)
        id_vecino: ID del vecino que solicita (BIGINT NOT NULL REFERENCES vecino)
        creado_por: ID del usuario que creó el pedido (BIGINT NOT NULL REFERENCES usuario)
        estado: Estado del pedido (TEXT NOT NULL DEFAULT 'iniciado')
        created_at: Fecha de creación (TIMESTAMPTZ NOT NULL DEFAULT now())
        junta: Relación con la junta
        vecino: Relación con el vecino
        creado_por_usuario: Relación con el usuario que creó el pedido
        certificado: Relación con el certificado emitido (si existe)
    """
    
    __tablename__ = "certificado_pedido"
    __table_args__ = (
        CheckConstraint("estado IN ('iniciado','pagado','emitido','rechazado')", name="ck_cert_pedido_estado"),
        Index("ix_cert_pedido_estado", "id_junta", "estado"),
        {"schema": "vecindApp"}
    )
    
    id_pedido = Column(BigInteger, primary_key=True, autoincrement=True)
    id_junta = Column(BigInteger, ForeignKey("vecindApp.junta.id_junta", ondelete="CASCADE"), nullable=False)
    id_vecino = Column(BigInteger, ForeignKey("vecindApp.vecino.id_vecino", ondelete="CASCADE"), nullable=False)
    creado_por = Column(BigInteger, ForeignKey("vecindApp.usuario.id_usuario", ondelete="RESTRICT"), nullable=False)
    estado = Column(Text, nullable=False, default="iniciado")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    # Relaciones
    junta = relationship("Junta", back_populates="certificados_pedidos")
    vecino = relationship("Vecino", back_populates="certificados_pedidos")
    creado_por_usuario = relationship("Usuario", back_populates="certificados_pedidos", foreign_keys=[creado_por])
    certificado = relationship("Certificado", back_populates="pedido", uselist=False)
    
    def __repr__(self) -> str:
        return f"<CertificadoPedido(id_pedido={self.id_pedido}, id_vecino={self.id_vecino}, estado='{self.estado}')>"
