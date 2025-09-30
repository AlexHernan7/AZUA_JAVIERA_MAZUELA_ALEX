"""Schemas para reservas de espacios."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from enum import Enum


class TipoEspacio(str, Enum):
    """Tipos de espacios disponibles."""
    CANCHA = "cancha"
    SALA = "sala"
    PLAZA = "plaza"
    OTRO = "otro"


class EstadoReserva(str, Enum):
    """Estados posibles de una reserva."""
    PENDIENTE = "pendiente"
    PAGADA = "pagada"
    APROBADA = "aprobada"
    RECHAZADA = "rechazada"
    CANCELADA = "cancelada"
    CONFIRMADA = "confirmada"


class EspacioBase(BaseModel):
    """Schema base para espacios."""
    nombre: str = Field(..., min_length=1, max_length=100)
    tipo: TipoEspacio
    capacidad: Optional[int] = Field(None, ge=1)
    activo: bool = True


class EspacioResponse(EspacioBase):
    """Schema de respuesta para espacios."""
    id_espacio: int
    id_junta: int
    
    class Config:
        from_attributes = True


class ReservaCreate(BaseModel):
    """Schema para crear una reserva."""
    id_espacio: int = Field(..., description="ID del espacio a reservar")
    inicio: datetime = Field(..., description="Fecha y hora de inicio de la reserva")
    fin: datetime = Field(..., description="Fecha y hora de fin de la reserva")
    observaciones: Optional[str] = Field(None, max_length=500)
    
    @validator('fin')
    def validar_fin_despues_inicio(cls, v, values):
        """Validar que la fecha de fin sea posterior al inicio."""
        if 'inicio' in values and v <= values['inicio']:
            raise ValueError('La fecha de fin debe ser posterior al inicio')
        return v
    
    @validator('inicio')
    def validar_fecha_futura(cls, v):
        """Validar que la reserva sea para una fecha futura."""
        if v <= datetime.now():
            raise ValueError('La reserva debe ser para una fecha futura')
        return v
    
    @validator('inicio', 'fin')
    def validar_horario_permitido(cls, v):
        """Validar que la hora esté en el rango permitido (12:00 - 22:00)."""
        if not (12 <= v.hour <= 22):
            raise ValueError('Las reservas solo están permitidas entre las 12:00 y 22:00 horas')
        return v


class ReservaUpdate(BaseModel):
    """Schema para actualizar una reserva."""
    inicio: Optional[datetime] = None
    fin: Optional[datetime] = None
    observaciones: Optional[str] = Field(None, max_length=500)
    estado: Optional[EstadoReserva] = None
    
    @validator('fin')
    def validar_fin_despues_inicio(cls, v, values):
        """Validar que la fecha de fin sea posterior al inicio."""
        if 'inicio' in values and values['inicio'] and v and v <= values['inicio']:
            raise ValueError('La fecha de fin debe ser posterior al inicio')
        return v


class ReservaResponse(BaseModel):
    """Schema de respuesta para reservas."""
    id_reserva: int
    id_junta: int
    id_espacio: int
    id_vecino: int
    creado_por: int
    inicio: datetime
    fin: datetime
    estado: EstadoReserva
    observaciones: Optional[str]
    created_at: datetime
    
    # Información relacionada
    espacio: Optional[EspacioResponse] = None
    
    class Config:
        from_attributes = True


class ReservaListResponse(BaseModel):
    """Schema para lista de reservas."""
    reservas: List[ReservaResponse]
    total: int
    pagina: int
    por_pagina: int


class DisponibilidadRequest(BaseModel):
    """Schema para consultar disponibilidad."""
    id_espacio: int
    fecha: datetime = Field(..., description="Fecha para consultar disponibilidad")
    
    @validator('fecha')
    def validar_fecha_futura(cls, v):
        """Validar que la fecha sea futura o actual."""
        if v.date() < datetime.now().date():
            raise ValueError('No se puede consultar disponibilidad de fechas pasadas')
        return v


class DisponibilidadResponse(BaseModel):
    """Schema de respuesta para disponibilidad."""
    id_espacio: int
    fecha: datetime
    horarios_disponibles: List[dict] = Field(
        ..., 
        description="Lista de horarios disponibles con formato {'inicio': '14:00', 'fin': '15:00'}"
    )
    horarios_ocupados: List[dict] = Field(
        ..., 
        description="Lista de horarios ocupados con información de la reserva"
    )


class ErrorResponse(BaseModel):
    """Schema para respuestas de error."""
    detail: str
    code: Optional[str] = None
