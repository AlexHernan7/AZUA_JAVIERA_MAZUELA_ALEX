"""
Schemas para autenticación y registro de usuarios.
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import date


class UsuarioRegistroRequest(BaseModel):
    """
    Schema para el request de registro de usuario.
    
    Define qué datos debe enviar el frontend cuando alguien se registra.
    """
    # Datos del usuario
    email: EmailStr = Field(..., description="Email del usuario")
    password: str = Field(..., min_length=8, description="Contraseña (mínimo 8 caracteres)")
    
    # Datos del vecino
    nombres: str = Field(..., min_length=2, max_length=100, description="Nombres del vecino")
    apellidos: str = Field(..., min_length=2, max_length=100, description="Apellidos del vecino")
    fecha_nacimiento: Optional[date] = Field(None, description="Fecha de nacimiento")
    telefono: Optional[str] = Field(None, max_length=20, description="Teléfono de contacto")
    direccion: Optional[str] = Field(None, max_length=200, description="Dirección del vecino")
    
    # Ubicación
    id_comuna: int = Field(..., gt=0, description="ID de la comuna")
    id_junta: int = Field(..., gt=0, description="ID de la junta de vecinos")
    
    @validator('nombres', 'apellidos')
    def validate_names(cls, v):
        """Valida que nombres y apellidos no estén vacíos y no tengan solo espacios."""
        if not v or not v.strip():
            raise ValueError('No puede estar vacío')
        return v.strip().title()  # Capitaliza cada palabra
    
    @validator('telefono')
    def validate_phone(cls, v):
        """Valida formato básico de teléfono."""
        if v is not None:
            # Remover espacios y caracteres especiales
            clean_phone = ''.join(filter(str.isdigit, v))
            if len(clean_phone) < 8:
                raise ValueError('Teléfono debe tener al menos 8 dígitos')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "juan.perez@gmail.com",
                "password": "MiPassword123",
                "nombres": "Juan Carlos",
                "apellidos": "Pérez González",
                "fecha_nacimiento": "1990-05-15",
                "telefono": "+56912345678",
                "direccion": "Los Aromos 123",
                "id_comuna": 1,
                "id_junta": 1
            }
        }


class VecinoResponse(BaseModel):
    """
    Schema para la respuesta con datos del vecino.
    
    Define qué datos devuelve la API sobre un vecino.
    """
    id_vecino: int
    nombres: str
    apellidos: str
    email: str
    telefono: Optional[str]
    direccion: Optional[str]
    fecha_nacimiento: Optional[date]
    
    class Config:
        from_attributes = True  # Para convertir desde modelos SQLAlchemy


class UsuarioRegistroResponse(BaseModel):
    """
    Schema para la respuesta exitosa de registro.
    
    Define qué datos devuelve la API cuando el registro es exitoso.
    """
    mensaje: str = "Usuario registrado exitosamente"
    id_usuario: int
    vecino: VecinoResponse
    
    class Config:
        json_schema_extra = {
            "example": {
                "mensaje": "Usuario registrado exitosamente",
                "id_usuario": 123,
                "vecino": {
                    "id_vecino": 456,
                    "nombres": "Juan Carlos",
                    "apellidos": "Pérez González",
                    "email": "juan.perez@gmail.com",
                    "telefono": "+56912345678",
                    "direccion": "Los Aromos 123",
                    "fecha_nacimiento": "1990-05-15"
                }
            }
        }


class ErrorResponse(BaseModel):
    """
    Schema para respuestas de error.
    
    Define cómo se devuelven los errores de la API.
    """
    error: str
    detalle: Optional[str] = None
    codigo: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Email ya registrado",
                "detalle": "Ya existe un usuario con este email en la junta",
                "codigo": "EMAIL_DUPLICADO"
            }
        }
