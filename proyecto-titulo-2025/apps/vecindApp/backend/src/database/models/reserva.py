"""
Modelo Reserva para la tabla reserva.

Representa las reservas de espacios en el sistema VecindApp.
"""

from sqlalchemy import Column, BigInteger, Text, ForeignKey, DateTime, CheckConstraint, Index, func
from sqlalchemy.orm import relationship
from src.database import Base


class Reserva(Base):
    """
    Modelo que representa una reserva de espacio.
    
    Attributes:
        id_reserva: Identificador único de la reserva (BIGSERIAL PRIMARY KEY)
        id_junta: ID de la junta (BIGINT NOT NULL REFERENCES junta)
        id_espacio: ID del espacio reservado (BIGINT NOT NULL REFERENCES espacio)
        id_vecino: ID del vecino que hace la reserva (BIGINT NOT NULL REFERENCES vecino)
        creado_por: ID del usuario que creó la reserva (BIGINT NOT NULL REFERENCES usuario)
        inicio: Fecha y hora de inicio (TIMESTAMPTZ NOT NULL)
        fin: Fecha y hora de fin (TIMESTAMPTZ NOT NULL)
        estado: Estado de la reserva (TEXT NOT NULL DEFAULT 'pendiente')
        observaciones: Observaciones adicionales (TEXT)
        created_at: Fecha de creación (TIMESTAMPTZ NOT NULL DEFAULT now())
        junta: Relación con la junta
        espacio: Relación con el espacio
        vecino: Relación con el vecino
        creado_por_usuario: Relación con el usuario que creó la reserva
    """
    
    __tablename__ = "reserva"
    __table_args__ = (
        CheckConstraint("estado IN ('pendiente','pagada','aprobada','rechazada','cancelada','confirmada')", name="ck_reserva_estado"),
        CheckConstraint("fin > inicio", name="ck_reserva_intervalo"),
        Index("ix_reserva_estado", "id_junta", "estado"),
        Index("ix_reserva_espacio_tiempo", "id_espacio", "inicio", "fin"),
        {"schema": "vecindApp"}
    )
    
    id_reserva = Column(BigInteger, primary_key=True, autoincrement=True)
    id_junta = Column(BigInteger, ForeignKey("vecindApp.junta.id_junta", ondelete="CASCADE"), nullable=False)
    id_espacio = Column(BigInteger, ForeignKey("vecindApp.espacio.id_espacio", ondelete="CASCADE"), nullable=False)
    id_vecino = Column(BigInteger, ForeignKey("vecindApp.vecino.id_vecino", ondelete="CASCADE"), nullable=False)
    creado_por = Column(BigInteger, ForeignKey("vecindApp.usuario.id_usuario", ondelete="RESTRICT"), nullable=False)
    inicio = Column(DateTime(timezone=True), nullable=False)
    fin = Column(DateTime(timezone=True), nullable=False)
    estado = Column(Text, nullable=False, default="pendiente")
    observaciones = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    # Relaciones
    junta = relationship("Junta", back_populates="reservas")
    espacio = relationship("Espacio", back_populates="reservas")
    vecino = relationship("Vecino", back_populates="reservas")
    creado_por_usuario = relationship("Usuario", back_populates="reservas_creadas", foreign_keys=[creado_por])
    
    def __repr__(self) -> str:
        return f"<Reserva(id_reserva={self.id_reserva}, id_espacio={self.id_espacio}, estado='{self.estado}')>"
