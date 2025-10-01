"""Modelo Espacio - Espacios reservables."""

from sqlalchemy import (
    Column,
    BigInteger,
    Text,
    Integer,
    Boolean,
    ForeignKey,
    CheckConstraint,
    Numeric,
    ARRAY,
)
from sqlalchemy.orm import relationship
from src.database import Base


class Espacio(Base):
    """Espacio común reservable de una junta."""

    __tablename__ = "espacio"
    __table_args__ = (
        CheckConstraint(
            "tipo IN ('cancha','sala','plaza','otro')", name="ck_espacio_tipo"
        ),
        CheckConstraint("valor >= 0", name="ck_espacio_valor_positivo"),
        CheckConstraint("capacidad > 0", name="ck_espacio_capacidad_positiva"),
        CheckConstraint("max_horas > 0", name="ck_espacio_max_horas_positivo"),
        {"schema": "vecindapp"},
    )

    id_espacio = Column(BigInteger, primary_key=True, autoincrement=True)
    id_junta = Column(
        BigInteger,
        ForeignKey("vecindapp.junta.id_junta", ondelete="CASCADE"),
        nullable=False,
    )
    nombre = Column(Text, nullable=False)
    tipo = Column(Text, nullable=False)
    capacidad = Column(Integer, nullable=False)
    valor = Column(Numeric(10, 2), nullable=False)  # Precio por hora en CLP
    foto = Column(Text)  # Ruta a la imagen del espacio
    permitido = Column(ARRAY(Text))  # Array de actividades permitidas
    no_permitido = Column(ARRAY(Text))  # Array de actividades no permitidas
    max_horas = Column(Integer, nullable=False, default=4)  # Máximo de horas por reserva
    activo = Column(Boolean, nullable=False, default=True)

    # Relaciones
    junta = relationship("Junta", back_populates="espacios")
    reservas = relationship(
        "Reserva", back_populates="espacio", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Espacio(id_espacio={self.id_espacio}, nombre='{self.nombre}', tipo='{self.tipo}')>"
