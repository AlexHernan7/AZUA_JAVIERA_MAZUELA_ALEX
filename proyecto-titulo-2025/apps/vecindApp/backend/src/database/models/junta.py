"""Modelo Junta - Juntas de vecinos."""

from sqlalchemy import Column, BigInteger, Text, ForeignKey, DateTime, Date, Boolean, LargeBinary, func
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
    rut = Column(Text, unique=True, nullable=False)  # RUT personalidad jurídica
    direccion = Column(Text)
    telefono = Column(Text)
    email = Column(Text)
    descripcion = Column(Text)
    fecha_constitucion = Column(Date, nullable=True)  # Fecha de constitución
    activa = Column(Boolean, nullable=False, default=True)  # Si está activa
    logo = Column(LargeBinary, nullable=True)  # Logo en binario
    firma_presidente = Column(LargeBinary, nullable=True)  # Firma del presidente en binario
    timbre = Column(LargeBinary, nullable=True)  # Timbre/sello de la junta en binario
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

    def __repr__(self) -> str:
        return f"<Junta(id_junta={self.id_junta}, nombre='{self.nombre}', rut='{self.rut}', id_comuna={self.id_comuna}, activa={self.activa})>"
