"""
Rutas relacionadas con usuarios y vecinos.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from src.database.session import get_db_session
from src.services.user_service import UserService
from src.schemas.auth_schemas import VecinoResponse
from src.schemas.user_schemas import UsuariosList, UsuarioListResponse, VecinoUpdateRequest, VecinoUpdateResponse
from src.core.security import verify_token
from src.utils.image_utils import binary_to_base64

# Crear router para rutas de usuarios
router = APIRouter(prefix="/users", tags=["Usuarios"])


async def verify_admin_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db_session)
) -> int:
    """
    Verifica que el usuario sea admin.
    
    Returns:
        ID del usuario admin autenticado
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autorización requerido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extraer token del header
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Esquema inválido")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato inválido. Use: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar token JWT
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Obtener user_id
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        user_id = int(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ID de usuario inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar permisos de admin
    user_service = UserService(db)
    is_admin = await user_service.is_user_admin(user_id)
    
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador"
        )
    
    return user_id


@router.get(
    "/vecino/{vecino_id}",
    response_model=VecinoResponse,
    summary="Obtener vecino por ID",
    description="Obtiene los datos de un vecino por su ID"
)
async def get_vecino(
    vecino_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Obtiene los datos de un vecino por su ID.
    """
    try:
        user_service = UserService(db)
        vecino = await user_service.get_vecino_by_id(vecino_id)
        
        if not vecino:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vecino no encontrado"
            )
        
        # Obtener usuario asociado
        usuario = await user_service.get_user_by_id(vecino.id_usuario)
        
        return VecinoResponse(
            id_vecino=vecino.id_vecino,
            nombres=vecino.nombres,
            apellidos=vecino.apellidos,
            email=usuario.email if usuario else "",
            telefono=vecino.telefono,
            direccion=vecino.direccion,
            fecha_nacimiento=vecino.fecha_nacimiento
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener vecino: {str(e)}"
        )


@router.get(
    "/admin/all",
    response_model=UsuariosList,
    summary="Obtener todos los usuarios (Admin)",
    description="Obtiene todos los usuarios del sistema con sus datos básicos. TEMPORAL: Sin autenticación para pruebas."
)
async def get_all_users_admin(
    db: AsyncSession = Depends(get_db_session)
):
    """
    Obtiene todos los usuarios del sistema.
    TEMPORAL: Sin autenticación para pruebas.
    """
    try:
        user_service = UserService(db)
        users_data = await user_service.get_all_users_with_details()
        
        usuarios_response = []
        for usuario, vecino, junta in users_data:
            usuario_response = UsuarioListResponse(
                id_usuario=usuario.id_usuario,
                nombres=vecino.nombres,
                apellido_paterno=vecino.apellido_paterno,
                apellido_materno=vecino.apellido_materno,
                rut=vecino.rut,
                junta_nombre=junta.nombre,
                email=usuario.email,
                activo=usuario.activo,
                created_at=usuario.created_at
            )
            usuarios_response.append(usuario_response)
        
        return UsuariosList(
            usuarios=usuarios_response,
            total=len(usuarios_response)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener usuarios: {str(e)}"
        )


@router.patch(
    "/vecino/{vecino_id}/profile",
    response_model=VecinoUpdateResponse,
    summary="Actualizar perfil de vecino",
    description="Permite al vecino actualizar su email, teléfono y foto de perfil. TEMPORAL: Sin autenticación para pruebas."
)
async def update_vecino_profile(
    vecino_id: int,
    update_data: VecinoUpdateRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Actualiza email, teléfono y/o foto de perfil del vecino.
    TEMPORAL: Sin autenticación para pruebas.
    """
    try:
        user_service = UserService(db)
        
        # Actualizar vecino
        updated_vecino = await user_service.update_vecino_profile(
            vecino_id=vecino_id,
            email=update_data.email,
            telefono=update_data.telefono,
            foto_perfil=update_data.foto_perfil
        )
        
        if not updated_vecino:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vecino no encontrado"
            )
        
        # Convertir foto de perfil binaria a base64 para respuesta
        foto_perfil_base64 = None
        if updated_vecino.foto_perfil:
            # Detectar si es SVG o imagen rasterizada
            if updated_vecino.foto_perfil.startswith(b'<svg') or b'<svg' in updated_vecino.foto_perfil[:100]:
                foto_perfil_base64 = binary_to_base64(updated_vecino.foto_perfil, "image/svg+xml")
            else:
                foto_perfil_base64 = binary_to_base64(updated_vecino.foto_perfil, "image/jpeg")
        
        return VecinoUpdateResponse(
            id_vecino=updated_vecino.id_vecino,
            nombres=updated_vecino.nombres,
            apellido_paterno=updated_vecino.apellido_paterno,
            apellido_materno=updated_vecino.apellido_materno,
            email=updated_vecino.email or "",
            telefono=updated_vecino.telefono,
            foto_perfil=foto_perfil_base64,
            mensaje="Datos actualizados correctamente"
        )
        
    except ValueError as e:
        # Errores de validación
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Errores internos
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar vecino: {str(e)}"
        )
