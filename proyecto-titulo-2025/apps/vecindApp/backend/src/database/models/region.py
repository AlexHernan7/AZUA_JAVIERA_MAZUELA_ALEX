"""Modelo Region - Regiones de Chile."""

from sqlalchemy import Column, BigInteger, Text, DateTime, func
from sqlalchemy.orm import relationship
from src.database import Base


class Region(Base):
    """Región de Chile con sus comunas asociadas."""
    
    __tablename__ = "region"
    __table_args__ = {"schema": "vecindapp"}
    
    id_region = Column(BigInteger, primary_key=True, autoincrement=True)
    nombre = Column(Text, nullable=False)
    codigo = Column(Text, unique=True)  # RM, V, VIII, etc.
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    # Relaciones
    comunas = relationship("Comuna", back_populates="region", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Region(id_region={self.id_region}, nombre='{self.nombre}', codigo='{self.codigo}')>"