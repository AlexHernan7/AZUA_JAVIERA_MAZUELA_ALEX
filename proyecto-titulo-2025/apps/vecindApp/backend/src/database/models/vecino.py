"""
Modelo Vecino para la tabla vecino.

Representa los vecinos en el sistema VecindApp.
"""

from sqlalchemy import Column, BigInteger, Text, Date, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from src.database import Base


class Vecino(Base):
    """
    Modelo que representa un vecino.
    
    Attributes:
        id_vecino: Identificador único del vecino (BIGSERIAL PRIMARY KEY)
        id_junta: ID de la junta a la que pertenece (BIGINT NOT NULL REFERENCES junta)
        id_usuario: ID del usuario asociado (opcional) (BIGINT UNIQUE REFERENCES usuario)
        nombres: Nombres del vecino (TEXT NOT NULL)
        apellidos: Apellidos del vecino (TEXT NOT NULL)
        fecha_nacimiento: Fecha de nacimiento (DATE)
        telefono: Teléfono de contacto (TEXT)
        email: Email de contacto (TEXT)
        direccion: Dirección del vecino (TEXT)
        id_comuna: ID de la comuna donde vive (BIGINT REFERENCES comuna)
        created_at: Fecha de creación (TIMESTAMPTZ NOT NULL DEFAULT now())
        junta: Relación con la junta
        usuario: Relación con el usuario (opcional)
        comuna: Relación con la comuna
        reservas: Relación con las reservas realizadas
        certificados_pedidos: Relación con los pedidos de certificados
    """
    
    __tablename__ = "vecino"
    __table_args__ = {"schema": "vecindApp"}
    
    id_vecino = Column(BigInteger, primary_key=True, autoincrement=True)
    id_junta = Column(BigInteger, ForeignKey("vecindApp.junta.id_junta", ondelete="CASCADE"), nullable=False)
    id_usuario = Column(BigInteger, ForeignKey("vecindApp.usuario.id_usuario", ondelete="SET NULL"), unique=True)
    nombres = Column(Text, nullable=False)
    apellidos = Column(Text, nullable=False)
    fecha_nacimiento = Column(Date)
    telefono = Column(Text)
    email = Column(Text)
    direccion = Column(Text)
    id_comuna = Column(BigInteger, ForeignKey("vecindApp.comuna.id_comuna", ondelete="SET NULL"))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    # Relaciones
    junta = relationship("Junta", back_populates="vecinos")
    usuario = relationship("Usuario", back_populates="vecino")
    comuna = relationship("Comuna", back_populates="vecinos")
    reservas = relationship("Reserva", back_populates="vecino", cascade="all, delete-orphan")
    certificados_pedidos = relationship("CertificadoPedido", back_populates="vecino", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Vecino(id_vecino={self.id_vecino}, nombres='{self.nombres}', apellidos='{self.apellidos}')>"
