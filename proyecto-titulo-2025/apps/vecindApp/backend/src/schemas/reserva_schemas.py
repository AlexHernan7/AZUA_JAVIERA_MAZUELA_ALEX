"""
Schemas para reservas de espacios comunitarios.

Contiene los modelos Pydantic para validación y serialización de datos de reservas.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, date, time
from decimal import Decimal


class ReservaCreateRequest(BaseModel):
    """Schema para crear una nueva reserva de espacio."""
    
    id_espacio: int = Field(..., gt=0, description="ID del espacio a reservar")
    id_junta: int = Field(..., gt=0, description="ID de la junta de vecinos")
    id_vecino: int = Field(..., gt=0, description="ID del vecino que hace la reserva")
    fecha: date = Field(..., description="Fecha de la reserva")
    hora_inicio: str = Field(..., description="Hora de inicio (formato HH:MM)")
    hora_termino: str = Field(..., description="Hora de término (formato HH:MM)")
    motivo: str = Field(..., min_length=3, max_length=200, description="Motivo de la reserva")
    asistentes: Optional[int] = Field(None, ge=1, description="Número de asistentes (opcional)")
    observaciones: Optional[str] = Field(None, max_length=500, description="Observaciones adicionales")
    acepta_reglamento: bool = Field(..., description="Si acepta el reglamento de uso")

    @validator("fecha")
    def validate_fecha(cls, v):
        """Valida que la fecha no sea en el pasado."""
        if v < date.today():
            raise ValueError("La fecha de reserva no puede ser en el pasado")
        return v

    @validator("hora_inicio", "hora_termino")
    def validate_hora_format(cls, v):
        """Valida el formato de hora HH:MM."""
        try:
            time.fromisoformat(v)
        except ValueError:
            raise ValueError("La hora debe estar en formato HH:MM (ej: 14:30)")
        return v

    @validator("hora_termino")
    def validate_hora_termino(cls, v, values):
        """Valida que la hora de término sea posterior a la de inicio."""
        if "hora_inicio" in values:
            try:
                inicio = time.fromisoformat(values["hora_inicio"])
                termino = time.fromisoformat(v)
                if termino <= inicio:
                    raise ValueError("La hora de término debe ser posterior a la hora de inicio")
            except ValueError:
                pass  # El error de formato ya se maneja en el validador anterior
        return v

    @validator("acepta_reglamento")
    def validate_acepta_reglamento(cls, v):
        """Valida que se acepte el reglamento."""
        if not v:
            raise ValueError("Debe aceptar el reglamento de uso para hacer la reserva")
        return v


class ReservaUpdateRequest(BaseModel):
    """Schema para actualizar una reserva existente."""
    
    fecha: Optional[date] = Field(None, description="Fecha de la reserva")
    hora_inicio: Optional[str] = Field(None, description="Hora de inicio (formato HH:MM)")
    hora_termino: Optional[str] = Field(None, description="Hora de término (formato HH:MM)")
    motivo: Optional[str] = Field(None, min_length=3, max_length=200, description="Motivo de la reserva")
    asistentes: Optional[int] = Field(None, ge=1, description="Número de asistentes")
    observaciones: Optional[str] = Field(None, max_length=500, description="Observaciones adicionales")
    estado: Optional[str] = Field(None, description="Estado de la reserva")

    @validator("fecha")
    def validate_fecha(cls, v):
        """Valida que la fecha no sea en el pasado."""
        if v is not None and v < date.today():
            raise ValueError("La fecha de reserva no puede ser en el pasado")
        return v

    @validator("hora_inicio", "hora_termino")
    def validate_hora_format(cls, v):
        """Valida el formato de hora HH:MM."""
        if v is not None:
            try:
                time.fromisoformat(v)
            except ValueError:
                raise ValueError("La hora debe estar en formato HH:MM (ej: 14:30)")
        return v

    @validator("estado")
    def validate_estado(cls, v):
        """Valida que el estado sea válido."""
        if v is not None:
            estados_validos = ['pendiente', 'pagada', 'aprobada', 'rechazada', 'cancelada', 'confirmada']
            if v.lower() not in estados_validos:
                raise ValueError(f"Estado debe ser uno de: {', '.join(estados_validos)}")
            return v.lower()
        return v


class ReservaResponse(BaseModel):
    """Schema para respuesta de reserva."""
    
    id_reserva: int = Field(..., description="ID único de la reserva")
    id_junta: int = Field(..., description="ID de la junta de vecinos")
    id_espacio: int = Field(..., description="ID del espacio reservado")
    id_vecino: int = Field(..., description="ID del vecino que hizo la reserva")
    creado_por: int = Field(..., description="ID del usuario que creó la reserva")
    inicio: datetime = Field(..., description="Fecha y hora de inicio")
    fin: datetime = Field(..., description="Fecha y hora de término")
    estado: str = Field(..., description="Estado de la reserva")
    observaciones: Optional[str] = Field(None, description="Observaciones adicionales")
    created_at: datetime = Field(..., description="Fecha de creación de la reserva")
    valor_reserva: Decimal = Field(..., description="Valor total de la reserva en CLP")
    
    # Información adicional del espacio
    espacio_nombre: Optional[str] = Field(None, description="Nombre del espacio")
    espacio_tipo: Optional[str] = Field(None, description="Tipo del espacio")
    espacio_capacidad: Optional[int] = Field(None, description="Capacidad del espacio")
    espacio_valor: Optional[Decimal] = Field(None, description="Valor por hora del espacio")
    
    # Información del vecino
    vecino_nombre: Optional[str] = Field(None, description="Nombre del vecino")
    vecino_email: Optional[str] = Field(None, description="Email del vecino")

    class Config:
        from_attributes = True


class ReservaListResponse(BaseModel):
    """Schema para lista de reservas."""
    
    reservas: List[ReservaResponse] = Field(..., description="Lista de reservas")
    total: int = Field(..., description="Total de reservas")
    pagina: int = Field(..., description="Página actual")
    por_pagina: int = Field(..., description="Elementos por página")


class DisponibilidadRequest(BaseModel):
    """Schema para verificar disponibilidad de un espacio."""
    
    id_espacio: int = Field(..., gt=0, description="ID del espacio")
    fecha: date = Field(..., description="Fecha a verificar")
    hora_inicio: str = Field(..., description="Hora de inicio (formato HH:MM)")
    hora_termino: str = Field(..., description="Hora de término (formato HH:MM)")

    @validator("fecha")
    def validate_fecha(cls, v):
        """Valida que la fecha no sea en el pasado."""
        if v < date.today():
            raise ValueError("La fecha no puede ser en el pasado")
        return v

    @validator("hora_inicio", "hora_termino")
    def validate_hora_format(cls, v):
        """Valida el formato de hora HH:MM."""
        try:
            time.fromisoformat(v)
        except ValueError:
            raise ValueError("La hora debe estar en formato HH:MM (ej: 14:30)")
        return v

    @validator("hora_termino")
    def validate_hora_termino(cls, v, values):
        """Valida que la hora de término sea posterior a la de inicio."""
        if "hora_inicio" in values:
            try:
                inicio = time.fromisoformat(values["hora_inicio"])
                termino = time.fromisoformat(v)
                if termino <= inicio:
                    raise ValueError("La hora de término debe ser posterior a la hora de inicio")
            except ValueError:
                pass
        return v


class DisponibilidadResponse(BaseModel):
    """Schema para respuesta de disponibilidad."""
    
    disponible: bool = Field(..., description="Si el horario está disponible")
    mensaje: str = Field(..., description="Mensaje explicativo")
    reservas_conflicto: Optional[List[dict]] = Field(None, description="Reservas que causan conflicto")


class ReservaConPagoRequest(BaseModel):
    """Schema para crear una reserva con pago."""
    
    id_espacio: int = Field(..., gt=0, description="ID del espacio a reservar")
    id_junta: int = Field(..., gt=0, description="ID de la junta de vecinos")
    id_vecino: int = Field(..., gt=0, description="ID del vecino que hace la reserva")
    fecha: date = Field(..., description="Fecha de la reserva")
    hora_inicio: str = Field(..., description="Hora de inicio (formato HH:MM)")
    hora_termino: str = Field(..., description="Hora de término (formato HH:MM)")
    motivo: str = Field(..., min_length=3, max_length=200, description="Motivo de la reserva")
    asistentes: Optional[int] = Field(None, ge=1, description="Número de asistentes (opcional)")
    observaciones: Optional[str] = Field(None, max_length=500, description="Observaciones adicionales")
    acepta_reglamento: bool = Field(..., description="Si acepta el reglamento de uso")
    
    @validator("fecha")
    def validate_fecha(cls, v):
        """Valida que la fecha no sea en el pasado."""
        if v < date.today():
            raise ValueError("La fecha de reserva no puede ser en el pasado")
        return v

    @validator("hora_inicio", "hora_termino")
    def validate_hora_format(cls, v):
        """Valida el formato de hora HH:MM."""
        try:
            time.fromisoformat(v)
        except ValueError:
            raise ValueError("La hora debe estar en formato HH:MM (ej: 14:30)")
        return v

    @validator("hora_termino")
    def validate_hora_termino(cls, v, values):
        """Valida que la hora de término sea posterior a la de inicio."""
        if "hora_inicio" in values:
            try:
                inicio = time.fromisoformat(values["hora_inicio"])
                termino = time.fromisoformat(v)
                if termino <= inicio:
                    raise ValueError("La hora de término debe ser posterior a la hora de inicio")
            except ValueError:
                pass  # El error de formato ya se maneja en el validador anterior
        return v

    @validator("acepta_reglamento")
    def validate_acepta_reglamento(cls, v):
        """Valida que se acepte el reglamento."""
        if not v:
            raise ValueError("Debe aceptar el reglamento de uso para hacer la reserva")
        return v
