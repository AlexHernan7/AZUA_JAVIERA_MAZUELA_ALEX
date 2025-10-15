"""
Rutas relacionadas con usuarios y vecinos.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from src.database.session import get_db_session
from src.services.user_service import UserService
from src.schemas.auth_schemas import VecinoResponse, VecinoListResponse
from src.schemas.user_schemas import (
    UsuariosList,
    UsuarioListResponse,
    VecinoUpdateRequest,
    VecinoUpdateResponse,
    ChangePasswordRequest,
    ChangePasswordResponse,
)
from src.core.security import verify_token
from src.utils.image_utils import binary_to_base64

# Crear router para rutas de usuarios
router = APIRouter(prefix="/users", tags=["Usuarios"])


async def verify_admin_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db_session),
) -> int:
    """
    Verifica que el usuario sea admin.
    """
    from src.core.logging import get_logger
    logger = get_logger(__name__)
    
    if not authorization:
        logger.warning("[AUTH] Token de autorización no proporcionado")
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
        logger.warning("[AUTH] Formato de autorización inválido")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato inválido. Use: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verificar token JWT
    payload = verify_token(token)
    if not payload:
        logger.warning("[AUTH] Token inválido o expirado")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Obtener user_id
    user_id = payload.get("sub")
    if not user_id:
        logger.warning("[AUTH] Token sin user_id")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = int(user_id)
    except ValueError:
        logger.warning(f"[AUTH] ID de usuario inválido: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ID de usuario inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.info(f"[AUTH] Verificando permisos de admin para usuario ID: {user_id}")

    # Verificar permisos de admin
    user_service = UserService(db)
    is_admin = await user_service.is_user_admin(user_id)
    
    logger.info(f"[AUTH] Usuario {user_id} es admin: {is_admin}")

    if not is_admin:
        logger.warning(f"[AUTH] Usuario {user_id} no tiene permisos de admin")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador",
        )

    logger.info(f"[AUTH] Usuario {user_id} verificado como admin exitosamente")
    return user_id


@router.get(
    "/vecino/{vecino_id}",
    response_model=VecinoResponse,
    summary="Obtener vecino por ID",
    description="Obtiene los datos de un vecino por su ID",
)
async def get_vecino(vecino_id: int, db: AsyncSession = Depends(get_db_session)):
    """
    Obtiene los datos de un vecino por su ID.
    """
    try:
        user_service = UserService(db)
        vecino = await user_service.get_vecino_by_id(vecino_id)

        if not vecino:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Vecino no encontrado"
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
            fecha_nacimiento=vecino.fecha_nacimiento,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener vecino: {str(e)}",
        )


@router.get(
    "/admin/all",
    response_model=UsuariosList,
    summary="Obtener todos los usuarios (Admin)",
    description="Obtiene todos los usuarios del sistema con sus datos básicos. "
    "TEMPORAL: Sin autenticación para pruebas.",
)
async def get_all_users_admin(db: AsyncSession = Depends(get_db_session)):
    """
    Obtiene todos los usuarios del sistema (TEMPORAL: sin auth).
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
                created_at=usuario.created_at,
            )
            usuarios_response.append(usuario_response)

        return UsuariosList(usuarios=usuarios_response, total=len(usuarios_response))

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener usuarios: {str(e)}",
        )


