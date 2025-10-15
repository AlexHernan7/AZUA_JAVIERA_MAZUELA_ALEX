"""
Rutas de administración del sistema (solo para usuarios con rol admin).
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional, List
from pydantic import BaseModel

from src.database.session import get_db_session
from src.database.models.usuario import Usuario
from src.database.models.vecino import Vecino
from src.database.models.directiva import Directiva
from src.database.models.junta import Junta
from src.database.models.rol import Rol
from src.database.models.usuario_rol import UsuarioRol
from src.api.routes.user_routes import verify_admin_user
from src.core.logging import get_logger

logger = get_logger(__name__)

# Crear router para rutas de administración
router = APIRouter(prefix="/admin", tags=["Administración"])


# Schemas de respuesta
class SystemUserResponse(BaseModel):
    """Schema para respuesta de usuario del sistema"""
    id_usuario: int
    email: str
    activo: bool
    roles: List[str]
    nombres: Optional[str] = None
    apellido_paterno: Optional[str] = None
    apellido_materno: Optional[str] = None
    junta_nombre: Optional[str] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


class UsuariosListResponse(BaseModel):
    """Schema para respuesta de lista de usuarios"""
    usuarios: List[SystemUserResponse]
    total: int


class UpdateEstadoRequest(BaseModel):
    """Schema para actualizar estado de usuario"""
    activo: bool


@router.get(
    "/usuarios",
    response_model=UsuariosListResponse,
    summary="Listar todos los usuarios del sistema",
    description="Obtiene la lista completa de usuarios con sus roles y datos básicos (solo admin)",
    responses={
        200: {"description": "Lista de usuarios"},
        401: {"description": "No autorizado"},
        403: {"description": "Acceso denegado - requiere rol admin"},
    },
)
async def get_all_system_users(
    limit: int = Query(1000, description="Límite de resultados"),
    admin_user_id: int = Depends(verify_admin_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Obtiene todos los usuarios del sistema con sus roles y datos básicos.
    Solo accesible por administradores.
    """
    try:
        logger.info(f"[ADMIN] Usuario {admin_user_id} solicitando lista de todos los usuarios")
        
        # Consultar todos los usuarios con sus relaciones
        result = await db.execute(
            select(Usuario)
            .options(
                selectinload(Usuario.roles),
                selectinload(Usuario.vecino).selectinload(Vecino.junta),
                selectinload(Usuario.directiva).selectinload(Directiva.junta)
            )
            .limit(limit)
        )
        usuarios = result.scalars().all()
        
        # Construir respuesta con todos los datos
        usuarios_response = []
        for usuario in usuarios:
            # Obtener roles del usuario
            roles_result = await db.execute(
                select(Rol.codigo)
                .join(UsuarioRol, Rol.id_rol == UsuarioRol.id_rol)
                .where(UsuarioRol.id_usuario == usuario.id_usuario)
            )
            roles = [r for r in roles_result.scalars().all()]
            
            # Obtener datos de vecino o directiva
            nombres = None
            apellido_paterno = None
            apellido_materno = None
            junta_nombre = None
            
            # Priorizar datos de vecino
            if usuario.vecino:
                nombres = usuario.vecino.nombres
                apellido_paterno = usuario.vecino.apellido_paterno
                apellido_materno = usuario.vecino.apellido_materno
                if usuario.vecino.junta:
                    junta_nombre = usuario.vecino.junta.nombre
            # Si no tiene vecino, usar datos de directiva
            elif usuario.directiva:
                nombres = usuario.directiva.nombres
                apellido_paterno = usuario.directiva.apellido_paterno
                apellido_materno = usuario.directiva.apellido_materno
                if usuario.directiva.junta:
                    junta_nombre = usuario.directiva.junta.nombre
            
            usuarios_response.append(SystemUserResponse(
                id_usuario=usuario.id_usuario,
                email=usuario.email,
                activo=usuario.activo,
                roles=roles,
                nombres=nombres,
                apellido_paterno=apellido_paterno,
                apellido_materno=apellido_materno,
                junta_nombre=junta_nombre,
                created_at=usuario.created_at.isoformat() if usuario.created_at else None
            ))
        
        logger.info(f"[ADMIN] Se encontraron {len(usuarios_response)} usuarios")
        
        return UsuariosListResponse(
            usuarios=usuarios_response,
            total=len(usuarios_response)
        )
        
    except Exception as e:
        logger.error(f"[ADMIN] Error al obtener lista de usuarios: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener usuarios: {str(e)}"
        )


@router.patch(
    "/usuarios/{usuario_id}/estado",
    summary="Actualizar estado activo/inactivo de un usuario",
    description="Permite activar o desactivar un usuario del sistema (solo admin)",
    responses={
        200: {"description": "Estado actualizado exitosamente"},
        401: {"description": "No autorizado"},
        403: {"description": "Acceso denegado - requiere rol admin"},
        404: {"description": "Usuario no encontrado"},
    },
)
async def update_user_estado(
    usuario_id: int,
    estado_request: UpdateEstadoRequest,
    admin_user_id: int = Depends(verify_admin_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Actualiza el estado activo/inactivo de un usuario.
    Solo accesible por administradores.
    """
    try:
        logger.info(f"[ADMIN] Usuario {admin_user_id} actualizando estado de usuario {usuario_id} a {estado_request.activo}")
        
        # Verificar que el usuario existe
        result = await db.execute(
            select(Usuario).where(Usuario.id_usuario == usuario_id)
        )
        usuario = result.scalar_one_or_none()
        
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # No permitir desactivar al propio admin
        if usuario_id == admin_user_id and not estado_request.activo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No puedes desactivar tu propio usuario"
            )
        
        # Actualizar estado
        usuario.activo = estado_request.activo
        await db.commit()
        
        logger.info(f"[ADMIN] Estado de usuario {usuario_id} actualizado exitosamente")
        
        return {
            "success": True,
            "mensaje": f"Usuario {'activado' if estado_request.activo else 'desactivado'} exitosamente",
            "id_usuario": usuario_id,
            "activo": estado_request.activo
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"[ADMIN] Error al actualizar estado de usuario {usuario_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar estado: {str(e)}"
        )

