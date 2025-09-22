"""
Schemas para certificados de residencia.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class CertificadoPedidoCreate(BaseModel):
    """Schema para crear una solicitud de certificado."""
    
    motivo_solicitud: str = Field(..., description="Motivo de la solicitud del certificado")


class CertificadoPedidoResponse(BaseModel):
    """Schema para respuesta de pedido de certificado."""
    
    id_pedido: int
    estado: str
    created_at: datetime
    vecino_nombres: str
    vecino_apellidos: str
    vecino_rut: str
    vecino_direccion: Optional[str] = None
    comuna: Optional[str] = None
    region: Optional[str] = None
    junta: Optional[str] = None
    motivo_solicitud: Optional[str] = None
    
    class Config:
        from_attributes = True


class CertificadoResponse(BaseModel):
    """Schema para respuesta de certificado generado."""
    
    id_certificado: int
    numero: str
    fecha_emision: datetime
    direccion: Optional[str] = None
    comuna: Optional[str] = None
    region: Optional[str] = None
    pdf_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class CertificadoConfirmacionData(BaseModel):
    """Schema para mostrar datos de confirmación antes de generar certificado."""
    
    nombres: str
    apellido_paterno: str
    apellido_materno: str
    rut: str
    direccion: Optional[str] = None
    comuna: Optional[str] = None
    region: Optional[str] = None
    junta: Optional[str] = None


class CertificadoGenerateRequest(BaseModel):
    """Schema para confirmar generación de certificado."""
    
    confirmar_datos: bool = Field(..., description="Debe ser True para confirmar")
    motivo_solicitud: str = Field(..., description="Motivo de la solicitud del certificado")
    # Permitir actualizar dirección si es necesaria
    direccion_actualizada: Optional[str] = None


class ErrorResponse(BaseModel):
    """Schema para respuestas de error."""
    
    error: str
    detalle: Optional[str] = None