async def verify_user_token(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db_session),
) -> int:
    """
    Verifica que el usuario esté autenticado y retorna su ID.
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

    return user_id


@router.patch(
    "/vecino/{vecino_id}/profile",
    response_model=VecinoUpdateResponse,
    summary="Actualizar perfil de vecino",
    description="Permite al vecino actualizar su email, teléfono y foto de perfil.",
)
async def update_vecino_profile(
    vecino_id: int,
    update_data: VecinoUpdateRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user_id: int = Depends(verify_user_token),
):
    """
    Actualiza email, teléfono y/o foto de perfil del vecino.
    """
    try:
        user_service = UserService(db)

        # Verificar que el vecino pertenece al usuario autenticado
        vecino = await user_service.get_vecino_by_id(vecino_id)
        if not vecino:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Vecino no encontrado"
            )

        if vecino.id_usuario != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para actualizar este perfil",
            )

        # Actualizar vecino
        updated_vecino = await user_service.update_vecino_profile(
            vecino_id=vecino_id,
            apellido_paterno=update_data.apellido_paterno,
            apellido_materno=update_data.apellido_materno,
            email=update_data.email,
            telefono=update_data.telefono,
            direccion=update_data.direccion,
            id_comuna=update_data.id_comuna,
            foto_perfil=update_data.foto_perfil,
        )

        if not updated_vecino:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Vecino no encontrado"
            )

        # Convertir foto de perfil binaria a base64 para respuesta
        foto_perfil_base64 = None
        if updated_vecino.foto_perfil:
            # Detectar si es SVG o imagen rasterizada
            if (
                updated_vecino.foto_perfil.startswith(b"<svg")
                or b"<svg" in updated_vecino.foto_perfil[:100]
            ):
                foto_perfil_base64 = binary_to_base64(
                    updated_vecino.foto_perfil, "image/svg+xml"
                )
            else:
                foto_perfil_base64 = binary_to_base64(
                    updated_vecino.foto_perfil, "image/jpeg"
                )

        # Obtener información de comuna y región para la respuesta
        from src.database.models.vecino import Vecino
        from src.database.models.comuna import Comuna
        from src.database.models.region import Region
        from sqlalchemy.orm import selectinload
        
        result = await db.execute(
            select(Vecino)
            .options(selectinload(Vecino.comuna).selectinload(Comuna.region))
            .where(Vecino.id_vecino == updated_vecino.id_vecino)
        )
        vecino_with_relations = result.scalar_one_or_none()
        
        comuna_nombre = None
        region_nombre = None
        if vecino_with_relations and vecino_with_relations.comuna:
            comuna_nombre = vecino_with_relations.comuna.nombre
            if vecino_with_relations.comuna.region:
                region_nombre = vecino_with_relations.comuna.region.nombre

        return VecinoUpdateResponse(
            id_vecino=updated_vecino.id_vecino,
            nombres=updated_vecino.nombres,
            apellido_paterno=updated_vecino.apellido_paterno,
            apellido_materno=updated_vecino.apellido_materno,
            rut=updated_vecino.rut,
            fecha_nacimiento=updated_vecino.fecha_nacimiento,
            email=updated_vecino.email or "",
            telefono=updated_vecino.telefono,
            direccion=updated_vecino.direccion,
            id_comuna=updated_vecino.id_comuna,
            comuna=comuna_nombre,
            region=region_nombre,
            foto_perfil=foto_perfil_base64,
            mensaje="Datos actualizados correctamente",
        )

    except ValueError as e:
        # Errores de validación
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        # Errores internos
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar vecino: {str(e)}",
        )


@router.patch(
    "/profile",
    response_model=VecinoUpdateResponse,
    summary="Actualizar mi perfil",
    description="Permite al usuario autenticado actualizar su propio perfil (email, teléfono y foto).",
)
async def update_my_profile(
    update_data: VecinoUpdateRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user_id: int = Depends(verify_user_token),
):
    """
    Actualiza el perfil del usuario autenticado.
    """
    try:
        user_service = UserService(db)

        # Obtener el vecino asociado al usuario autenticado
        vecino = await user_service.get_vecino_by_user_id(current_user_id)
        if not vecino:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Perfil de vecino no encontrado",
            )

        # Actualizar vecino
        updated_vecino = await user_service.update_vecino_profile(
            vecino_id=vecino.id_vecino,
            apellido_paterno=update_data.apellido_paterno,
            apellido_materno=update_data.apellido_materno,
            email=update_data.email,
            telefono=update_data.telefono,
            direccion=update_data.direccion,
            id_comuna=update_data.id_comuna,
            comuna_nombre=update_data.comuna_nombre,
            foto_perfil=update_data.foto_perfil,
        )

        if not updated_vecino:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Error al actualizar el perfil",
            )

        # Convertir foto de perfil binaria a base64 para respuesta
        foto_perfil_base64 = None
        if updated_vecino.foto_perfil:
            # Detectar si es SVG o imagen rasterizada
            if (
                updated_vecino.foto_perfil.startswith(b"<svg")
                or b"<svg" in updated_vecino.foto_perfil[:100]
            ):
                foto_perfil_base64 = binary_to_base64(
                    updated_vecino.foto_perfil, "image/svg+xml"
                )
            else:
                foto_perfil_base64 = binary_to_base64(
                    updated_vecino.foto_perfil, "image/jpeg"
                )

        # Obtener información de comuna y región para la respuesta
        from src.database.models.vecino import Vecino
        from src.database.models.comuna import Comuna
        from src.database.models.region import Region
        from sqlalchemy.orm import selectinload
        
        result = await db.execute(
            select(Vecino)
            .options(selectinload(Vecino.comuna).selectinload(Comuna.region))
            .where(Vecino.id_vecino == updated_vecino.id_vecino)
        )
        vecino_with_relations = result.scalar_one_or_none()
        
        comuna_nombre = None
        region_nombre = None
        if vecino_with_relations and vecino_with_relations.comuna:
            comuna_nombre = vecino_with_relations.comuna.nombre
            if vecino_with_relations.comuna.region:
                region_nombre = vecino_with_relations.comuna.region.nombre

        return VecinoUpdateResponse(
            id_vecino=updated_vecino.id_vecino,
            nombres=updated_vecino.nombres,
            apellido_paterno=updated_vecino.apellido_paterno,
            apellido_materno=updated_vecino.apellido_materno,
            rut=updated_vecino.rut,
            fecha_nacimiento=updated_vecino.fecha_nacimiento,
            email=updated_vecino.email or "",
            telefono=updated_vecino.telefono,
            direccion=updated_vecino.direccion,
            id_comuna=updated_vecino.id_comuna,
            comuna=comuna_nombre,
            region=region_nombre,
            foto_perfil=foto_perfil_base64,
            mensaje="Perfil actualizado correctamente",
        )

    except ValueError as e:
        # Errores de validación
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        # Errores internos
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar perfil: {str(e)}",
        )


@router.post(
    "/change-password",
    response_model=ChangePasswordResponse,
    summary="Cambiar contraseña",
    description="Permite al usuario autenticado cambiar su contraseña.",
)
async def change_password(
    password_data: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user_id: int = Depends(verify_user_token),
):
    """
    Cambia la contraseña del usuario autenticado.
    
    Requiere:
    - Contraseña actual correcta
    - Nueva contraseña que cumpla con los requisitos de seguridad
    - Nueva contraseña diferente a la actual
    """
    try:
        user_service = UserService(db)
        
        success = await user_service.change_password(
            user_id=current_user_id,
            current_password=password_data.current_password,
            new_password=password_data.new_password,
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al cambiar la contraseña",
            )
        
        return ChangePasswordResponse(
            success=True,
            mensaje="Contraseña actualizada exitosamente",
        )
    
    except ValueError as e:
        # Errores de validación (contraseña incorrecta, validación fallida, etc.)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except HTTPException:
        raise
    except Exception as e:
        # Errores internos
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al cambiar contraseña: {str(e)}",
        )


@router.get(
    "/vecinos/mi-junta",
    response_model=list[VecinoListResponse],
    summary="Listar vecinos de mi junta",
    description="Obtiene la lista de vecinos de la junta del usuario autenticado (vecino o directivo)",
    responses={
        200: {"description": "Lista de vecinos de la junta del usuario"},
        401: {"description": "Token de autorización requerido"},
        403: {"description": "Usuario no tiene perfil de vecino ni de directivo"},
        404: {"description": "Usuario no pertenece a ninguna junta"},
    },
)
async def get_my_junta_vecinos(
    activos_only: bool = False,
    current_user_id: int = Depends(verify_user_token),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Obtiene los vecinos de la junta del usuario autenticado.
    
    Args:
        activos_only: Si True, solo devuelve vecinos activos
        current_user_id: ID del usuario autenticado (obtenido del token)
        db: Sesión de base de datos
    
    Returns:
        Lista de vecinos de la junta del usuario autenticado
    """
    try:
        user_service = UserService(db)
        
        # Obtener vecinos de la junta del usuario
        vecinos = await user_service.get_vecinos_by_user_junta(
            current_user_id, activos_only
        )
        
        # Convertir a response format
        vecinos_response = []
        for vecino in vecinos:
            foto_perfil_base64 = None
            if vecino.foto_perfil:
                if (
                    vecino.foto_perfil.startswith(b"<svg")
                    or b"<svg" in vecino.foto_perfil[:100]
                ):
                    foto_perfil_base64 = binary_to_base64(
                        vecino.foto_perfil, "image/svg+xml"
                    )
                else:
                    foto_perfil_base64 = binary_to_base64(vecino.foto_perfil, "image/jpeg")

            # Obtener estado activo del usuario
            activo = vecino.usuario.activo if vecino.usuario else False
            
            # Obtener nombres de junta, comuna y región
            junta_nombre = vecino.junta.nombre if vecino.junta else None
            comuna_nombre = vecino.comuna.nombre if vecino.comuna else None
            region_nombre = vecino.comuna.region.nombre if vecino.comuna and vecino.comuna.region else None

            vecinos_response.append(VecinoListResponse(
                id_vecino=vecino.id_vecino,
                id_usuario=vecino.id_usuario,
                rut=vecino.rut,
                nombres=vecino.nombres,
                apellido_paterno=vecino.apellido_paterno,
                apellido_materno=vecino.apellido_materno,
                email=vecino.email,
                telefono=vecino.telefono,
                direccion=vecino.direccion,
                fecha_nacimiento=vecino.fecha_nacimiento,
                foto_perfil=foto_perfil_base64,
                activo=activo,
                junta_nombre=junta_nombre,
                comuna_nombre=comuna_nombre,
                region_nombre=region_nombre,
            ))

        return vecinos_response

    except ValueError as e:
        # Errores de validación (usuario sin vecino, vecino sin junta, etc.)
        if "perfil de vecino" in str(e):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e),
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        # Errores internos
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener vecinos: {str(e)}",
        )
