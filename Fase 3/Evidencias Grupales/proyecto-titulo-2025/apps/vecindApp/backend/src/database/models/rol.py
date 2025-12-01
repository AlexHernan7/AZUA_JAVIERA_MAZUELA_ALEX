"""Modelo Rol - Roles del sistema."""

from sqlalchemy import Column, BigInteger, Text, CheckConstraint
from sqlalchemy.orm import relationship
from src.database import Base


class Rol(Base):
    """Rol con permisos específicos."""

    __tablename__ = "rol"
    __table_args__ = (
        CheckConstraint(
            "codigo IN ('vecino','directiva','admin')", name="ck_rol_codigo"
        ),
        {"schema": "vecindapp"},
    )

    id_rol = Column(BigInteger, primary_key=True, autoincrement=True)
    codigo = Column(Text, nullable=False, unique=True)
    nombre = Column(Text, nullable=False)
    descripcion = Column(Text)

    # Relaciones
    usuarios = relationship("UsuarioRol", back_populates="rol")

    def __repr__(self) -> str:
        return f"<Rol(id_rol={self.id_rol}, codigo='{self.codigo}', nombre='{self.nombre}')>"
