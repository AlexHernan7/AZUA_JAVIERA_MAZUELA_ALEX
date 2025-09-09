"""
Modelo Rol para la tabla rol.

Representa los roles de usuario en el sistema VecindApp.
"""

from sqlalchemy import Column, BigInteger, Text, CheckConstraint
from sqlalchemy.orm import relationship
from src.database import Base


class Rol(Base):
    """
    Modelo que representa un rol de usuario en el sistema.
    
    Attributes:
        id_rol: Identificador único del rol (BIGSERIAL PRIMARY KEY)
        codigo: Código único del rol (TEXT NOT NULL UNIQUE CHECK)
        nombre: Nombre del rol (TEXT NOT NULL)
        descripcion: Descripción del rol (TEXT)
        usuarios: Relación con los usuarios que tienen este rol
    """
    
    __tablename__ = "rol"
    __table_args__ = (
        CheckConstraint("codigo IN ('vecino','directiva','admin')", name="ck_rol_codigo"),
        {"schema": "vecindApp"}
    )
    
    id_rol = Column(BigInteger, primary_key=True, autoincrement=True)
    codigo = Column(Text, nullable=False, unique=True)
    nombre = Column(Text, nullable=False)
    descripcion = Column(Text)
    
    # Relaciones
    usuarios = relationship("UsuarioRol", back_populates="rol")
    
    def __repr__(self) -> str:
        return f"<Rol(id_rol={self.id_rol}, codigo='{self.codigo}', nombre='{self.nombre}')>"
