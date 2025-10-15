"""
Rutas para gestión de juntas de vecinos.

Contiene endpoints para registro y consulta de juntas.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import logging

from src.database.session import get_db_session
from src.services.junta_service import JuntaService
from src.schemas.junta_schemas import (
    JuntaCreateRequest,
    JuntaCreateResponse,
    JuntaResponse,
    JuntasList,
    JuntaUpdateRequest,
    JuntaUpdateResponse,
    ErrorResponse,
)
from src.api.routes.user_routes import verify_admin_user, verify_directiva_user

# Crear router para rutas de juntas
router = APIRouter(prefix="/juntas", tags=["Juntas"])

logger = logging.getLogger(__name__)


@router.post(
    "/",
    response_model=JuntaCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva junta (Solo Admin)",
    description="Registra una nueva junta de vecinos. Requiere permisos de administrador.",
    responses={
        201: {"description": "Junta creada exitosamente"},
        400: {"model": ErrorResponse, "description": "Error de validación"},
        401: {"description": "Token de autorización requerido"},
        403: {"description": "Se requieren permisos de administrador"},
        409: {"model": ErrorResponse, "description": "RUT o nombre ya registrado"},
    },
)
async def create_junta(
    junta_data: JuntaCreateRequest,
    admin_user_id: int = Depends(verify_admin_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Crea una nueva junta de vecinos.
    
    Args:
        junta_data: Datos de la junta a crear
        admin_user_id: ID del usuario administrador (validado automáticamente)
        db: Sesión de base de datos
    
    Returns:
        Datos de la junta creada
    """
    try:
        logger.info(f"🔄 Admin {admin_user_id} iniciando creación de junta: {junta_data.nombre}")
        
        service = JuntaService(db)
        junta_creada = await service.create_junta(junta_data)
        
        logger.info(f"✅ Junta creada exitosamente: {junta_creada.nombre} (ID: {junta_creada.id_junta})")
        return junta_creada
        
    except ValueError as e:
        logger.warning(f"❌ Error de validación creando junta: {str(e)}")
        # Determinar si es conflicto o validación
        if "ya existe" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"error": "Conflicto de datos", "detalle": str(e)}
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "Error de validación", "detalle": str(e)}
            )
    except Exception as e:
        logger.error(f"💥 Error inesperado creando junta: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error interno del servidor", "detalle": str(e)}
        )


@router.get(
    "/{junta_id}",
    response_model=JuntaResponse,
    summary="Obtener junta por ID",
    description="Obtiene los datos completos de una junta específica",
    responses={
        200: {"description": "Datos de la junta obtenidos exitosamente"},
        404: {"model": ErrorResponse, "description": "Junta no encontrada"},
    },
)
async def get_junta_by_id(
    junta_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Obtiene una junta por su ID.
    
    Args:
        junta_id: ID de la junta
        db: Sesión de base de datos
    
    Returns:
        Datos completos de la junta
    """
    try:
        service = JuntaService(db)
        junta = await service.get_junta_by_id(junta_id)
        
        if not junta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Junta no encontrada", "detalle": f"No existe junta con ID {junta_id}"}
            )
        
        logger.info(f"📋 Datos de junta {junta_id} obtenidos exitosamente")
        return junta
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Error obteniendo junta {junta_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error interno del servidor", "detalle": str(e)}
        )


@router.get(
    "/",
    response_model=JuntasList,
    summary="Listar juntas",
    description="Obtiene lista de juntas con filtros opcionales",
    responses={
        200: {"description": "Lista de juntas obtenida exitosamente"},
    },
)
async def list_juntas(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(50, ge=1, le=100, description="Número máximo de registros (1-100)"),
    activa: Optional[bool] = Query(None, description="Filtrar por estado activo (true/false)"),
    comuna_id: Optional[int] = Query(None, ge=1, description="Filtrar por ID de comuna"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Lista las juntas con filtros opcionales.
    
    Args:
        skip: Número de registros a saltar para paginación
        limit: Número máximo de registros a retornar
        activa: Si se especifica, filtra por estado activo
        comuna_id: Si se especifica, filtra por comuna
        db: Sesión de base de datos
    
    Returns:
        Lista de juntas con estadísticas
    """
    try:
        service = JuntaService(db)
        resultado = await service.list_juntas(
            skip=skip,
            limit=limit,
            activa_only=activa,
            comuna_id=comuna_id
        )
        
        logger.info(f"📋 Lista de juntas obtenida: {resultado['total']} total, {len(resultado['juntas'])} en página")
        
        return JuntasList(
            juntas=resultado['juntas'],
            total=resultado['total'],
            activas=resultado['activas'],
            inactivas=resultado['inactivas']
        )
        
    except Exception as e:
        logger.error(f"💥 Error listando juntas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error interno del servidor", "detalle": str(e)}
        )


