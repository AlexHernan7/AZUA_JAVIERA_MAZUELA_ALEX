"""
Utilidades para manejo de imágenes.
"""

import base64
from typing import Optional


def base64_to_binary(base64_string: str) -> bytes:
    """
    Convierte una cadena base64 a datos binarios.
    
    Args:
        base64_string: Imagen en formato "data:image/type;base64,data"
        
    Returns:
        bytes: Datos binarios de la imagen
        
    Raises:
        ValueError: Si el formato base64 es inválido
    """
    try:
        if base64_string.startswith('data:image/'):
            # Extraer solo los datos base64 (sin el prefijo)
            _, data = base64_string.split(',', 1)
        else:
            data = base64_string
        
        return base64.b64decode(data)
    except Exception as e:
        raise ValueError(f"Error al decodificar imagen base64: {str(e)}")


def binary_to_base64(binary_data: bytes, mime_type: str = "image/jpeg") -> str:
    """
    Convierte datos binarios a cadena base64.
    
    Args:
        binary_data: Datos binarios de la imagen
        mime_type: Tipo MIME de la imagen (default: image/jpeg)
        
    Returns:
        str: Imagen en formato "data:image/type;base64,data"
    """
    if not binary_data:
        return None
    
    try:
        base64_data = base64.b64encode(binary_data).decode('utf-8')
        return f"data:{mime_type};base64,{base64_data}"
    except Exception as e:
        raise ValueError(f"Error al codificar imagen a base64: {str(e)}")


def get_mime_type_from_base64(base64_string: str) -> Optional[str]:
    """
    Extrae el tipo MIME de una cadena base64.
    
    Args:
        base64_string: Imagen en formato "data:image/type;base64,data"
        
    Returns:
        str: Tipo MIME (ej: "image/jpeg") o None si no se puede determinar
    """
    try:
        if base64_string.startswith('data:image/'):
            header = base64_string.split(',')[0]
            mime_type = header.split(';')[0].split(':')[1]
            return mime_type
        return None
    except:
        return None


def validate_image_size(binary_data: bytes, max_size: int = 2 * 1024 * 1024) -> bool:
    """
    Valida que el tamaño de la imagen esté dentro de los límites.
    
    Args:
        binary_data: Datos binarios de la imagen
        max_size: Tamaño máximo en bytes (default: 2MB)
        
    Returns:
        bool: True si el tamaño es válido
    """
    return len(binary_data) <= max_size
