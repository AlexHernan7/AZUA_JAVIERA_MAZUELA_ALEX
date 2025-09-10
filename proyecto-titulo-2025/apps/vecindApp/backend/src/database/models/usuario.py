"""
Modelo Usuario para la tabla usuario.

Representa los usuarios del sistema VecindApp.
"""

from typing import TYPE_CHECKING
from sqlalchemy import Column, BigInteger, Text, Boolean, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import relationship
from src.database import Base

if TYPE_CHECKING:
    from .reserva import Reserva
    from .certificado_pedido import CertificadoPedido


class Usuario(Base):
    """
    Modelo que representa un usuario del sistema.
    
    Attributes:
        id_usuario: Identificador único del usuario (BIGSERIAL PRIMARY KEY)
        id_junta: ID de la junta a la que pertenece (BIGINT NOT NULL REFERENCES junta)
        email: Email del usuario (TEXT NOT NULL)
        pass_hash: Hash de la contraseña (TEXT NOT NULL)
        activo: Estado activo del usuario (BOOLEAN NOT NULL DEFAULT TRUE)
        ultimo_acceso: Fecha del último acceso (TIMESTAMPTZ)
        created_at: Fecha de creación (TIMESTAMPTZ NOT NULL DEFAULT now())
        junta: Relación con la junta
        roles: Relación con los roles del usuario
        vecino: Relación con el perfil de vecino
        reservas_creadas: Relación con las reservas creadas por este usuario
        certificados_pedidos: Relación con los pedidos de certificados creados
        transacciones: Relación con las transacciones realizadas
    """
    
    __tablename__ = "usuario"
    __table_args__ = (
        UniqueConstraint("id_junta", "email", name="ux_usuario_email"),
        {"schema": "vecindApp"}
    )
    
    id_usuario = Column(BigInteger, primary_key=True, autoincrement=True)
    id_junta = Column(BigInteger, ForeignKey("vecindApp.junta.id_junta", ondelete="CASCADE"), nullable=False)
    email = Column(Text, nullable=False)
    pass_hash = Column(Text, nullable=False)
    activo = Column(Boolean, nullable=False, default=True)
    ultimo_acceso = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    # Relaciones
    junta = relationship("Junta", back_populates="usuarios")
    roles = relationship("UsuarioRol", back_populates="usuario", cascade="all, delete-orphan")
    vecino = relationship("Vecino", back_populates="usuario", uselist=False)
    reservas_creadas = relationship("Reserva", back_populates="creado_por_usuario", foreign_keys="[Reserva.creado_por]")
    certificados_pedidos = relationship("CertificadoPedido", back_populates="creado_por_usuario", foreign_keys="[CertificadoPedido.creado_por]")
    transacciones = relationship("Transaccion", back_populates="usuario")
    
    def __repr__(self) -> str:
        return f"<Usuario(id_usuario={self.id_usuario}, email='{self.email}', id_junta={self.id_junta})>"
