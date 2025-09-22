"""Modelo Junta - Juntas de vecinos."""

from sqlalchemy import Column, BigInteger, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from src.database import Base


class Junta(Base):
    """Junta de vecinos con sus espacios y miembros."""

    __tablename__ = "junta"
    __table_args__ = {"schema": "vecindapp"}

    id_junta = Column(BigInteger, primary_key=True, autoincrement=True)
    id_comuna = Column(
        BigInteger, ForeignKey("vecindapp.comuna.id_comuna", ondelete="SET NULL")
    )
    nombre = Column(Text, nullable=False)
    direccion = Column(Text)
    telefono = Column(Text)
    email = Column(Text)
    descripcion = Column(Text)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relaciones
    comuna = relationship("Comuna", back_populates="juntas")
    usuarios = relationship(
        "Usuario", back_populates="junta", cascade="all, delete-orphan"
    )
    vecinos = relationship(
        "Vecino", back_populates="junta", cascade="all, delete-orphan"
    )
    directiva = relationship(
        "Directiva", back_populates="junta", cascade="all, delete-orphan"
    )
    espacios = relationship(
        "Espacio", back_populates="junta", cascade="all, delete-orphan"
    )
    reservas = relationship(
        "Reserva", back_populates="junta", cascade="all, delete-orphan"
    )
    certificados_pedidos = relationship(
        "CertificadoPedido", back_populates="junta", cascade="all, delete-orphan"
    )
    certificados = relationship(
        "Certificado", back_populates="junta", cascade="all, delete-orphan"
    )
    transacciones = relationship(
        "Transaccion", back_populates="junta", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Junta(id_junta={self.id_junta}, nombre='{self.nombre}', id_comuna={self.id_comuna})>"
