"""
Modelo Junta para la tabla junta.

Representa las juntas de vecinos en el sistema VecindApp.
"""

from sqlalchemy import Column, BigInteger, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from src.database import Base


class Junta(Base):
    """
    Modelo que representa una junta de vecinos.
    
    Attributes:
        id_junta: Identificador único de la junta (BIGSERIAL PRIMARY KEY)
        id_comuna: ID de la comuna donde está ubicada (BIGINT REFERENCES comuna)
        nombre: Nombre de la junta (TEXT NOT NULL)
        direccion: Dirección de la junta (TEXT)
        telefono: Teléfono de contacto (TEXT)
        email: Email de contacto (TEXT)
        descripcion: Descripción de la junta (TEXT)
        created_at: Fecha de creación (TIMESTAMPTZ NOT NULL DEFAULT now())
        comuna: Relación con la comuna
        usuarios: Relación con los usuarios de esta junta
        vecinos: Relación con los vecinos de esta junta
        espacios: Relación con los espacios de esta junta
        reservas: Relación con las reservas de esta junta
        certificados_pedidos: Relación con los pedidos de certificados
        certificados: Relación con los certificados emitidos
        transacciones: Relación con las transacciones
    """
    
    __tablename__ = "junta"
    __table_args__ = {"schema": "vecindApp"}
    
    id_junta = Column(BigInteger, primary_key=True, autoincrement=True)
    id_comuna = Column(BigInteger, ForeignKey("vecindApp.comuna.id_comuna", ondelete="SET NULL"))
    nombre = Column(Text, nullable=False)
    direccion = Column(Text)
    telefono = Column(Text)
    email = Column(Text)
    descripcion = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    # Relaciones
    comuna = relationship("Comuna", back_populates="juntas")
    usuarios = relationship("Usuario", back_populates="junta", cascade="all, delete-orphan")
    vecinos = relationship("Vecino", back_populates="junta", cascade="all, delete-orphan")
    espacios = relationship("Espacio", back_populates="junta", cascade="all, delete-orphan")
    reservas = relationship("Reserva", back_populates="junta", cascade="all, delete-orphan")
    certificados_pedidos = relationship("CertificadoPedido", back_populates="junta", cascade="all, delete-orphan")
    certificados = relationship("Certificado", back_populates="junta", cascade="all, delete-orphan")
    transacciones = relationship("Transaccion", back_populates="junta", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Junta(id_junta={self.id_junta}, nombre='{self.nombre}', id_comuna={self.id_comuna})>"
