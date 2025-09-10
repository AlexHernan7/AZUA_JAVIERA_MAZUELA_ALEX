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
        """
        Valida formato de teléfono chileno.
        
        Acepta: +56912345678, 56912345678, 912345678
        Nota: El sistema almacenará solo los 9 dígitos (sin +56)
        """
        if v is not None:
            # Remover espacios y caracteres especiales
            clean_phone = ''.join(filter(str.isdigit, v))
            
            # Verificar longitud según formato
            if clean_phone.startswith('56') and len(clean_phone) == 11:
                # Formato: 56912345678
                if not clean_phone[2] in '23456789':
                    raise ValueError('Número de teléfono chileno inválido')
            elif len(clean_phone) == 9:
                # Formato: 912345678
                if not clean_phone[0] in '23456789':
                    raise ValueError('Número de teléfono chileno inválido')
            else:
                raise ValueError('Formato inválido. Use: +56912345678, 56912345678 o 912345678')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "juan.perez@gmail.com",
                "password": "MiPassword123",
                "nombres": "Juan Carlos",
                "apellidos": "Pérez González",
                "fecha_nacimiento": "1990-05-15",
                "telefono": "912345678",
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


# === SCHEMAS DE LOGIN ===

class LoginRequest(BaseModel):
    """
    Schema para la petición de login.
    
    Datos requeridos para autenticar un usuario.
    """
    email: EmailStr = Field(..., description="Email del usuario")
    password: str = Field(..., min_length=1, description="Contraseña del usuario")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "juan.perez@gmail.com",
                "password": "MiPassword123"
            }
        }


class LoginResponse(BaseModel):
    """
    Schema para la respuesta exitosa de login.
    
    Incluye el token de acceso y datos básicos del usuario.
    """
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Tipo de token")
    expires_in: int = Field(..., description="Tiempo de expiración en minutos")
    user: "UserLoginData" = Field(..., description="Datos básicos del usuario")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1440,
                "user": {
                    "id_usuario": 1,
                    "email": "juan.perez@gmail.com",
                    "nombres": "Juan Carlos",
                    "apellidos": "Pérez González",
                    "activo": True,
                    "vecino": {
                        "id_vecino": 1,
                        "nombres": "Juan Carlos",
                        "apellidos": "Pérez González",
                        "telefono": "912345678",
                        "direccion": "Los Aromos 123"
                    }
                }
            }
        }


class UserLoginData(BaseModel):
    """
    Schema con datos del usuario para la respuesta de login.
    
    Incluye información básica del usuario y vecino.
    """
    id_usuario: int
    email: str
    nombres: str
    apellidos: str
    activo: bool
    vecino: Optional["VecinoLoginData"] = None
    
    class Config:
        from_attributes = True


class VecinoLoginData(BaseModel):
    """
    Schema con datos del vecino para la respuesta de login.
    """
    id_vecino: int
    nombres: str
    apellidos: str
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    
    class Config:
        from_attributes = True


class LoginError(BaseModel):
    """
    Schema para errores de login.
    """
    error: str = Field(..., description="Mensaje de error")
    detalle: str = Field(..., description="Detalle del error")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Credenciales inválidas",
                "detalle": "Email o contraseña incorrectos"
            }
        }
