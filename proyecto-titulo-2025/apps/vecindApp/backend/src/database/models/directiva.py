"""Modelo Directiva - Miembros de la directiva de juntas de vecinos."""

from sqlalchemy import (
    Column,
    BigInteger,
    Text,
    Date,
    ForeignKey,
    DateTime,
    CheckConstraint,
    func,
    LargeBinary,
)
from sqlalchemy.orm import relationship
from src.database import Base


class Directiva(Base):
    """Directiva con datos personales y cargo específico."""

    __tablename__ = "directiva"
    __table_args__ = (
        CheckConstraint(
            "cargo IN ('presidente','vicepresidente','secretario','tesorero','director','vocal')", 
            name="ck_directiva_cargo"
        ),
        {"schema": "vecindapp"}
    )

    id_directiva = Column(BigInteger, primary_key=True, autoincrement=True)
    id_junta = Column(
        BigInteger,
        ForeignKey("vecindapp.junta.id_junta", ondelete="CASCADE"),
        nullable=False,
    )
    id_usuario = Column(
        BigInteger,
        ForeignKey("vecindapp.usuario.id_usuario", ondelete="SET NULL"),
        unique=True,
    )
    rut = Column(Text, nullable=False, unique=True)
    nombres = Column(Text, nullable=False)
    apellido_paterno = Column(Text, nullable=False)
    apellido_materno = Column(Text)
    telefono = Column(Text)
    email = Column(Text)
    cargo = Column(Text, nullable=False)  # presidente, secretario, tesorero, etc.
    fecha_inicio_cargo = Column(Date, nullable=False)
    fecha_termino_cargo = Column(Date)  # NULL si está activo
    foto_perfil = Column(LargeBinary)  # BYTEA para almacenar imagen en binario
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relaciones
    junta = relationship("Junta", back_populates="directiva")
    usuario = relationship("Usuario", back_populates="directiva")

    def __repr__(self) -> str:
        return f"<Directiva(id_directiva={self.id_directiva}, rut='{self.rut}', nombres='{self.nombres}', cargo='{self.cargo}')>"
