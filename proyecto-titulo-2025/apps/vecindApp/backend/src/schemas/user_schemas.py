"""
Schemas relacionados con usuarios y vecinos.
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List
from datetime import date, datetime
import re


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


class UsuarioListResponse(BaseModel):
    """
    Schema para respuesta con datos básicos de usuario para admin.
    """
    id_usuario: int
    nombres: str
    apellido_paterno: str
    apellido_materno: Optional[str]
    rut: str
    junta_nombre: str
    email: str
    activo: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UsuariosList(BaseModel):
    """
    Schema para listar todos los usuarios (admin).
    """
    usuarios: List[UsuarioListResponse]
    total: int


class VecinoUpdateRequest(BaseModel):
    """
    Schema para actualizar datos del perfil de vecino.
    """
    email: Optional[EmailStr] = Field(None, description="Nuevo email del vecino")
    telefono: Optional[str] = Field(None, description="Nuevo teléfono del vecino")
    
    @validator('telefono')
    def validate_telefono(cls, v):
        if v is None:
            return v
        
        # Limpiar caracteres especiales
        telefono_limpio = re.sub(r'[^\d+]', '', v)
        
        # Normalizar formato chileno
        if not telefono_limpio.startswith('+56'):
            if telefono_limpio.startswith('56'):
                telefono_limpio = f"+{telefono_limpio}"
            elif telefono_limpio.startswith('9') and len(telefono_limpio) == 8:
                telefono_limpio = f"+569{telefono_limpio[1:]}"
            elif len(telefono_limpio) == 8:
                telefono_limpio = f"+56{telefono_limpio}"
            else:
                raise ValueError("Formato de teléfono inválido. Use formato chileno (+56XXXXXXXXX)")
        
        # Validar longitud
        if len(telefono_limpio) < 11 or len(telefono_limpio) > 12:
            raise ValueError("Teléfono debe tener entre 11 y 12 dígitos incluyendo +56")
        
        return telefono_limpio
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "nuevo@email.com",
                "telefono": "+56987654321"
            }
        }


class VecinoUpdateResponse(BaseModel):
    """
    Schema para respuesta de actualización de vecino.
    """
    id_vecino: int
    nombres: str
    apellido_paterno: str
    apellido_materno: Optional[str]
    email: str
    telefono: Optional[str]
    mensaje: str = "Datos actualizados correctamente"
    
    class Config:
        from_attributes = True