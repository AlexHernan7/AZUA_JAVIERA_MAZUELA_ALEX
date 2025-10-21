"""
Rutas para gestión de espacios comunitarios.

Contiene endpoints para crear, consultar y gestionar espacios comunitarios.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
import logging
import os
import uuid
from pathlib import Path

from src.database.session import get_db_session
from src.services.espacio_service import EspacioService
from src.schemas.espacio_schemas import (
    EspacioCreateRequest,
    EspacioUpdateRequest,
    EspacioResponse,
    EspacioListResponse,
    EspacioDirectivaUpdateRequest,
    EspacioDirectivaUpdateResponse,
)
from src.schemas.auth_schemas import ErrorResponse
from src.api.routes.user_routes import verify_user_token, verify_directiva_user

# Crear router para rutas de espacios
router = APIRouter(prefix="/espacios", tags=["Espacios"])

logger = logging.getLogger(__name__)


@router.post(
    "/",
    response_model=EspacioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo espacio comunitario",
    description="Crea un nuevo espacio comunitario en una junta de vecinos. Requiere autenticación.",
    responses={
        201: {"description": "Espacio creado exitosamente"},
        400: {"model": ErrorResponse, "description": "Error de validación"},
        401: {"description": "Token de autorización requerido"},
        404: {"model": ErrorResponse, "description": "Junta no encontrada"},
        409: {"model": ErrorResponse, "description": "Conflicto de datos"},
    },
)
async def create_espacio(
    # Campos del formulario
    nombre: str = Form(...),
    id_tipo: int = Form(...),
    capacidad: int = Form(...),
    valor: float = Form(...),
    max_horas: int = Form(4),
    activo: bool = Form(True),
    id_junta: int = Form(...),
    permitido: Optional[List[str]] = Form(None),
    no_permitido: Optional[List[str]] = Form(None),
    # Archivo opcional
    foto: Optional[UploadFile] = File(None),
    user_id: int = Depends(verify_user_token),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Crea un nuevo espacio comunitario con o sin archivo.
    
    Args:
        nombre: Nombre del espacio
        id_tipo: ID del tipo de espacio
        capacidad: Capacidad máxima
        valor: Precio por hora
        max_horas: Máximo de horas por reserva
        activo: Si está activo
        id_junta: ID de la junta
        permitido: Lista de actividades permitidas
        no_permitido: Lista de actividades no permitidas
        foto: Archivo de imagen (opcional)
        user_id: ID del usuario autenticado
        db: Sesión de base de datos
    
    Returns:
        Datos del espacio creado
    """
    try:
        logger.info(f"🔄 Usuario {user_id} creando espacio: {nombre}")
        
        # Procesar archivo si existe - convertir a binario
        foto_binary = None
        if foto and foto.filename:
            # Leer el contenido del archivo
            file_content = await foto.read()
            foto_binary = file_content  # Ya es bytes, lo guardamos directamente
            logger.info(f"📷 Foto procesada: {len(file_content)} bytes")
        
        # Crear objeto de datos del espacio
        espacio_data = EspacioCreateRequest(
            nombre=nombre,
            id_tipo=id_tipo,
            capacidad=capacidad,
            valor=valor,
            max_horas=max_horas,
            activo=activo,
            id_junta=id_junta,
            permitido=permitido or [],
            no_permitido=no_permitido or [],
            foto=foto_binary  # Ahora es binario
        )
        
        espacio_service = EspacioService(db)
        espacio_creado = await espacio_service.create_espacio(espacio_data, user_id)
        
        logger.info(f"✅ Espacio '{espacio_creado.nombre}' creado exitosamente con ID {espacio_creado.id_espacio}")
        return espacio_creado
        
    except ValueError as e:
        logger.warning(f"⚠️ Error de validación al crear espacio: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ Error inesperado al crear espacio: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get(
    "/{espacio_id}",
    response_model=EspacioResponse,
    summary="Obtener espacio por ID",
    description="Obtiene los datos de un espacio comunitario específico.",
    responses={
        200: {"description": "Espacio encontrado"},
        404: {"model": ErrorResponse, "description": "Espacio no encontrado"},
    },
)
async def get_espacio(
    espacio_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Obtiene un espacio por su ID.
    
    Args:
        espacio_id: ID del espacio
        db: Sesión de base de datos
    
    Returns:
        Datos del espacio
    """
    try:
        espacio_service = EspacioService(db)
        espacio = await espacio_service.get_espacio_by_id(espacio_id)
        
        if not espacio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Espacio con ID {espacio_id} no encontrado"
            )
        
        return espacio
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error al obtener espacio {espacio_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get(
    "/junta/{id_junta}",
    response_model=EspacioListResponse,
    summary="Obtener espacios de una junta",
    description="Obtiene todos los espacios comunitarios de una junta específica.",
    responses={
        200: {"description": "Lista de espacios obtenida exitosamente"},
        400: {"model": ErrorResponse, "description": "Parámetros inválidos"},
    },
)
async def get_espacios_by_junta(
    id_junta: int,
    activo_only: bool = Query(default=True, description="Solo mostrar espacios activos"),
    pagina: int = Query(default=1, ge=1, description="Número de página"),
    por_pagina: int = Query(default=10, ge=1, le=100, description="Elementos por página"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Obtiene todos los espacios de una junta.
    
    Args:
        id_junta: ID de la junta
        activo_only: Si solo mostrar espacios activos
        pagina: Número de página (1-indexed)
        por_pagina: Elementos por página
        db: Sesión de base de datos
    
    Returns:
        Lista paginada de espacios
    """
    try:
        espacio_service = EspacioService(db)
        espacios = await espacio_service.get_espacios_by_junta(
            id_junta=id_junta,
            activo_only=activo_only,
            pagina=pagina,
            por_pagina=por_pagina
        )
        
        return espacios
        
    except Exception as e:
        logger.error(f"❌ Error al obtener espacios de junta {id_junta}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.put(
    "/{espacio_id}",
    response_model=EspacioResponse,
    summary="Actualizar espacio comunitario",
    description="Actualiza los datos de un espacio comunitario existente. Requiere autenticación.",
    responses={
        200: {"description": "Espacio actualizado exitosamente"},
        400: {"model": ErrorResponse, "description": "Error de validación"},
        401: {"description": "Token de autorización requerido"},
        404: {"model": ErrorResponse, "description": "Espacio no encontrado"},
    },
)
async def update_espacio(
    espacio_id: int,
    espacio_data: EspacioUpdateRequest,
    user_id: int = Depends(verify_user_token),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Actualiza un espacio existente.
    
    Args:
        espacio_id: ID del espacio a actualizar
        espacio_data: Datos a actualizar
        user_id: ID del usuario autenticado (validado automáticamente)
        db: Sesión de base de datos
    
    Returns:
        Datos del espacio actualizado
    """
    try:
        logger.info(f"🔄 Usuario {user_id} actualizando espacio {espacio_id}")
        
        espacio_service = EspacioService(db)
        espacio_actualizado = await espacio_service.update_espacio(
            espacio_id, espacio_data, user_id
        )
        
        if not espacio_actualizado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Espacio con ID {espacio_id} no encontrado"
            )
        
        logger.info(f"✅ Espacio {espacio_id} actualizado exitosamente")
        return espacio_actualizado
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"⚠️ Error de validación al actualizar espacio: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ Error inesperado al actualizar espacio {espacio_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.patch(
    "/directiva/{espacio_id}",
    response_model=EspacioDirectivaUpdateResponse,
    summary="Actualizar espacio (Solo Directiva)",
    description="Actualiza los datos editables de un espacio. Solo el usuario directiva de esa junta puede actualizar. Campos editables: capacidad, valor, foto, permitido, no_permitido, max_horas.",
    responses={
        200: {"description": "Espacio actualizado exitosamente"},
        400: {"model": ErrorResponse, "description": "Error de validación"},
        401: {"description": "Token de autorización requerido"},
        403: {"model": ErrorResponse, "description": "Se requieren permisos de directiva o no tiene permisos para editar este espacio"},
        404: {"model": ErrorResponse, "description": "Espacio no encontrado"},
    },
)
async def update_espacio_directiva(
    espacio_id: int,
    update_data: EspacioDirectivaUpdateRequest,
    directiva_info: tuple[int, int] = Depends(verify_directiva_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Actualiza los datos de un espacio comunitario (solo para directivas).
    
    Solo puede ser ejecutado por un usuario con rol directiva, y únicamente
    puede actualizar espacios de su propia junta.
    
    Campos que se pueden actualizar:
    - capacidad: Capacidad máxima de personas
    - valor: Precio por hora en CLP
    - foto: Foto del espacio en formato base64
    - permitido: Lista de actividades permitidas
    - no_permitido: Lista de actividades no permitidas
    - max_horas: Máximo de horas por reserva
    
    Args:
        espacio_id: ID del espacio a actualizar
        update_data: Datos a actualizar (al menos uno debe ser proporcionado)
        directiva_info: Tupla (user_id, junta_id) del usuario directiva (validado automáticamente)
        db: Sesión de base de datos
    
    Returns:
        Datos actualizados del espacio
    """
    try:
        user_id, directiva_junta_id = directiva_info
        
        logger.info(f"🔄 Directiva {user_id} iniciando actualización de espacio {espacio_id}")
        
        service = EspacioService(db)
        espacio_actualizado = await service.update_espacio_directiva(
            espacio_id=espacio_id,
            update_data=update_data,
            directiva_junta_id=directiva_junta_id
        )
        
        logger.info(f"✅ Espacio {espacio_id} actualizado exitosamente por directiva {user_id}")
        return espacio_actualizado
        
    except ValueError as e:
        logger.warning(f"❌ Error de validación actualizando espacio {espacio_id}: {str(e)}")
        
        # Determinar código de error apropiado
        if "no encontrado" in str(e).lower():
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
        logger.error(f"💥 Error inesperado actualizando espacio {espacio_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error interno del servidor", "detalle": str(e)}
        )


@router.delete(
    "/{espacio_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar espacio comunitario",
    description="Elimina un espacio comunitario (soft delete). Requiere autenticación.",
    responses={
        204: {"description": "Espacio eliminado exitosamente"},
        401: {"description": "Token de autorización requerido"},
        404: {"model": ErrorResponse, "description": "Espacio no encontrado"},
    },
)
async def delete_espacio(
    espacio_id: int,
    user_id: int = Depends(verify_user_token),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Elimina un espacio (soft delete - lo marca como inactivo).
    
    Args:
        espacio_id: ID del espacio a eliminar
        user_id: ID del usuario autenticado (validado automáticamente)
        db: Sesión de base de datos
    
    Returns:
        Status 204 si se eliminó exitosamente
    """
    try:
        logger.info(f"🔄 Usuario {user_id} eliminando espacio {espacio_id}")
        
        espacio_service = EspacioService(db)
        eliminado = await espacio_service.delete_espacio(espacio_id, user_id)
        
        if not eliminado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Espacio con ID {espacio_id} no encontrado"
            )
        
        logger.info(f"✅ Espacio {espacio_id} eliminado exitosamente")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error inesperado al eliminar espacio {espacio_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.delete(
    "/directiva/{espacio_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar espacio (Solo Directiva)",
    description="Elimina (soft delete) un espacio si pertenece a la junta del usuario directiva.",
    responses={
        204: {"description": "Espacio eliminado exitosamente"},
        401: {"description": "Token de autorización requerido"},
        403: {"model": ErrorResponse, "description": "No tienes permisos para eliminar este espacio"},
        404: {"model": ErrorResponse, "description": "Espacio no encontrado"},
    },
)
async def delete_espacio_directiva(
    espacio_id: int,
    directiva_info: tuple[int, int] = Depends(verify_directiva_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Elimina (soft delete) un espacio si pertenece a la junta del usuario directiva.
    """
    try:
        user_id, directiva_junta_id = directiva_info
        logger.info(f"🔄 Directiva {user_id} eliminando espacio {espacio_id}")

        servicio = EspacioService(db)
        eliminado = await servicio.delete_espacio_directiva(espacio_id, directiva_junta_id)
        if not eliminado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "No encontrado", "detalle": f"Espacio {espacio_id} no existe"}
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "Acceso denegado", "detalle": str(e)}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error eliminando espacio {espacio_id} por directiva: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error interno del servidor", "detalle": str(e)}
        )

async def save_uploaded_file(file: UploadFile) -> str:
    """
    Guarda un archivo subido y retorna la ruta relativa.
    
    Args:
        file: Archivo subido
        
    Returns:
        Ruta relativa del archivo guardado
    """
    # Crear directorio de uploads si no existe
    upload_dir = Path("uploads/espacios")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generar nombre único para el archivo
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = upload_dir / unique_filename
    
    # Guardar archivo
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Retornar ruta relativa
    return f"uploads/espacios/{unique_filename}"
