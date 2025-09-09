"""
Modelo Comuna para la tabla comuna.

Representa las comunas de Chile en el sistema VecindApp.
"""

from sqlalchemy import Column, BigInteger, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from src.database import Base


class Comuna(Base):
    """
    Modelo que representa una comuna de Chile.
    
    Attributes:
        id_comuna: Identificador único de la comuna (BIGSERIAL PRIMARY KEY)
        id_region: ID de la región a la que pertenece (BIGINT NOT NULL REFERENCES region)
        nombre: Nombre de la comuna (TEXT NOT NULL)
        region: Relación con la región
        juntas: Relación con las juntas de vecinos de esta comuna
        vecinos: Relación con los vecinos de esta comuna
    """
    
    __tablename__ = "comuna"
    __table_args__ = (
        UniqueConstraint("id_region", "nombre", name="ux_comuna"),
        {"schema": "vecindApp"}
    )
    
    id_comuna = Column(BigInteger, primary_key=True, autoincrement=True)
    id_region = Column(BigInteger, ForeignKey("vecindApp.region.id_region", ondelete="RESTRICT"), nullable=False)
    nombre = Column(Text, nullable=False)
    
    # Relaciones
    region = relationship("Region", back_populates="comunas")
    juntas = relationship("Junta", back_populates="comuna")
    vecinos = relationship("Vecino", back_populates="comuna")
    
    def __repr__(self) -> str:
        return f"<Comuna(id_comuna={self.id_comuna}, nombre='{self.nombre}', id_region={self.id_region})>"
