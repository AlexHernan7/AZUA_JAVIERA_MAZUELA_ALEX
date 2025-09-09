"""
Modelo UsuarioRol para la tabla usuario_rol.

Representa la relación muchos a muchos entre usuarios y roles en el sistema VecindApp.
"""

from sqlalchemy import Column, BigInteger, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from src.database import Base


class UsuarioRol(Base):
    """
    Modelo que representa la relación entre usuarios y roles.
    
    Attributes:
        id_usuario: ID del usuario (BIGINT NOT NULL REFERENCES usuario)
        id_rol: ID del rol (BIGINT NOT NULL REFERENCES rol)
        usuario: Relación con el usuario
        rol: Relación con el rol
    """
    
    __tablename__ = "usuario_rol"
    __table_args__ = (
        PrimaryKeyConstraint("id_usuario", "id_rol"),
        {"schema": "vecindApp"}
    )
    
    id_usuario = Column(BigInteger, ForeignKey("vecindApp.usuario.id_usuario", ondelete="CASCADE"), nullable=False)
    id_rol = Column(BigInteger, ForeignKey("vecindApp.rol.id_rol", ondelete="RESTRICT"), nullable=False)
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="roles")
    rol = relationship("Rol", back_populates="usuarios")
    
    def __repr__(self) -> str:
        return f"<UsuarioRol(id_usuario={self.id_usuario}, id_rol={self.id_rol})>"
