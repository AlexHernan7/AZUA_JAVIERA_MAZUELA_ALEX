"""Modelo UsuarioRol - Relación usuario-rol."""

from sqlalchemy import Column, BigInteger, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from src.database import Base


class UsuarioRol(Base):
    """Asignación de roles a usuarios."""

    __tablename__ = "usuario_rol"
    __table_args__ = (
        PrimaryKeyConstraint("id_usuario", "id_rol"),
        {"schema": "vecindapp"},
    )

    id_usuario = Column(
        BigInteger,
        ForeignKey("vecindapp.usuario.id_usuario", ondelete="CASCADE"),
        nullable=False,
    )
    id_rol = Column(
        BigInteger,
        ForeignKey("vecindapp.rol.id_rol", ondelete="RESTRICT"),
        nullable=False,
    )

    # Relaciones
    usuario = relationship("Usuario", back_populates="roles")
    rol = relationship("Rol", back_populates="usuarios")

    def __repr__(self) -> str:
        return f"<UsuarioRol(id_usuario={self.id_usuario}, id_rol={self.id_rol})>"
