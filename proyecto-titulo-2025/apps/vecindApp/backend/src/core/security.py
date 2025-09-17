"""
Módulo de seguridad para VecindApp.

Contiene funciones para el manejo seguro de contraseñas y autenticación JWT.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
from src.core.config import settings

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


# === JWT FUNCTIONS ===


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Crea un JWT access token.

    Args:
        data: Datos a incluir en el token (user_id, email, etc.)
        expires_delta: Tiempo de expiración personalizado

    Returns:
        Token JWT codificado

    Example:
        >>> create_access_token({"sub": "123", "email": "user@example.com"})
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.api.access_token_expire_minutes
        )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode, settings.api.secret_key, algorithm=settings.api.algorithm
    )

    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verifica y decodifica un JWT token.

    Args:
        token: Token JWT a verificar

    Returns:
        Payload del token si es válido, None si no es válido

    Example:
        >>> verify_token("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
        {"sub": "123", "email": "user@example.com", "exp": 1234567890}
    """
    try:
        payload = jwt.decode(
            token, settings.api.secret_key, algorithms=[settings.api.algorithm]
        )
        return payload
    except JWTError:
        return None


def get_user_id_from_token(token: str) -> Optional[int]:
    """
    Extrae el user_id de un JWT token.

    Args:
        token: Token JWT

    Returns:
        ID del usuario si el token es válido, None si no

    Example:
        >>> get_user_id_from_token("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
        123
    """
    payload = verify_token(token)
    if payload:
        return payload.get("sub")
    return None
