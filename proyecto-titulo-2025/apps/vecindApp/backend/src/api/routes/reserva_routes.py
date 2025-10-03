"""
Rutas para gestión de reservas de espacios comunitarios.

Contiene endpoints para crear, consultar y gestionar reservas de espacios.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import logging

from src.database.session import get_db_session
from src.services.reserva_service import ReservaService
from src.schemas.reserva_schemas import (
    ReservaCreateRequest,
    ReservaUpdateRequest,
    ReservaResponse,
    ReservaListResponse,
    DisponibilidadRequest,
    DisponibilidadResponse,
    ReservaConPagoRequest,
)
from src.schemas.auth_schemas import ErrorResponse
from src.api.routes.user_routes import verify_user_token

# Crear router para rutas de reservas
router = APIRouter(prefix="/reservas", tags=["Reservas"])

logger = logging.getLogger(__name__)


@router.post(
    "/",
    response_model=ReservaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva reserva de espacio",
    description="Crea una nueva reserva de espacio comunitario con validación de solapamiento. Requiere autenticación.",
    responses={
        201: {"description": "Reserva creada exitosamente"},
        400: {"model": ErrorResponse, "description": "Error de validación o conflicto de horarios"},
        401: {"description": "Token de autorización requerido"},
        404: {"model": ErrorResponse, "description": "Espacio, junta o vecino no encontrado"},
        409: {"model": ErrorResponse, "description": "Conflicto de datos"},
    },
)
async def create_reserva(
    reserva_data: ReservaCreateRequest,
    user_id: int = Depends(verify_user_token),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Crea una nueva reserva de espacio con validación de solapamiento.
    
    Args:
        reserva_data: Datos de la reserva a crear
        user_id: ID del usuario autenticado
        db: Sesión de base de datos
    
    Returns:
        Datos de la reserva creada
    """
    try:
        logger.info(f"Usuario {user_id} creando reserva para espacio {reserva_data.id_espacio}")
        
        reserva_service = ReservaService(db)
        reserva_creada = await reserva_service.create_reserva(reserva_data, user_id)
        
        logger.info(f"Reserva creada exitosamente con ID {reserva_creada.id_reserva}")
        return reserva_creada
        
    except ValueError as e:
        logger.warning(f"⚠️ Error de validación al crear reserva: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ Error inesperado al crear reserva: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post(
    "/verificar-disponibilidad",
    response_model=DisponibilidadResponse,
    summary="Verificar disponibilidad de espacio",
    description="Verifica si un espacio está disponible en un horario específico sin crear la reserva.",
    responses={
        200: {"description": "Disponibilidad verificada exitosamente"},
        400: {"model": ErrorResponse, "description": "Error de validación"},
    },
)
async def verificar_disponibilidad(
    disponibilidad_data: DisponibilidadRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Verifica la disponibilidad de un espacio en un horario específico.
    
    Args:
        disponibilidad_data: Datos para verificar disponibilidad
        db: Sesión de base de datos
    
    Returns:
        Resultado de la verificación de disponibilidad
    """
    try:
        logger.info(f"🔄 Verificando disponibilidad para espacio {disponibilidad_data.id_espacio}")
        
        reserva_service = ReservaService(db)
        resultado = await reserva_service.verificar_disponibilidad(disponibilidad_data)
        
        logger.info(f"✅ Disponibilidad verificada: {resultado.disponible}")
        return resultado
        
    except Exception as e:
        logger.error(f"❌ Error al verificar disponibilidad: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get(
    "/{reserva_id}",
    response_model=ReservaResponse,
    summary="Obtener reserva por ID",
    description="Obtiene los datos de una reserva específica.",
    responses={
        200: {"description": "Reserva encontrada"},
        404: {"model": ErrorResponse, "description": "Reserva no encontrada"},
    },
)
async def get_reserva(
    reserva_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Obtiene una reserva por su ID.
    
    Args:
        reserva_id: ID de la reserva
        db: Sesión de base de datos
    
    Returns:
        Datos de la reserva
    """
    try:
        reserva_service = ReservaService(db)
        reserva = await reserva_service.get_reserva_by_id(reserva_id)
        
        if not reserva:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reserva con ID {reserva_id} no encontrada"
            )
        
        return reserva
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error al obtener reserva {reserva_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get(
    "/espacio/{id_espacio}",
    response_model=ReservaListResponse,
    summary="Obtener reservas de un espacio",
    description="Obtiene todas las reservas de un espacio específico con filtros opcionales.",
    responses={
        200: {"description": "Lista de reservas obtenida exitosamente"},
        400: {"model": ErrorResponse, "description": "Parámetros inválidos"},
    },
)
async def get_reservas_by_espacio(
    id_espacio: int,
    fecha_desde: Optional[str] = Query(None, description="Fecha desde (YYYY-MM-DD)"),
    fecha_hasta: Optional[str] = Query(None, description="Fecha hasta (YYYY-MM-DD)"),
    pagina: int = Query(default=1, ge=1, description="Número de página"),
    por_pagina: int = Query(default=10, ge=1, le=100, description="Elementos por página"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Obtiene todas las reservas de un espacio específico.
    
    Args:
        id_espacio: ID del espacio
        fecha_desde: Fecha desde (opcional)
        fecha_hasta: Fecha hasta (opcional)
        pagina: Número de página (1-indexed)
        por_pagina: Elementos por página
        db: Sesión de base de datos
    
    Returns:
        Lista paginada de reservas
    """
    try:
        # Convertir strings de fecha a objetos date si se proporcionan
        fecha_desde_obj = None
        fecha_hasta_obj = None
        
        if fecha_desde:
            try:
                from datetime import datetime
                fecha_desde_obj = datetime.strptime(fecha_desde, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Formato de fecha_desde inválido. Use YYYY-MM-DD"
                )
        
        if fecha_hasta:
            try:
                from datetime import datetime
                fecha_hasta_obj = datetime.strptime(fecha_hasta, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Formato de fecha_hasta inválido. Use YYYY-MM-DD"
                )
        
        reserva_service = ReservaService(db)
        reservas = await reserva_service.get_reservas_by_espacio(
            id_espacio=id_espacio,
            fecha_desde=fecha_desde_obj,
            fecha_hasta=fecha_hasta_obj,
            pagina=pagina,
            por_pagina=por_pagina
        )
        
        return reservas
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error al obtener reservas del espacio {id_espacio}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.put(
    "/{reserva_id}",
    response_model=ReservaResponse,
    summary="Actualizar reserva",
    description="Actualiza los datos de una reserva existente. Requiere autenticación.",
    responses={
        200: {"description": "Reserva actualizada exitosamente"},
        400: {"model": ErrorResponse, "description": "Error de validación"},
        401: {"description": "Token de autorización requerido"},
        404: {"model": ErrorResponse, "description": "Reserva no encontrada"},
    },
)
async def update_reserva(
    reserva_id: int,
    reserva_data: ReservaUpdateRequest,
    user_id: int = Depends(verify_user_token),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Actualiza una reserva existente.
    
    Args:
        reserva_id: ID de la reserva a actualizar
        reserva_data: Datos a actualizar
        user_id: ID del usuario autenticado (validado automáticamente)
        db: Sesión de base de datos
    
    Returns:
        Datos de la reserva actualizada
    """
    try:
        logger.info(f"🔄 Usuario {user_id} actualizando reserva {reserva_id}")
        
        # TODO: Implementar lógica de actualización en el servicio
        # Por ahora, retornamos un error indicando que no está implementado
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="La funcionalidad de actualización de reservas no está implementada aún"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error inesperado al actualizar reserva {reserva_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.delete(
    "/{reserva_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancelar reserva",
    description="Cancela una reserva existente (soft delete). Requiere autenticación.",
    responses={
        204: {"description": "Reserva cancelada exitosamente"},
        401: {"description": "Token de autorización requerido"},
        404: {"model": ErrorResponse, "description": "Reserva no encontrada"},
    },
)
async def cancel_reserva(
    reserva_id: int,
    user_id: int = Depends(verify_user_token),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Cancela una reserva (soft delete - cambia el estado a 'cancelada').
    
    Args:
        reserva_id: ID de la reserva a cancelar
        user_id: ID del usuario autenticado (validado automáticamente)
        db: Sesión de base de datos
    
    Returns:
        Status 204 si se canceló exitosamente
    """
    try:
        logger.info(f"🔄 Usuario {user_id} cancelando reserva {reserva_id}")
        
        # TODO: Implementar lógica de cancelación en el servicio
        # Por ahora, retornamos un error indicando que no está implementado
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="La funcionalidad de cancelación de reservas no está implementada aún"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error inesperado al cancelar reserva {reserva_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post(
    "/webpay-payment",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Crear reserva con Webpay Plus",
    description="Crea una reserva de espacio con pago Webpay Plus y retorna token para redirección"
)
async def crear_reserva_webpay_payment(
    request: ReservaConPagoRequest,
    user_id: int = Depends(verify_user_token),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Crea una reserva pendiente de pago con Webpay Plus.
    
    Returns:
        Dict con reserva, payment_intent, payment_url y webpay_token
    """
    try:
        service = ReservaService(db)
        
        # Crear reserva con pago Webpay
        reserva, payment_intent, webpay_url, webpay_token = await service.crear_reserva_con_webpay(
            reserva_data=request,
            user_id=user_id
        )
        
        logger.info(f"🏟️💳 Reserva con Webpay creada: reserva={reserva.id_reserva}, payment={payment_intent.id_payment_intent}")
        
        return {
            "reserva": reserva,
            "payment_intent": payment_intent,
            "message": "Reserva creada. Complete el pago para confirmar la reserva.",
            "payment_url": webpay_url,
            "webpay_token": webpay_token,
            "provider": "webpay"
        }
        
    except ValueError as e:
        logger.warning(f"❌ Error creando reserva con Webpay: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Error en la solicitud", "detalle": str(e)}
        )
    except Exception as e:
        logger.error(f"💥 Error inesperado en webpay-payment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error interno del servidor", "detalle": str(e)}
        )