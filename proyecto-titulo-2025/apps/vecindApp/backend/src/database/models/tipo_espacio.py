"""Modelo TipoEspacio - Tipos de espacios comunitarios."""

from sqlalchemy import Column, BigInteger, Text, Boolean
from sqlalchemy.orm import relationship
from src.database import Base


class TipoEspacio(Base):
    """Tipos predefinidos de espacios comunitarios."""

    __tablename__ = "tipo_espacio"
    __table_args__ = {"schema": "vecindapp"}

    id_tipo = Column(BigInteger, primary_key=True, autoincrement=True)
    tipo = Column(Text, nullable=False, unique=True)
    descripcion = Column(Text)
    activo = Column(Boolean, nullable=False, default=True)

    # Relaciones
    espacios = relationship("Espacio", back_populates="tipo_espacio")

    def __repr__(self) -> str:
        return f"<TipoEspacio(id_tipo={self.id_tipo}, tipo='{self.tipo}')>"
