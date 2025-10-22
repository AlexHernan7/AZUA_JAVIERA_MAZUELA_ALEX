"""
Rutas para directivos de juntas de vecinos.

Contiene endpoints para registro y gestión de directivos.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError
import logging

from src.database.session import get_db_session
from src.services.directiva_service import DirectivaService
from src.schemas.directiva_schemas import (
    DirectivaRegistroRequest,
    DirectivaRegistroResponse,
    DirectivaResponse,
    ErrorResponse,
)
from src.utils import binary_to_base64
from src.api.routes.user_routes import verify_admin_user, verify_user_token

# Crear router para rutas de directivos
router = APIRouter(prefix="/directiva", tags=["Directivos"])

logger = logging.getLogger(__name__)


@router.post(
    "/register",
    response_model=DirectivaRegistroResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo directivo (Solo Admin)",
    description="Registra un nuevo directivo y crea su usuario con rol de directiva. Requiere permisos de administrador.",
    responses={
        201: {"description": "Directivo registrado exitosamente"},
        400: {"model": ErrorResponse, "description": "Error de validación"},
        401: {"description": "Token de autorización requerido"},
        403: {"description": "Se requieren permisos de administrador"},
        409: {"model": ErrorResponse, "description": "Email o RUT ya registrado"},
    },
)
async def register_directivo(
    directivo_data: DirectivaRegistroRequest, 
    admin_user_id: int = Depends(verify_admin_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Registra un nuevo directivo y crea su usuario asociado.
    
    Args:
        directivo_data: Datos del directivo a registrar
        db: Sesión de base de datos
    
    Returns:
        Datos del usuario y directivo creados
    """
    try:
        logger.info(f"🔄 Iniciando registro de directivo: {directivo_data.email} por admin ID: {admin_user_id}")

        # Crear servicio de directivos
        directiva_service = DirectivaService(db)
        logger.info("✅ Servicio de directivos creado")

        # Registrar directivo
        logger.info(
            f"🔄 Registrando directivo en junta {directivo_data.id_junta}, cargo: {directivo_data.cargo}"
        )
        usuario, directiva = await directiva_service.register_directivo(directivo_data)
        logger.info(
            f"✅ Directivo registrado exitosamente: ID {usuario.id_usuario}, Directiva ID {directiva.id_directiva}"
        )

        # Convertir foto de perfil binaria a base64 para respuesta
        foto_perfil_base64 = None
        if directiva.foto_perfil:
            # Detectar si es SVG o imagen rasterizada
            if (
                directiva.foto_perfil.startswith(b"<svg")
                or b"<svg" in directiva.foto_perfil[:100]
            ):
                foto_perfil_base64 = binary_to_base64(
                    directiva.foto_perfil, "image/svg+xml"
                )
            else:
                foto_perfil_base64 = binary_to_base64(directiva.foto_perfil, "image/jpeg")

        # Logging para debugging
        logger.info(f"📋 usuario.id_usuario: {usuario.id_usuario}")
        logger.info(f"📋 directiva.id_usuario: {directiva.id_usuario}")
        logger.info(f"📋 directiva.id_directiva: {directiva.id_directiva}")

        # Preparar respuesta
        directiva_response = DirectivaResponse(
            id_usuario=directiva.id_usuario,  # Usar el id_usuario de directiva, no de usuario
            id_directiva=directiva.id_directiva,
            rut=directiva.rut,
            nombres=directiva.nombres,
            apellido_paterno=directiva.apellido_paterno,
            apellido_materno=directiva.apellido_materno,
            telefono=directiva.telefono,
            email=directiva.email,
            cargo=directiva.cargo,
            fecha_inicio_cargo=directiva.fecha_inicio_cargo,
            fecha_termino_cargo=directiva.fecha_termino_cargo,
            foto_perfil=foto_perfil_base64,
        )
        
        logger.info(f"✅ DirectivaResponse creado correctamente")

        return DirectivaRegistroResponse(
            id_usuario=usuario.id_usuario, 
            directiva=directiva_response
        )

    except ValidationError as e:
        # Errores de validación de Pydantic
        logger.error(f"❌ Error de validación de Pydantic: {str(e)}")
        logger.error(f"❌ Detalles: {e.errors()}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Error de validación del schema",
                "detalle": str(e),
                "errores": e.errors(),
                "codigo": "SCHEMA_VALIDATION_ERROR",
            },
        )

    except ValueError as e:
        # Errores de validación de negocio
        logger.error(f"❌ Error de validación de negocio: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Error de validación",
                "detalle": str(e),
                "codigo": "VALIDATION_ERROR",
            },
        )

    except Exception as e:
        # Errores inesperados
        logger.error(f"❌ Error interno del servidor: {str(e)}")
        logger.error(f"❌ Tipo de error: {type(e).__name__}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Error interno del servidor",
                "detalle": str(e),
                "codigo": "INTERNAL_ERROR",
            },
        )