@router.get(
    "/comuna/{comuna_id}",
    response_model=list[JuntaResponse],
    summary="Obtener juntas por comuna",
    description="Obtiene todas las juntas activas de una comuna específica",
    responses={
        200: {"description": "Juntas de la comuna obtenidas exitosamente"},
    },
)
async def get_juntas_by_comuna(
    comuna_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Obtiene todas las juntas activas de una comuna.
    
    Args:
        comuna_id: ID de la comuna
        db: Sesión de base de datos
    
    Returns:
        Lista de juntas activas de la comuna
    """
    try:
        service = JuntaService(db)
        juntas = await service.get_juntas_by_comuna(comuna_id)
        
        logger.info(f"📋 Juntas de comuna {comuna_id} obtenidas: {len(juntas)} juntas")
        return juntas
        
    except Exception as e:
        logger.error(f"💥 Error obteniendo juntas de comuna {comuna_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error interno del servidor", "detalle": str(e)}
        )


@router.patch(
    "/{junta_id}",
    response_model=JuntaUpdateResponse,
    summary="Actualizar junta (Solo Directiva)",
    description="Actualiza los datos de una junta. Solo el usuario directiva de esa junta puede actualizarla. Campos editables: teléfono, email, descripción y logo.",
    responses={
        200: {"description": "Junta actualizada exitosamente"},
        400: {"model": ErrorResponse, "description": "Error de validación"},
        401: {"description": "Token de autorización requerido"},
        403: {"model": ErrorResponse, "description": "Se requieren permisos de directiva o no tiene permisos para editar esta junta"},
        404: {"model": ErrorResponse, "description": "Junta no encontrada"},
    },
)
async def update_junta(
    junta_id: int,
    update_data: JuntaUpdateRequest,
    directiva_info: tuple[int, int] = Depends(verify_directiva_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Actualiza los datos de una junta de vecinos.
    
    Solo puede ser ejecutado por un usuario con rol directiva, y únicamente
    puede actualizar su propia junta.
    
    Campos que se pueden actualizar:
    - teléfono: Número de contacto de la junta
    - email: Correo de contacto de la junta
    - descripción: Descripción de la junta
    - logo: Logo de la junta en formato base64
    
    Args:
        junta_id: ID de la junta a actualizar
        update_data: Datos a actualizar (al menos uno debe ser proporcionado)
        directiva_info: Tupla (user_id, junta_id) del usuario directiva (validado automáticamente)
        db: Sesión de base de datos
    
    Returns:
        Datos actualizados de la junta
    """
    try:
        user_id, directiva_junta_id = directiva_info
        
        logger.info(f"🔄 Directiva {user_id} iniciando actualización de junta {junta_id}")
        
        service = JuntaService(db)
        junta_actualizada = await service.update_junta(
            junta_id=junta_id,
            update_data=update_data,
            directiva_junta_id=directiva_junta_id
        )
        
        logger.info(f"✅ Junta {junta_id} actualizada exitosamente por directiva {user_id}")
        return junta_actualizada
        
    except ValueError as e:
        logger.warning(f"❌ Error de validación actualizando junta {junta_id}: {str(e)}")
        
        # Determinar código de error apropiado
        if "no encontrada" in str(e).lower():
            status_code = status.HTTP_404_NOT_FOUND
        elif "no tienes permisos" in str(e).lower():
            status_code = status.HTTP_403_FORBIDDEN
        else:
            status_code = status.HTTP_400_BAD_REQUEST
        
        raise HTTPException(
            status_code=status_code,
            detail={"error": "Error de validación", "detalle": str(e)}
        )
    except Exception as e:
        logger.error(f"💥 Error inesperado actualizando junta {junta_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error interno del servidor", "detalle": str(e)}
        )
