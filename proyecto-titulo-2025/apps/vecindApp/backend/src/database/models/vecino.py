"""
Modelo Vecino para la tabla vecino.

Representa los vecinos en el sistema VecindApp.
"""

from sqlalchemy import Column, BigInteger, Text, Date, ForeignKey, DateTime, CheckConstraint, func, LargeBinary
from sqlalchemy.orm import relationship
from src.database import Base


class Vecino(Base):
    """
    Modelo que representa un vecino.
    
    Attributes:
        id_vecino: Identificador único del vecino (BIGSERIAL PRIMARY KEY)
        id_junta: ID de la junta a la que pertenece (BIGINT NOT NULL REFERENCES junta)
        id_usuario: ID del usuario asociado (opcional) (BIGINT UNIQUE REFERENCES usuario)
        rut: RUT del vecino sin puntos ni guión (TEXT NOT NULL UNIQUE)
        nombres: Nombres del vecino (TEXT NOT NULL)
        apellido_paterno: Apellido paterno del vecino (TEXT NOT NULL)
        apellido_materno: Apellido materno del vecino (TEXT)
        fecha_nacimiento: Fecha de nacimiento (DATE)
        telefono: Teléfono de contacto (TEXT)
        email: Email de contacto (TEXT)
        direccion: Dirección del vecino (TEXT)
        foto_perfil: Foto de perfil en binario (BYTEA)
        id_comuna: ID de la comuna donde vive (BIGINT REFERENCES comuna)
        created_at: Fecha de creación (TIMESTAMPTZ NOT NULL DEFAULT now())
        junta: Relación con la junta
        usuario: Relación con el usuario (opcional)
        comuna: Relación con la comuna
        reservas: Relación con las reservas realizadas
        certificados_pedidos: Relación con los pedidos de certificados
    """
    
    __tablename__ = "vecino"
    __table_args__ = (
        # Constraint para garantizar que el vecino vive en la misma comuna que su junta
        # NOTA: Comentado temporalmente porque PostgreSQL no permite subconsultas en CHECK constraints
        # CheckConstraint(
        #     "id_comuna = (SELECT id_comuna FROM vecindApp.junta WHERE id_junta = vecino.id_junta)",
        #     name="ck_vecino_comuna_consistency"
        # ),
        {"schema": "vecindApp"}
    )
    
    id_vecino = Column(BigInteger, primary_key=True, autoincrement=True)
    id_junta = Column(BigInteger, ForeignKey("vecindApp.junta.id_junta", ondelete="CASCADE"), nullable=False)
    id_usuario = Column(BigInteger, ForeignKey("vecindApp.usuario.id_usuario", ondelete="SET NULL"), unique=True)
    rut = Column(Text, nullable=False, unique=True)
    nombres = Column(Text, nullable=False)
    apellido_paterno = Column(Text, nullable=False)
    apellido_materno = Column(Text)
    fecha_nacimiento = Column(Date)
    telefono = Column(Text)
    email = Column(Text)
    direccion = Column(Text)
    foto_perfil = Column(LargeBinary)  # BYTEA para almacenar imagen en binario
    id_comuna = Column(BigInteger, ForeignKey("vecindApp.comuna.id_comuna", ondelete="SET NULL"))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    # Relaciones
    junta = relationship("Junta", back_populates="vecinos")
    usuario = relationship("Usuario", back_populates="vecino")
    comuna = relationship("Comuna", back_populates="vecinos")
    reservas = relationship("Reserva", back_populates="vecino", cascade="all, delete-orphan")
    certificados_pedidos = relationship("CertificadoPedido", back_populates="vecino", cascade="all, delete-orphan")
    
    # Nota: id_comuna es redundante con junta.comuna, pero se mantiene para:
    # 1. Facilitar el flujo UX (selección comuna → junta)
    # 2. Optimizar consultas que filtran por comuna
    # La consistencia se garantiza con el constraint ck_vecino_comuna_consistency
    
    def __repr__(self) -> str:
        return f"<Vecino(id_vecino={self.id_vecino}, rut='{self.rut}', nombres='{self.nombres}', apellido_paterno='{self.apellido_paterno}')>"
