"""
Schemas para directivos de juntas de vecinos.

Contiene los modelos Pydantic para validación y serialización de datos de directivos.
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
from datetime import date
import re


class DirectivaRegistroRequest(BaseModel):
    """Schema para registro de directivo."""
    
    # Datos personales
    rut: str = Field(..., description="RUT del directivo")
    nombres: str = Field(..., min_length=2, max_length=100, description="Nombres del directivo")
    apellido_paterno: str = Field(..., min_length=2, max_length=100, description="Apellido paterno")
    apellido_materno: Optional[str] = Field(None, max_length=100, description="Apellido materno")
    telefono: str = Field(..., description="Teléfono de contacto")
    email: EmailStr = Field(..., description="Correo electrónico")
    
    # Datos del cargo
    cargo: str = Field(..., description="Cargo en la directiva")
    fecha_inicio_cargo: date = Field(..., description="Fecha de inicio del cargo")
    fecha_termino_cargo: Optional[date] = Field(None, description="Fecha de término del cargo")
    
    # Datos de la junta
    id_junta: int = Field(..., gt=0, description="ID de la junta de vecinos")
    
    # Credenciales
    password: str = Field(..., min_length=8, description="Contraseña del usuario")
    confirm_password: str = Field(..., description="Confirmación de contraseña")
    
    # Foto de perfil opcional (base64)
    foto_perfil: Optional[str] = Field(None, description="Foto de perfil en base64")

    @validator("rut")
    def validate_rut(cls, v):
        """Valida formato de RUT chileno."""
        if not v:
            raise ValueError("RUT es requerido")
        
        # Remover puntos y guiones
        rut_clean = re.sub(r'[.-]', '', v.strip())
        
        # Validar formato básico
        if not re.match(r'^\d{7,8}[0-9Kk]$', rut_clean):
            raise ValueError("Formato de RUT inválido")
        
        return rut_clean.upper()

    @validator("telefono")
    def validate_telefono(cls, v):
        """Valida formato de teléfono chileno."""
        if not v:
            raise ValueError("Teléfono es requerido")
        
        # Remover espacios y caracteres especiales
        phone_clean = re.sub(r'[\s\-\(\)]', '', v.strip())
        
        # Validar formato chileno
        if not re.match(r'^(\+56)?[0-9]{8,9}$', phone_clean):
            raise ValueError("Formato de teléfono inválido")
        
        return phone_clean

    @validator("cargo")
    def validate_cargo(cls, v):
        """Valida que el cargo sea válido."""
        cargos_validos = ['presidente', 'vicepresidente', 'secretario', 'tesorero', 'director', 'vocal']
        if v.lower() not in cargos_validos:
            raise ValueError(f"Cargo debe ser uno de: {', '.join(cargos_validos)}")
        return v.lower()

    @validator("fecha_termino_cargo")
    def validate_fecha_termino(cls, v, values):
        """Valida que la fecha de término sea posterior a la de inicio."""
        if v and 'fecha_inicio_cargo' in values:
            if v <= values['fecha_inicio_cargo']:
                raise ValueError("Fecha de término debe ser posterior a la fecha de inicio")
        return v

    @validator("confirm_password")
    def validate_passwords_match(cls, v, values):
        """Valida que las contraseñas coincidan."""
        if 'password' in values and v != values['password']:
            raise ValueError("Las contraseñas no coinciden")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "rut": "12345678-9",
                "nombres": "Juan Carlos",
                "apellido_paterno": "González",
                "apellido_materno": "Pérez",
                "telefono": "+56987654321",
                "email": "juan.gonzalez@email.com",
                "cargo": "presidente",
                "fecha_inicio_cargo": "2024-01-01",
                "fecha_termino_cargo": "2025-12-31",
                "id_junta": 1,
                "password": "MiPassword123!",
                "confirm_password": "MiPassword123!"
            }
        }


class DirectivaResponse(BaseModel):
    """Schema para respuesta de datos de directivo."""
    
    id_usuario: int
    id_directiva: int
    rut: str
    nombres: str
    apellido_paterno: str
    apellido_materno: Optional[str]
    telefono: str
    email: str
    cargo: str
    fecha_inicio_cargo: date
    fecha_termino_cargo: Optional[date]
    foto_perfil: Optional[str] = Field(None, description="Foto de perfil en base64")
    junta_nombre: Optional[str] = Field(None, description="Nombre de la junta")

    class Config:
        from_attributes = True


class DirectivaRegistroResponse(BaseModel):
    """Schema para respuesta de registro exitoso de directivo."""
    
    id_usuario: int
    directiva: DirectivaResponse

    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    """Schema para respuestas de error."""
    
    error: str
    detalle: str
    codigo: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Error de validación",
                "detalle": "El RUT ya está registrado",
                "codigo": "VALIDATION_ERROR"
            }
        }
