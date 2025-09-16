"""
Schemas para autenticación y registro de usuarios.
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import date
import re
import base64
import binascii


class UsuarioRegistroRequest(BaseModel):
    """
    Schema para el request de registro de usuario.
    
    Define qué datos debe enviar el frontend cuando alguien se registra.
    """
    # Datos del usuario
    email: EmailStr = Field(..., description="Email válido del usuario")
    password: str = Field(
        ..., 
        min_length=8, 
        max_length=12, 
        description="Contraseña (8-12 caracteres, alfanumérica + 1 especial)"
    )
    
    # Datos del vecino
    rut: str = Field(..., min_length=8, max_length=12, description="RUT sin puntos ni guión")
    nombres: str = Field(..., min_length=2, max_length=100, description="Nombres del vecino")
    apellido_paterno: str = Field(..., min_length=2, max_length=100, description="Apellido paterno")
    apellido_materno: str = Field(..., min_length=2, max_length=100, description="Apellido materno")
    fecha_nacimiento: date = Field(..., description="Fecha de nacimiento")
    telefono: str = Field(..., description="Teléfono con formato +56XXXXXXXXX")
    direccion: str = Field(..., min_length=5, max_length=200, description="Dirección del vecino")
    foto_perfil: Optional[str] = Field(None, description="Foto de perfil codificada en base64 (opcional)")
    
    # Ubicación
    id_region: int = Field(..., gt=0, description="ID de la región")
    id_comuna: int = Field(..., gt=0, description="ID de la comuna")
    id_junta: int = Field(..., gt=0, description="ID de la junta de vecinos")
    
    @validator('rut')
    def validate_rut(cls, v):
        """
        Valida RUT chileno usando algoritmo módulo 11.
        Acepta RUT con o sin puntos/guión, almacena sin formato.
        """
        if not v:
            raise ValueError('RUT es requerido')
        
        # Limpiar RUT (solo números y K)
        clean_rut = re.sub(r'[^0-9Kk]', '', v.upper())
        
        if len(clean_rut) < 8 or len(clean_rut) > 9:
            raise ValueError('RUT debe tener entre 8 y 9 caracteres')
        
        # Separar número y dígito verificador
        if len(clean_rut) == 8:
            numero = clean_rut[:-1]
            dv = clean_rut[-1]
        else:  # 9 caracteres
            numero = clean_rut[:-1]
            dv = clean_rut[-1]
        
        # Validar que el número sea numérico
        if not numero.isdigit():
            raise ValueError('Número de RUT inválido')
        
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
            raise ValueError('RUT inválido')
        
        return clean_rut
    
    @validator('nombres', 'apellido_paterno', 'apellido_materno')
    def validate_names(cls, v):
        """Valida que nombres y apellidos no estén vacíos y no tengan solo espacios."""
        if not v or not v.strip():
            raise ValueError('No puede estar vacío')
        return v.strip().title()  # Capitaliza cada palabra
    
    @validator('email')
    def validate_email_format(cls, v):
        """
        Validación adicional del email para asegurar formato correcto.
        Pydantic's EmailStr ya valida, pero agregamos verificación extra.
        """
        if not v:
            raise ValueError('Email es requerido')
        
        # Verificar formato básico con regex más estricto
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Formato de email inválido')
        
        return v.lower().strip()
    
    @validator('password')
    def validate_password_complexity(cls, v):
        """
        Valida que la contraseña cumpla con los requisitos de seguridad:
        - Entre 8 y 12 caracteres
        - Al menos una letra
        - Al menos un número  
        - Al menos un carácter especial
        """
        if not v:
            raise ValueError('Contraseña es requerida')
        
        # Verificar longitud (ya validado por Field, pero por seguridad)
        if len(v) < 8 or len(v) > 12:
            raise ValueError('La contraseña debe tener entre 8 y 12 caracteres')
        
        # Verificar que tenga al menos una letra
        if not re.search(r'[a-zA-Z]', v):
            raise ValueError('La contraseña debe contener al menos una letra')
        
        # Verificar que tenga al menos un número
        if not re.search(r'\d', v):
            raise ValueError('La contraseña debe contener al menos un número')
        
        # Verificar que tenga al menos un carácter especial
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>/?]', v):
            raise ValueError('La contraseña debe contener al menos un carácter especial (!@#$%^&*()_+-=[]{}|;:,.<>?)')
        
        return v
    
    @validator('telefono')
    def validate_phone(cls, v):
        """
        Valida formato de teléfono chileno.
        Requiere formato +56XXXXXXXXX (obligatorio).
        """
        if not v:
            raise ValueError('Teléfono es requerido')
        
        # Verificar formato +56
        if not v.startswith('+56'):
            raise ValueError('Teléfono debe comenzar con +56')
        
        # Extraer solo números después de +56
        phone_digits = v[3:]  # Quitar +56
        
        if not phone_digits.isdigit():
            raise ValueError('El teléfono debe contener solo números después de +56')
        
        if len(phone_digits) != 9:
            raise ValueError('El teléfono debe tener exactamente 9 dígitos después de +56')
        
        # Verificar que comience con dígito válido para móviles chilenos
        if phone_digits[0] not in '23456789':
            raise ValueError('Número de teléfono chileno inválido')
        
        return v  # Almacenar con formato +56
    
    @validator('direccion')
    def validate_address(cls, v):
        """Valida que la dirección no esté vacía."""
        if not v or not v.strip():
            raise ValueError('Dirección es requerida')
        return v.strip().title()
    
    @validator('foto_perfil')
    def validate_photo(cls, v):
        """
        Valida la foto de perfil en base64.
        Verifica formato, tamaño y tipo de imagen.
        """
        if v is None:
            return v
        
        # Si es un ejemplo de documentación con puntos suspensivos, permitirlo
        if v.endswith('...'):
            return v
        
        try:
            # Verificar si es base64 válido
            if not v.startswith('data:image/'):
                raise ValueError('La foto debe ser una imagen en formato base64 con prefijo data:image/')
            
            # Extraer el tipo MIME y los datos
            if ',' not in v:
                raise ValueError('Formato de imagen base64 inválido: falta la coma separadora')
            
            header, data = v.split(',', 1)
            mime_type = header.split(';')[0].split(':')[1]
            
            # Verificar tipos de imagen permitidos
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/svg+xml']
            if mime_type not in allowed_types:
                raise ValueError(f'Tipo de imagen no permitido. Use: {", ".join(allowed_types)}')
            
            # Verificar que hay datos después de la coma
            if not data or len(data.strip()) < 10:
                raise ValueError('Los datos base64 de la imagen están vacíos o son muy cortos')
            
            # Decodificar base64 para verificar validez y tamaño
            try:
                image_data = base64.b64decode(data, validate=True)
            except Exception:
                raise ValueError('Los datos base64 de la imagen son inválidos')
            
            # Verificar tamaño máximo (5MB - aumentado para ser más flexible)
            max_size = 5 * 1024 * 1024  # 5MB
            if len(image_data) > max_size:
                raise ValueError('La imagen no puede superar los 5MB')
            
            # Verificar tamaño mínimo muy permisivo (50 bytes)
            min_size = 50  # 50 bytes
            if len(image_data) < min_size:
                raise ValueError('La imagen es demasiado pequeña (mínimo 50 bytes)')
            
            return v
            
        except binascii.Error:
            raise ValueError('Formato base64 inválido')
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f'Error al procesar la imagen: {str(e)}')
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "juan.perez@gmail.com",
                "password": "MiPass123!",
                "rut": "12345678K",
                "nombres": "Juan Carlos",
                "apellido_paterno": "Pérez",
                "apellido_materno": "González",
                "fecha_nacimiento": "1990-05-15",
                "telefono": "+56912345678",
                "direccion": "Los Aromos 123, Maipú",
                "foto_perfil": "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIj4KICA8Y2lyY2xlIGN4PSI1MCIgY3k9IjUwIiByPSI0MCIgZmlsbD0iYmx1ZSIgLz4KICA8dGV4dCB4PSI1MCIgeT0iNTUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZpbGw9IndoaXRlIiBmb250LXNpemU9IjE2Ij5UZXN0PC90ZXh0Pgo8L3N2Zz4=",
                "id_region": 13,
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
    rut: str
    nombres: str
    apellido_paterno: str
    apellido_materno: Optional[str]
    email: str
    telefono: Optional[str]
    direccion: Optional[str]
    fecha_nacimiento: Optional[date]
    foto_perfil: Optional[str] = None  # Base64 de la imagen o None
    
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
                    "rut": "12345678K",
                    "nombres": "Juan Carlos",
                    "apellido_paterno": "Pérez",
                    "apellido_materno": "González",
                    "email": "juan.perez@gmail.com",
                    "telefono": "+56912345678",
                    "direccion": "Los Aromos 123",
                    "fecha_nacimiento": "1990-05-15",
                    "foto_perfil": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD..."
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
    Validaciones básicas para permitir login de usuarios existentes.
    """
    email: EmailStr = Field(..., description="Email del usuario")
    password: str = Field(..., min_length=1, description="Contraseña del usuario")
    
    @validator('email')
    def validate_email_basic(cls, v):
        """
        Validación básica del email para login.
        Solo normaliza el formato, no rechaza emails existentes.
        """
        if not v:
            raise ValueError('Email es requerido')
        return v.lower().strip()
    
    @validator('password')
    def validate_password_basic(cls, v):
        """
        Validación básica de contraseña para login.
        Solo verifica que no esté vacía.
        """
        if not v or not v.strip():
            raise ValueError('Contraseña es requerida')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "juan.perez@gmail.com",
                "password": "MiPass123!"
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
                    "apellido_paterno": "Pérez",
                    "apellido_materno": "González",
                    "activo": True,
                    "vecino": {
                        "nombres": "Juan Carlos",
                        "apellido_paterno": "Pérez",
                        "apellido_materno": "González",
                        "rut": "12345678K",
                        "fecha_nacimiento": "1990-05-15",
                        "telefono": "+56912345678",
                        "direccion": "Los Aromos 123",
                        "foto_perfil": "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIj4KICA8Y2lyY2xlIGN4PSI1MCIgY3k9IjUwIiByPSI0MCIgZmlsbD0iYmx1ZSIgLz4KICA8dGV4dCB4PSI1MCIgeT0iNTUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZpbGw9IndoaXRlIiBmb250LXNpemU9IjE2Ij5UZXN0PC90ZXh0Pgo8L3N2Zz4=",
                        "comuna": "Maipú",
                        "region": "Región Metropolitana",
                        "junta": "Junta de Vecinos Los Aromos"
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
    apellido_paterno: str
    apellido_materno: Optional[str]
    activo: bool
    vecino: Optional["VecinoLoginData"] = None
    
    class Config:
        from_attributes = True


class VecinoLoginData(BaseModel):
    """
    Schema con datos del vecino para la respuesta de login.
    """
    nombres: str
    apellido_paterno: str
    apellido_materno: Optional[str] = None
    rut: str
    fecha_nacimiento: Optional[date] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    foto_perfil: Optional[str] = None
    comuna: Optional[str] = None
    region: Optional[str] = None
    junta: Optional[str] = None
    
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
