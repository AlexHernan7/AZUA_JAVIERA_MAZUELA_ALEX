"""
Schemas para juntas de vecinos.
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
from datetime import date, datetime
import re


class JuntaCreateRequest(BaseModel):
    """
    Schema para crear una nueva junta de vecinos.
    """
    
    nombre: str = Field(..., description="Nombre de la junta de vecinos", min_length=3, max_length=200)
    rut: str = Field(..., description="RUT de personalidad jurídica", min_length=9, max_length=12)
    email: EmailStr = Field(..., description="Correo de contacto de la junta")
    telefono: str = Field(..., description="Teléfono de contacto")
    direccion: str = Field(..., description="Dirección de la sede", min_length=10, max_length=300)
    id_comuna: int = Field(..., description="ID de la comuna donde está ubicada", gt=0)
    fecha_constitucion: Optional[date] = Field(None, description="Fecha de constitución de la junta")
    descripcion: Optional[str] = Field(None, description="Descripción de la junta", max_length=1000)
    activa: bool = Field(True, description="Si la junta está activa")
    logo: Optional[str] = Field(None, description="Logo de la junta en base64")

    @validator("rut")
    def validate_rut(cls, v):
        """Validar formato de RUT chileno."""
        if not v:
            raise ValueError("RUT es requerido")
        
        # Limpiar el RUT
        rut_limpio = re.sub(r'[^0-9kK]', '', v.upper())
        
        # Validar longitud
        if len(rut_limpio) < 8 or len(rut_limpio) > 9:
            raise ValueError("RUT debe tener entre 8 y 9 caracteres")
        
        # Separar número y dígito verificador
        numero = rut_limpio[:-1]
        dv = rut_limpio[-1]
        
        # Validar que el número sean solo dígitos
        if not numero.isdigit():
            raise ValueError("Parte numérica del RUT debe contener solo dígitos")
        
        # Validar dígito verificador
        if dv not in '0123456789K':
            raise ValueError("Dígito verificador debe ser un número o K")
        
        # Calcular dígito verificador
        suma = 0
        multiplicador = 2
        
        for digit in reversed(numero):
            suma += int(digit) * multiplicador
            multiplicador += 1
            if multiplicador > 7:
                multiplicador = 2
        
        resto = suma % 11
        dv_calculado = 11 - resto
        
        if dv_calculado == 11:
            dv_calculado = '0'
        elif dv_calculado == 10:
            dv_calculado = 'K'
        else:
            dv_calculado = str(dv_calculado)
        
        if dv != dv_calculado:
            raise ValueError("RUT inválido")
        
        # Formatear RUT
        return f"{numero}-{dv}"

    @validator("telefono")
    def validate_telefono(cls, v):
        """Validar formato de teléfono chileno."""
        if not v:
            raise ValueError("Teléfono es requerido")
        
        # Limpiar caracteres especiales
        telefono_limpio = re.sub(r"[^\d+]", "", v)
        
        # Normalizar formato chileno
        if not telefono_limpio.startswith("+56"):
            if telefono_limpio.startswith("56"):
                telefono_limpio = f"+{telefono_limpio}"
            elif telefono_limpio.startswith("9") and len(telefono_limpio) == 8:
                telefono_limpio = f"+569{telefono_limpio[1:]}"
            elif len(telefono_limpio) == 8:
                telefono_limpio = f"+56{telefono_limpio}"
            else:
                raise ValueError("Formato de teléfono inválido. Use formato chileno (+56XXXXXXXXX)")
        
        # Validar longitud
        if len(telefono_limpio) < 11 or len(telefono_limpio) > 12:
            raise ValueError("Teléfono debe tener entre 11 y 12 dígitos incluyendo +56")
        
        return telefono_limpio

    @validator("fecha_constitucion")
    def validate_fecha_constitucion(cls, v):
        """Validar que la fecha de constitución no sea futura."""
        if v and v > date.today():
            raise ValueError("La fecha de constitución no puede ser futura")
        return v

    @validator("logo")
    def validate_logo(cls, v):
        """Validar formato de logo en base64."""
        if v is None:
            return v
        
        # Validar formato base64
        if not v.startswith("data:image/"):
            raise ValueError("El logo debe estar en formato base64 con prefijo data:image/")
        
        try:
            # Extraer el tipo MIME y los datos
            header, data = v.split(",", 1)
            mime_type = header.split(";")[0].split(":")[1]
            
            # Validar tipos MIME permitidos
            allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/svg+xml"]
            if mime_type not in allowed_types:
                raise ValueError(f"Tipo de imagen no permitido. Use: {', '.join(allowed_types)}")
            
            # Validar que los datos base64 sean válidos
            import base64
            decoded = base64.b64decode(data)
            
            # Validar tamaño (máximo 5MB para logos)
            max_size = 5 * 1024 * 1024  # 5MB
            if len(decoded) > max_size:
                raise ValueError("El logo es demasiado grande. Máximo 5MB permitido")
            
            return v
            
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Error al validar logo: {str(e)}")

    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "Junta de Vecinos Barrio Oeste",
                "rut": "12.345.678-9",
                "email": "contacto@junta.cl",
                "telefono": "+56987654321",
                "direccion": "Calle Principal 123, Depto A",
                "id_comuna": 1,
                "fecha_constitucion": "2020-01-15",
                "descripcion": "Junta de vecinos comprometida con el desarrollo comunitario",
                "activa": True,
                "logo": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD..."
            }
        }


class JuntaCreateResponse(BaseModel):
    """
    Schema para respuesta de creación de junta.
    """
    
    id_junta: int
    nombre: str
    rut: str
    email: str
    telefono: str
    direccion: str
    id_comuna: int
    comuna_nombre: str
    region_nombre: str
    fecha_constitucion: Optional[date]
    descripcion: Optional[str]
    activa: bool
    logo: Optional[str] = None  # Logo en base64 si existe
    created_at: datetime
    mensaje: str = "Junta creada exitosamente"

    class Config:
        from_attributes = True


class JuntaResponse(BaseModel):
    """
    Schema para respuesta con datos completos de junta.
    """
    
    id_junta: int
    nombre: str
    rut: str
    email: Optional[str]
    telefono: Optional[str]
    direccion: Optional[str]
    id_comuna: int
    comuna_nombre: str
    region_nombre: str
    fecha_constitucion: Optional[date]
    descripcion: Optional[str]
    activa: bool
    logo: Optional[str] = None  # Logo en base64 si existe
    created_at: datetime

    class Config:
        from_attributes = True


class JuntaListResponse(BaseModel):
    """
    Schema para listado de juntas (sin logo para optimizar).
    """
    
    id_junta: int
    nombre: str
    rut: str
    email: Optional[str]
    direccion: Optional[str]
    comuna_nombre: str
    region_nombre: str
    activa: bool
    created_at: datetime

    class Config:
        from_attributes = True


class JuntasList(BaseModel):
    """
    Schema para listar juntas.
    """
    
    juntas: list[JuntaListResponse]
    total: int
    activas: int
    inactivas: int


class ErrorResponse(BaseModel):
    """
    Schema para respuestas de error.
    """
    
    error: str
    detalle: Optional[str] = None
    codigo: Optional[str] = None
