"""
Módulo de seguridad para VecindApp.

Contiene funciones para el manejo seguro de contraseñas y autenticación JWT.
"""

import warnings
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
from typing import TYPE_CHECKING
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from src.core.config import settings

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from src.database.models import Usuario, Vecino

# Suprimir warnings específicos de bcrypt/passlib
warnings.filterwarnings("ignore", message=".*trapped.*error reading bcrypt version.*")

# Configuración para hash de contraseñas
# bcrypt es muy seguro y recomendado para contraseñas
# Configuramos bcrypt para evitar warnings de versión
pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto",
    bcrypt__default_rounds=12,
    bcrypt__min_rounds=4,
    bcrypt__max_rounds=31
)


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


# === FASTAPI DEPENDENCIES ===

# Configurar esquema de autenticación Bearer
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: "AsyncSession" = Depends(None)  # Se debe pasar la dependencia de DB
) -> "Usuario":
    """
    Dependency para obtener el usuario actual desde el JWT token.
    
    Args:
        credentials: Credenciales HTTP Bearer
        db: Sesión de base de datos
        
    Returns:
        Usuario autenticado
        
    Raises:
        HTTPException: Si el token es inválido o el usuario no existe
    """
    # Importar aquí para evitar importaciones circulares
    from src.database.models import Usuario
    from src.database.session import get_db_session
    from sqlalchemy import select
    
    # Si no se pasó la dependencia de DB, obtenerla
    if db is None:
        async for session in get_db_session():
            db = session
            break
    
    # Verificar token
    payload = verify_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extraer user_id del payload
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: falta user_id",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Buscar usuario en la base de datos
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: user_id debe ser un número",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    query = select(Usuario).where(Usuario.id_usuario == user_id)
    result = await db.execute(query)
    usuario = result.scalar_one_or_none()
    
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar que el usuario esté activo
    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario inactivo",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return usuario


async def get_current_vecino(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: "AsyncSession" = Depends(None)
) -> "Vecino":
    """
    Dependency para obtener el vecino actual directamente desde el token.
    
    Args:
        credentials: Credenciales HTTP Bearer
        db: Sesión de base de datos
        
    Returns:
        Vecino asociado al usuario
        
    Raises:
        HTTPException: Si el usuario no tiene perfil de vecino
    """
    # Importar aquí para evitar importaciones circulares
    from src.database.models import Usuario, Vecino
    from src.database.session import get_db_session
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    
    # Si no se pasó la dependencia de DB, obtenerla
    if db is None:
        async for session in get_db_session():
            db = session
            break
    
    # Primero obtener el usuario
    current_user = await get_current_user(credentials, db)
    
    # Buscar vecino asociado al usuario
    query = select(Vecino).where(Vecino.id_usuario == current_user.id_usuario)
    result = await db.execute(query)
    vecino = result.scalar_one_or_none()
    
    if vecino is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario no tiene perfil de vecino"
        )
    
    return vecino
