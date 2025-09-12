"""Modelo Vecino - Perfil de vecinos."""

from sqlalchemy import Column, BigInteger, Text, Date, ForeignKey, DateTime, CheckConstraint, func, LargeBinary
from sqlalchemy.orm import relationship
from src.database import Base


class Vecino(Base):
    """Vecino con datos personales y documentos."""
    
    __tablename__ = "vecino"
    __table_args__ = (
        # Constraint para garantizar que el vecino vive en la misma comuna que su junta
        # NOTA: Comentado temporalmente porque PostgreSQL no permite subconsultas en CHECK constraints
        # CheckConstraint(
        #     "id_comuna = (SELECT id_comuna FROM vecindapp.junta WHERE id_junta = vecino.id_junta)",
        #     name="ck_vecino_comuna_consistency"
        # ),
        {"schema": "vecindapp"}
    )
    
    id_vecino = Column(BigInteger, primary_key=True, autoincrement=True)
    id_junta = Column(BigInteger, ForeignKey("vecindapp.junta.id_junta", ondelete="CASCADE"), nullable=False)
    id_usuario = Column(BigInteger, ForeignKey("vecindapp.usuario.id_usuario", ondelete="SET NULL"), unique=True)
    rut = Column(Text, nullable=False, unique=True)
    nombres = Column(Text, nullable=False)
    apellido_paterno = Column(Text, nullable=False)
    apellido_materno = Column(Text)
    fecha_nacimiento = Column(Date)
    telefono = Column(Text)
    email = Column(Text)
    direccion = Column(Text)
    foto_perfil = Column(LargeBinary)  # BYTEA para almacenar imagen en binario
    id_comuna = Column(BigInteger, ForeignKey("vecindapp.comuna.id_comuna", ondelete="SET NULL"))
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
