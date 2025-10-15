"""
Schemas para espacios comunitarios.

Contiene los modelos Pydantic para validación y serialización de datos de espacios.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from decimal import Decimal


class EspacioCreateRequest(BaseModel):
    """Schema para crear un nuevo espacio comunitario."""
    
    nombre: str = Field(..., min_length=2, max_length=100, description="Nombre del espacio")
    id_tipo: int = Field(..., gt=0, description="ID del tipo de espacio")
    capacidad: int = Field(..., gt=0, description="Capacidad máxima de personas")
    valor: Decimal = Field(..., ge=0, description="Precio por hora en CLP")
    foto: Optional[bytes] = Field(None, description="Foto del espacio en formato binario")
    permitido: Optional[List[str]] = Field(default_factory=list, description="Lista de actividades permitidas")
    no_permitido: Optional[List[str]] = Field(default_factory=list, description="Lista de actividades no permitidas")
    max_horas: int = Field(4, gt=0, le=24, description="Máximo de horas por reserva")
    activo: bool = Field(True, description="Si el espacio está activo")
    id_junta: int = Field(..., gt=0, description="ID de la junta de vecinos")

    @validator("permitido")
    def validate_permitido(cls, v):
        """Valida que las actividades permitidas no estén vacías si se proporcionan."""
        if v is not None:
            # Filtrar elementos vacíos
            v = [item.strip() for item in v if item and item.strip()]
        return v

    @validator("no_permitido")
    def validate_no_permitido(cls, v):
        """Valida que las actividades no permitidas no estén vacías si se proporcionan."""
        if v is not None:
            # Filtrar elementos vacíos
            v = [item.strip() for item in v if item and item.strip()]
        return v
    
    class Config:
        arbitrary_types_allowed = True  # Permitir bytes como tipo


class EspacioUpdateRequest(BaseModel):
    """Schema para actualizar un espacio existente."""
    
    nombre: Optional[str] = Field(None, min_length=2, max_length=100, description="Nombre del espacio")
    id_tipo: Optional[int] = Field(None, gt=0, description="ID del tipo de espacio")
    capacidad: Optional[int] = Field(None, gt=0, description="Capacidad máxima de personas")
    valor: Optional[Decimal] = Field(None, ge=0, description="Precio por hora en CLP")
    foto: Optional[str] = Field(None, description="Ruta a la imagen del espacio")
    permitido: Optional[List[str]] = Field(None, description="Lista de actividades permitidas")
    no_permitido: Optional[List[str]] = Field(None, description="Lista de actividades no permitidas")
    max_horas: Optional[int] = Field(None, gt=0, le=24, description="Máximo de horas por reserva")
    activo: Optional[bool] = Field(None, description="Si el espacio está activo")

    @validator("permitido")
    def validate_permitido(cls, v):
        """Valida que las actividades permitidas no estén vacías si se proporcionan."""
        if v is not None:
            # Filtrar elementos vacíos
            v = [item.strip() for item in v if item and item.strip()]
        return v

    @validator("no_permitido")
    def validate_no_permitido(cls, v):
        """Valida que las actividades no permitidas no estén vacías si se proporcionan."""
        if v is not None:
            # Filtrar elementos vacíos
            v = [item.strip() for item in v if item and item.strip()]
        return v

    @validator("foto")
    def validate_foto(cls, v):
        """Valida que la foto sea una ruta válida si se proporciona."""
        if v is not None and v.strip():
            # Validar que sea una ruta válida (básico)
            # Acepta rutas absolutas, URLs y rutas relativas de uploads
            if not (v.strip().startswith(('/', 'http://', 'https://', 'uploads/'))):
                raise ValueError("La foto debe ser una ruta válida o URL")
        return v


class EspacioResponse(BaseModel):
    """Schema para respuesta de espacio."""
    
    id_espacio: int = Field(..., description="ID único del espacio")
    id_junta: int = Field(..., description="ID de la junta de vecinos")
    id_tipo: int = Field(..., description="ID del tipo de espacio")
    nombre: str = Field(..., description="Nombre del espacio")
    tipo: str = Field(..., description="Tipo de espacio (nombre del tipo)")
    capacidad: int = Field(..., description="Capacidad máxima de personas")
    valor: Decimal = Field(..., description="Precio por hora en CLP")
    foto: Optional[str] = Field(None, description="Ruta a la imagen del espacio")
    permitido: Optional[List[str]] = Field(None, description="Lista de actividades permitidas")
    no_permitido: Optional[List[str]] = Field(None, description="Lista de actividades no permitidas")
    max_horas: int = Field(..., description="Máximo de horas por reserva")
    activo: bool = Field(..., description="Si el espacio está activo")
    
    @classmethod
    def from_orm(cls, obj):
        """Método personalizado para convertir desde el modelo ORM."""
        # Convertir foto de binario a base64 si existe
        foto_base64 = None
        if obj.foto:
            try:
                from src.utils import binary_to_base64
                # Si ya es una ruta de texto, dejarla como está
                if isinstance(obj.foto, str):
                    foto_base64 = obj.foto
                # Si es binario, convertir a base64
                elif isinstance(obj.foto, bytes):
                    foto_base64 = binary_to_base64(obj.foto, "image/png")
            except Exception as e:
                import logging
                logging.warning(f"Error convirtiendo foto de espacio a base64: {str(e)}")
                foto_base64 = None
        
        return cls(
            id_espacio=obj.id_espacio,
            id_junta=obj.id_junta,
            id_tipo=obj.id_tipo,
            nombre=obj.nombre,
            tipo=obj.tipo_espacio.tipo if obj.tipo_espacio else "No especificado",
            capacidad=obj.capacidad,
            valor=obj.valor,
            foto=foto_base64,
            permitido=obj.permitido,
            no_permitido=obj.no_permitido,
            max_horas=obj.max_horas,
            activo=obj.activo
        )
    
    class Config:
        from_attributes = True


class EspacioListResponse(BaseModel):
    """Schema para lista de espacios."""
    
    espacios: List[EspacioResponse] = Field(..., description="Lista de espacios")
    total: int = Field(..., description="Total de espacios")
    pagina: int = Field(..., description="Página actual")
    por_pagina: int = Field(..., description="Elementos por página")


class EspacioDirectivaUpdateRequest(BaseModel):
    """
    Schema para que un usuario directiva actualice un espacio.
    Solo permite editar campos específicos.
    """
    
    capacidad: Optional[int] = Field(None, gt=0, description="Capacidad máxima de personas")
    valor: Optional[Decimal] = Field(None, ge=0, description="Precio por hora en CLP")
    foto: Optional[str] = Field(None, description="Foto del espacio en base64")
    permitido: Optional[List[str]] = Field(None, description="Lista de actividades permitidas")
    no_permitido: Optional[List[str]] = Field(None, description="Lista de actividades no permitidas")
    max_horas: Optional[int] = Field(None, gt=0, le=24, description="Máximo de horas por reserva")

    @validator("permitido")
    def validate_permitido(cls, v):
        """Valida que las actividades permitidas no estén vacías si se proporcionan."""
        if v is not None:
            v = [item.strip() for item in v if item and item.strip()]
        return v

    @validator("no_permitido")
    def validate_no_permitido(cls, v):
        """Valida que las actividades no permitidas no estén vacías si se proporcionan."""
        if v is not None:
            v = [item.strip() for item in v if item and item.strip()]
        return v

    @validator("foto")
    def validate_foto(cls, v):
        """Valida formato de foto en base64."""
        if v is None or not v.strip():
            return v
        
        # Validar formato base64
        if not v.startswith("data:image/"):
            raise ValueError("La foto debe estar en formato base64 con prefijo data:image/")
        
        try:
            import base64
            # Extraer el tipo MIME y los datos
            header, data = v.split(",", 1)
            mime_type = header.split(";")[0].split(":")[1]
            
            # Validar tipos MIME permitidos
            allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
            if mime_type not in allowed_types:
                raise ValueError(f"Tipo de imagen no permitido. Use: {', '.join(allowed_types)}")
            
            # Validar que los datos base64 sean válidos
            decoded = base64.b64decode(data)
            
            # Validar tamaño (máximo 5MB)
            max_size = 5 * 1024 * 1024  # 5MB
            if len(decoded) > max_size:
                raise ValueError("La foto es demasiado grande. Máximo 5MB permitido")
            
            return v
            
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Error al validar foto: {str(e)}")

    class Config:
        json_schema_extra = {
            "example": {
                "capacidad": 50,
                "valor": 15000,
                "foto": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD...",
                "permitido": ["Reuniones", "Talleres", "Eventos sociales"],
                "no_permitido": ["Fumar", "Mascotas", "Bebidas alcohólicas"],
                "max_horas": 4
            }
        }


class EspacioDirectivaUpdateResponse(BaseModel):
    """Schema para respuesta de actualización de espacio por directiva."""
    
    id_espacio: int
    capacidad: int
    valor: Decimal
    foto: Optional[str]
    permitido: Optional[List[str]]
    no_permitido: Optional[List[str]]
    max_horas: int
    mensaje: str = "Espacio actualizado exitosamente"

    class Config:
        from_attributes = True