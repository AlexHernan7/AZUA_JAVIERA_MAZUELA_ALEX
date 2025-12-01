"""
Schemas para tablas maestras.
"""

from pydantic import BaseModel, Field
from typing import Optional


class EstadoCertificadoResponse(BaseModel):
    """Schema para respuesta de estado de certificado."""
    
    id_estado: int
    nombre_estado: str
    descripcion: Optional[str] = None
    activo: bool
    
    class Config:
        from_attributes = True


class MotivoSolicitudResponse(BaseModel):
    """Schema para respuesta de motivo de solicitud."""
    
    id_motivo: int
    motivo: str
    grupo: str
    descripcion: Optional[str] = None
    activo: bool
    
    class Config:
        from_attributes = True


class TipoEspacioResponse(BaseModel):
    """Schema para respuesta de tipo de espacio."""
    
    id_tipo: int
    tipo: str
    descripcion: Optional[str] = None
    activo: bool
    
    class Config:
        from_attributes = True


class EstadoReservaResponse(BaseModel):
    """Schema para respuesta de estado de reserva."""
    
    id_estado: int
    nombre_estado: str
    descripcion: Optional[str] = None
    activo: bool
    
    class Config:
        from_attributes = True


class MotivoSolicitudListResponse(BaseModel):
    """Schema para lista de motivos agrupados."""
    
    motivos: list[MotivoSolicitudResponse]
    total: int
    
    class Config:
        from_attributes = True


class MotivoGrupoResponse(BaseModel):
    """Schema para motivos agrupados por categoría."""
    
    grupo: str
    items: list[MotivoSolicitudResponse]
    
    class Config:
        from_attributes = True


class MotivosAgrupadosResponse(BaseModel):
    """Schema para motivos agrupados."""
    
    grupos: list[MotivoGrupoResponse]
    total: int
    
    class Config:
        from_attributes = True
