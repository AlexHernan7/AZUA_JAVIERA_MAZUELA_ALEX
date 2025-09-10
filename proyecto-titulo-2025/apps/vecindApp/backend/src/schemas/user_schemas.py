"""
Schemas relacionados con usuarios y vecinos.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


class VecinoCreate(BaseModel):
    """
    Schema para crear un vecino (usado internamente).
    """
    nombres: str
    apellidos: str
    fecha_nacimiento: Optional[date] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    id_junta: int
    id_comuna: int


class JuntaResponse(BaseModel):
    """
    Schema para respuesta con datos de junta.
    """
    id_junta: int
    nombre: str
    direccion: Optional[str]
    telefono: Optional[str]
    email: Optional[str]
    
    class Config:
        from_attributes = True


class ComunaResponse(BaseModel):
    """
    Schema para respuesta con datos de comuna.
    """
    id_comuna: int
    nombre: str
    
    class Config:
        from_attributes = True


class JuntasList(BaseModel):
    """
    Schema para listar juntas por comuna.
    """
    juntas: List[JuntaResponse]
    total: int


class ComunasList(BaseModel):
    """
    Schema para listar comunas.
    """
    comunas: List[ComunaResponse]
    total: int
