"""
Modelo Espacio para la tabla espacio.

Representa los espacios disponibles para reserva en el sistema VecindApp.
"""

from sqlalchemy import Column, BigInteger, Text, Integer, Boolean, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from src.database import Base


class Espacio(Base):
    """
    Modelo que representa un espacio disponible para reserva.
    
    Attributes:
        id_espacio: Identificador único del espacio (BIGSERIAL PRIMARY KEY)
        id_junta: ID de la junta propietaria (BIGINT NOT NULL REFERENCES junta)
        nombre: Nombre del espacio (TEXT NOT NULL)
        tipo: Tipo de espacio (TEXT NOT NULL CHECK)
        capacidad: Capacidad máxima del espacio (INTEGER)
        activo: Estado activo del espacio (BOOLEAN NOT NULL DEFAULT TRUE)
        junta: Relación con la junta
        reservas: Relación con las reservas de este espacio
    """
    
    __tablename__ = "espacio"
    __table_args__ = (
        CheckConstraint("tipo IN ('cancha','sala','plaza','otro')", name="ck_espacio_tipo"),
        {"schema": "vecindApp"}
    )
    
    id_espacio = Column(BigInteger, primary_key=True, autoincrement=True)
    id_junta = Column(BigInteger, ForeignKey("vecindApp.junta.id_junta", ondelete="CASCADE"), nullable=False)
    nombre = Column(Text, nullable=False)
    tipo = Column(Text, nullable=False)
    capacidad = Column(Integer)
    activo = Column(Boolean, nullable=False, default=True)
    
    # Relaciones
    junta = relationship("Junta", back_populates="espacios")
    reservas = relationship("Reserva", back_populates="espacio", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Espacio(id_espacio={self.id_espacio}, nombre='{self.nombre}', tipo='{self.tipo}')>"
