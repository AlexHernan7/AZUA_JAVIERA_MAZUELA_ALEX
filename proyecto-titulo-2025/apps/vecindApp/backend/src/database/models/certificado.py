"""
Modelo Certificado para la tabla certificado.

Representa los certificados emitidos en el sistema VecindApp.
"""

from sqlalchemy import Column, BigInteger, Text, ForeignKey, DateTime, UniqueConstraint, func
from sqlalchemy.orm import relationship
from src.database import Base


class Certificado(Base):
    """
    Modelo que representa un certificado emitido.
    
    Attributes:
        id_certificado: Identificador único del certificado (BIGSERIAL PRIMARY KEY)
        id_junta: ID de la junta (BIGINT NOT NULL REFERENCES junta)
        id_pedido: ID del pedido asociado (BIGINT UNIQUE NOT NULL REFERENCES certificado_pedido)
        numero: Número del certificado (TEXT NOT NULL)
        fecha_emision: Fecha de emisión (TIMESTAMPTZ NOT NULL DEFAULT now())
        direccion: Dirección al momento de emisión (TEXT)
        comuna: Comuna al momento de emisión (TEXT)
        region: Región al momento de emisión (TEXT)
        pdf_url: URL del PDF del certificado (TEXT)
        junta: Relación con la junta
        pedido: Relación con el pedido de certificado
    """
    
    __tablename__ = "certificado"
    __table_args__ = (
        UniqueConstraint("id_junta", "numero", name="ux_cert_num"),
        {"schema": "vecindApp"}
    )
    
    id_certificado = Column(BigInteger, primary_key=True, autoincrement=True)
    id_junta = Column(BigInteger, ForeignKey("vecindApp.junta.id_junta", ondelete="CASCADE"), nullable=False)
    id_pedido = Column(BigInteger, ForeignKey("vecindApp.certificado_pedido.id_pedido", ondelete="CASCADE"), nullable=False, unique=True)
    numero = Column(Text, nullable=False)
    fecha_emision = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    direccion = Column(Text)
    comuna = Column(Text)
    region = Column(Text)
    pdf_url = Column(Text)
    
    # Relaciones
    junta = relationship("Junta", back_populates="certificados")
    pedido = relationship("CertificadoPedido", back_populates="certificado")
    
    def __repr__(self) -> str:
        return f"<Certificado(id_certificado={self.id_certificado}, numero='{self.numero}', id_pedido={self.id_pedido})>"
