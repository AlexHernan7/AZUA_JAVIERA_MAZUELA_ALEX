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
    id_region: int

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
    foto_perfil: Optional[str] = Field(
        None, description="Nueva foto de perfil en base64"
    )

    @validator("telefono")
    def validate_telefono(cls, v):
        if v is None:
            return v

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
                raise ValueError(
                    "Formato de teléfono inválido. Use formato chileno (+56XXXXXXXXX)"
                )

        # Validar longitud
        if len(telefono_limpio) < 11 or len(telefono_limpio) > 12:
            raise ValueError("Teléfono debe tener entre 11 y 12 dígitos incluyendo +56")

        return telefono_limpio

    @validator("foto_perfil")
    def validate_foto_perfil(cls, v):
        if v is None:
            return v

        # Validar formato base64
        if not v.startswith("data:image/"):
            raise ValueError(
                "La foto debe estar en formato base64 con prefijo data:image/"
            )

        try:
            # Extraer el tipo MIME y los datos
            header, data = v.split(",", 1)
            mime_type = header.split(";")[0].split(":")[1]

            # Validar tipos MIME permitidos
            allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/svg+xml"]
            if mime_type not in allowed_types:
                raise ValueError(
                    f"Tipo de imagen no permitido. Use: {', '.join(allowed_types)}"
                )

            # Validar que los datos base64 sean válidos
            import base64

            decoded = base64.b64decode(data)

            # Validar tamaño (máximo 2MB)
            max_size = 2 * 1024 * 1024  # 2MB
            if len(decoded) > max_size:
                raise ValueError("La imagen es demasiado grande. Máximo 2MB permitido")

            return v

        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Error al validar imagen: {str(e)}")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "nuevo@email.com",
                "telefono": "+56987654321",
                "foto_perfil": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD...",
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
    foto_perfil: Optional[str] = None
    mensaje: str = "Datos actualizados correctamente"

    class Config:
        from_attributes = True
