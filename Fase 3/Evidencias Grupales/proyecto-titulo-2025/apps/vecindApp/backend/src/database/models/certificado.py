"""Modelo Certificado."""

from sqlalchemy import (
    Column,
    BigInteger,
    Text,
    ForeignKey,
    DateTime,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship
from src.database import Base


class Certificado(Base):
    """Certificado generado para un vecino."""

    __tablename__ = "certificado"
    __table_args__ = (
        UniqueConstraint("id_junta", "numero", name="ux_cert_num"),
        {"schema": "vecindapp"},
    )

    id_certificado = Column(BigInteger, primary_key=True, autoincrement=True)
    id_junta = Column(
        BigInteger,
        ForeignKey("vecindapp.junta.id_junta", ondelete="CASCADE"),
        nullable=False,
    )
    id_pedido = Column(
        BigInteger,
        ForeignKey("vecindapp.certificado_pedido.id_pedido", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    numero = Column(Text, nullable=False)
    fecha_emision = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    direccion = Column(Text)
    comuna = Column(Text)
    region = Column(Text)
    pdf_url = Column(Text)

    # Relaciones
    junta = relationship("Junta", back_populates="certificados")
    pedido = relationship("CertificadoPedido", back_populates="certificado")

    def __repr__(self) -> str:
        return f"<Certificado(id_certificado={self.id_certificado}, numero='{self.numero}', id_pedido={self.id_pedido})>"
