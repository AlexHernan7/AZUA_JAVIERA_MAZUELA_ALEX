"""
Modelo Region para la tabla region.

Representa las regiones de Chile en el sistema VecindApp.
"""

from sqlalchemy import Column, BigInteger, Text, DateTime, func
from sqlalchemy.orm import relationship
from src.database import Base


class Region(Base):
    """
    Modelo que representa una región de Chile.
    
    Attributes:
        id_region: Identificador único de la región (BIGSERIAL PRIMARY KEY)
        nombre: Nombre de la región (TEXT NOT NULL)
        codigo: Código ISO de la región (TEXT UNIQUE)
        created_at: Fecha de creación (TIMESTAMPTZ NOT NULL DEFAULT now())
        comunas: Relación con las comunas de esta región
    """
    
    __tablename__ = "region"
    __table_args__ = {"schema": "vecindApp"}
    
    id_region = Column(BigInteger, primary_key=True, autoincrement=True)
    nombre = Column(Text, nullable=False)
    codigo = Column(Text, unique=True)  # RM, V, VIII, etc.
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    # Relaciones
    comunas = relationship("Comuna", back_populates="region", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Region(id_region={self.id_region}, nombre='{self.nombre}', codigo='{self.codigo}')>"