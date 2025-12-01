"""Modelo Reserva - Reservas de espacios."""

from sqlalchemy import (
    Column,
    BigInteger,
    Text,
    ForeignKey,
    DateTime,
    CheckConstraint,
    Index,
    Numeric,
    func,
)
from sqlalchemy.orm import relationship
from src.database import Base


class Reserva(Base):
    """Reserva de espacio por un vecino."""

    __tablename__ = "reserva"
    __table_args__ = (
        CheckConstraint("fin > inicio", name="ck_reserva_intervalo"),
        CheckConstraint("valor_reserva >= 0", name="ck_reserva_valor_positivo"),
        Index("ix_reserva_estado", "id_junta", "id_estado"),
        Index("ix_reserva_espacio_tiempo", "id_espacio", "inicio", "fin"),
        {"schema": "vecindapp"},
    )

    id_reserva = Column(BigInteger, primary_key=True, autoincrement=True)
    id_junta = Column(
        BigInteger,
        ForeignKey("vecindapp.junta.id_junta", ondelete="CASCADE"),
        nullable=False,
    )
    id_espacio = Column(
        BigInteger,
        ForeignKey("vecindapp.espacio.id_espacio", ondelete="CASCADE"),
        nullable=False,
    )
    id_vecino = Column(
        BigInteger,
        ForeignKey("vecindapp.vecino.id_vecino", ondelete="CASCADE"),
        nullable=False,
    )
    creado_por = Column(
        BigInteger,
        ForeignKey("vecindapp.usuario.id_usuario", ondelete="RESTRICT"),
        nullable=False,
    )
    id_estado = Column(
        BigInteger,
        ForeignKey("vecindapp.estado_reserva.id_estado", ondelete="RESTRICT"),
        nullable=False,
    )
    inicio = Column(DateTime(timezone=True), nullable=False)
    fin = Column(DateTime(timezone=True), nullable=False)
    observaciones = Column(Text)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    valor_reserva = Column(
        Numeric(10, 2), nullable=False, default=0.00
    )

    # Relaciones
    junta = relationship("Junta", back_populates="reservas")
    espacio = relationship("Espacio", back_populates="reservas")
    vecino = relationship("Vecino", back_populates="reservas")
    creado_por_usuario = relationship(
        "Usuario", back_populates="reservas_creadas", foreign_keys=[creado_por]
    )
    estado = relationship("EstadoReserva", back_populates="reservas")

    def __repr__(self) -> str:
        return f"<Reserva(id_reserva={self.id_reserva}, id_espacio={self.id_espacio}, estado='{self.estado}', valor={self.valor_reserva})>"
