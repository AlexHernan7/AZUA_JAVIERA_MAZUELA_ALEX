"""
Schemas para certificados de residencia.
"""

from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field


class CertificadoPedidoCreate(BaseModel):
    """Schema para crear una solicitud de certificado."""
    
    id_motivo: int = Field(..., description="ID del motivo de solicitud")
    valor_certificado: Optional[Decimal] = Field(None, description="Valor del certificado en CLP (opcional, usa valor por defecto si no se especifica)")


class CertificadoPedidoResponse(BaseModel):
    """Schema para respuesta de pedido de certificado."""
    
    id_pedido: int
    id_estado: int
    estado: str  # nombre_estado de la relación
    created_at: datetime
    valor_certificado: Decimal
    vecino_nombres: str
    vecino_apellidos: str
    vecino_rut: str
    vecino_direccion: Optional[str] = None
    comuna: Optional[str] = None
    region: Optional[str] = None
    junta: Optional[str] = None
    id_motivo: int
    motivo_solicitud: str  # motivo de la relación
    motivo_grupo: Optional[str] = None  # grupo del motivo
    
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
    id_motivo: int = Field(..., description="ID del motivo de la solicitud del certificado")
    # Permitir actualizar dirección si es necesaria
    direccion_actualizada: Optional[str] = None


class ErrorResponse(BaseModel):
    """Schema para respuestas de error."""
    
    error: str
    detalle: Optional[str] = None