@router.get(
    "/junta/{junta_id}",
    response_model=list[DirectivaResponse],
    summary="Listar directivos de una junta",
    description="Obtiene la lista de todos los directivos de una junta específica",
)
async def get_directivos_by_junta(
    junta_id: int, 
    activos_only: bool = False,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Obtiene los directivos de una junta específica.
    
    Args:
        junta_id: ID de la junta
        activos_only: Si True, solo devuelve directivos activos
        db: Sesión de base de datos
    
    Returns:
        Lista de directivos de la junta
    """
    try:
        directiva_service = DirectivaService(db)
        
        if activos_only:
            directivos = await directiva_service.get_directivos_activos_by_junta(junta_id)
        else:
            directivos = await directiva_service.get_directivos_by_junta(junta_id)

        # Convertir a response format
        directivos_response = []
        for directiva in directivos:
            foto_perfil_base64 = None
            if directiva.foto_perfil:
                if (
                    directiva.foto_perfil.startswith(b"<svg")
                    or b"<svg" in directiva.foto_perfil[:100]
                ):
                    foto_perfil_base64 = binary_to_base64(
                        directiva.foto_perfil, "image/svg+xml"
                    )
                else:
                    foto_perfil_base64 = binary_to_base64(directiva.foto_perfil, "image/jpeg")

            directivos_response.append(DirectivaResponse(
                id_usuario=directiva.id_usuario,
                id_directiva=directiva.id_directiva,
                rut=directiva.rut,
                nombres=directiva.nombres,
                apellido_paterno=directiva.apellido_paterno,
                apellido_materno=directiva.apellido_materno,
                telefono=directiva.telefono,
                email=directiva.email,
                cargo=directiva.cargo,
                fecha_inicio_cargo=directiva.fecha_inicio_cargo,
                fecha_termino_cargo=directiva.fecha_termino_cargo,
                foto_perfil=foto_perfil_base64,
            ))

        return directivos_response

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error al obtener directivos", "detalle": str(e)},
        )


@router.get(
    "/mi-junta",
    response_model=list[DirectivaResponse],
    summary="Listar directivos de mi junta",
    description="Obtiene la lista de directivos de la junta del vecino autenticado",
    responses={
        200: {"description": "Lista de directivos de la junta del usuario"},
        401: {"description": "Token de autorización requerido"},
        403: {"description": "Usuario no tiene perfil de vecino"},
        404: {"description": "Usuario no pertenece a ninguna junta"},
    },
)
async def get_my_junta_directivos(
    activos_only: bool = False,
    current_user_id: int = Depends(verify_user_token),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Obtiene los directivos de la junta del vecino autenticado.
    
    Args:
        activos_only: Si True, solo devuelve directivos activos
        current_user_id: ID del usuario autenticado (obtenido del token)
        db: Sesión de base de datos
    
    Returns:
        Lista de directivos de la junta del usuario autenticado
    """
    try:
        logger.info(f"🔄 Obteniendo directivos de la junta para usuario ID: {current_user_id}")
        
        directiva_service = DirectivaService(db)
        
        # Obtener directivos de la junta del usuario
        directivos = await directiva_service.get_directivos_by_user_junta(
            current_user_id, activos_only
        )
        
        logger.info(f"✅ Encontrados {len(directivos)} directivos")

        # Convertir a response format
        directivos_response = []
        for directiva in directivos:
            foto_perfil_base64 = None
            if directiva.foto_perfil:
                if (
                    directiva.foto_perfil.startswith(b"<svg")
                    or b"<svg" in directiva.foto_perfil[:100]
                ):
                    foto_perfil_base64 = binary_to_base64(
                        directiva.foto_perfil, "image/svg+xml"
                    )
                else:
                    foto_perfil_base64 = binary_to_base64(directiva.foto_perfil, "image/jpeg")

            directivos_response.append(DirectivaResponse(
                id_usuario=directiva.id_usuario,
                id_directiva=directiva.id_directiva,
                rut=directiva.rut,
                nombres=directiva.nombres,
                apellido_paterno=directiva.apellido_paterno,
                apellido_materno=directiva.apellido_materno,
                telefono=directiva.telefono,
                email=directiva.email,
                cargo=directiva.cargo,
                fecha_inicio_cargo=directiva.fecha_inicio_cargo,
                fecha_termino_cargo=directiva.fecha_termino_cargo,
                foto_perfil=foto_perfil_base64,
            ))

        return directivos_response

    except ValueError as e:
        # Errores de validación (usuario sin vecino, vecino sin junta, etc.)
        logger.warning(f"❌ Error de validación para usuario {current_user_id}: {str(e)}")
        if "perfil de vecino" in str(e):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"error": "Acceso denegado", "detalle": str(e)},
            )
        elif "no pertenece a ninguna junta" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Junta no encontrada", "detalle": str(e)},
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "Error de validación", "detalle": str(e)},
            )
    
    except Exception as e:
        logger.error(f"❌ Error interno al obtener directivos para usuario {current_user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error al obtener directivos", "detalle": str(e)},
        )
