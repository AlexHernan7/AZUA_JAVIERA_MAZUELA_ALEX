"""Modelo Comuna."""

from sqlalchemy import Column, BigInteger, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from src.database import Base


class Comuna(Base):
    """Comuna perteneciente a una región."""
    
    __tablename__ = "comuna"
    __table_args__ = (
        UniqueConstraint("id_region", "nombre", name="ux_comuna"),
        {"schema": "vecindapp"}
    )
    
    id_comuna = Column(BigInteger, primary_key=True, autoincrement=True)
    id_region = Column(BigInteger, ForeignKey("vecindapp.region.id_region", ondelete="RESTRICT"), nullable=False)
    nombre = Column(Text, nullable=False)
    
    # Relaciones
    region = relationship("Region", back_populates="comunas")
    juntas = relationship("Junta", back_populates="comuna")
    vecinos = relationship("Vecino", back_populates="comuna")
    
    def __repr__(self) -> str:
        return f"<Comuna(id_comuna={self.id_comuna}, nombre='{self.nombre}', id_region={self.id_region})>"
