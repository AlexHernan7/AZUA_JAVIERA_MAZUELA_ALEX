"""
Módulo de seguridad para VecindApp.

Contiene funciones para el manejo seguro de contraseñas y autenticación.
"""

from passlib.context import CryptContext
from typing import Optional

# Configuración para hash de contraseñas
# bcrypt es muy seguro y recomendado para contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Convierte una contraseña en texto plano a un hash seguro.
    
    Args:
        password: Contraseña en texto plano
        
    Returns:
        Hash de la contraseña que se puede guardar en la BD
        
    Example:
        >>> hash_password("mi_password_123")
        "$2b$12$EixZaYVK1fsbw1ZfbX3OXe..."
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña coincide con su hash.
    
    Args:
        plain_password: Contraseña en texto plano
        hashed_password: Hash almacenado en la BD
        
    Returns:
        True si coinciden, False si no
        
    Example:
        >>> verify_password("mi_password_123", "$2b$12$EixZaYVK1fsbw1ZfbX3OXe...")
        True
    """
    return pwd_context.verify(plain_password, hashed_password)


def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
    """
    Valida que una contraseña cumpla con los requisitos mínimos.
    
    Args:
        password: Contraseña a validar
        
    Returns:
        Tupla (es_válida, mensaje_error)
        
    Example:
        >>> validate_password_strength("123")
        (False, "La contraseña debe tener al menos 8 caracteres")
    """
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"
    
    if not any(c.isupper() for c in password):
        return False, "La contraseña debe tener al menos una mayúscula"
    
    if not any(c.islower() for c in password):
        return False, "La contraseña debe tener al menos una minúscula"
    
    if not any(c.isdigit() for c in password):
        return False, "La contraseña debe tener al menos un número"
    
    return True, None
