"""Rutas para gestión de reservas de espacios."""

from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_db_session
from src.core.security import get_current_vecino, security
from src.services.reserva_service import ReservaService
from src.schemas.reserva_schemas import (
    ReservaCreate,
    ReservaUpdate,
    ReservaResponse,
    ReservaListResponse,
    DisponibilidadRequest,
    DisponibilidadResponse,
    EstadoReserva,
    ErrorResponse
)
from src.database.models import Usuario, Vecino

router = APIRouter(prefix="/reservas", tags=["reservas"])


@router.post(
    "/",
    response_model=ReservaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva reserva",
    description="Crear una nueva reserva de espacio. Requiere autenticación como vecino."
)
async def crear_reserva(
    reserva_data: ReservaCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db_session)
):
    """Crear una nueva reserva de espacio."""
    
    # Obtener vecino actual
    current_vecino = await get_current_vecino(credentials, db)
    
    service = ReservaService(db)
    
    try:
        return await service.crear_reserva(
            reserva_data=reserva_data,
            id_vecino=current_vecino.id_vecino,
            id_usuario=current_vecino.id_usuario
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get(
    "/mis-reservas",
    response_model=ReservaListResponse,
    summary="Listar mis reservas",
    description="Obtener lista de reservas del vecino autenticado con filtros opcionales."
)
async def listar_mis_reservas(
    estado: Optional[EstadoReserva] = Query(None, description="Filtrar por estado de reserva"),
    fecha_desde: Optional[datetime] = Query(None, description="Filtrar desde fecha (ISO format)"),
    fecha_hasta: Optional[datetime] = Query(None, description="Filtrar hasta fecha (ISO format)"),
    pagina: int = Query(1, ge=1, description="Número de página"),
    por_pagina: int = Query(10, ge=1, le=100, description="Elementos por página"),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db_session)
):
    """Listar reservas del vecino autenticado."""
    
    # Obtener vecino actual
    current_vecino = await get_current_vecino(credentials, db)
    
    service = ReservaService(db)
    
    try:
        resultado = await service.listar_reservas_vecino(
            id_vecino=current_vecino.id_vecino,
            estado=estado,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            pagina=pagina,
            por_pagina=por_pagina
        )
        
        return ReservaListResponse(**resultado)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get(
    "/{id_reserva}",
    response_model=ReservaResponse,
    summary="Obtener reserva específica",
    description="Obtener detalles de una reserva específica del vecino autenticado."
)
async def obtener_reserva(
    id_reserva: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db_session)
):
    """Obtener una reserva específica."""
    
    # Obtener vecino actual
    current_vecino = await get_current_vecino(credentials, db)
    
    service = ReservaService(db)
    
    try:
        return await service.obtener_reserva(
            id_reserva=id_reserva,
            id_vecino=current_vecino.id_vecino
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.put(
    "/{id_reserva}",
    response_model=ReservaResponse,
    summary="Actualizar reserva",
    description="Actualizar una reserva existente. Solo se pueden modificar reservas pendientes."
)
async def actualizar_reserva(
    id_reserva: int,
    reserva_data: ReservaUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db_session)
):
    """Actualizar una reserva existente."""
    
    # Obtener vecino actual
    current_vecino = await get_current_vecino(credentials, db)
    
    service = ReservaService(db)
    
    try:
        return await service.actualizar_reserva(
            id_reserva=id_reserva,
            reserva_data=reserva_data,
            id_vecino=current_vecino.id_vecino
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.delete(
    "/{id_reserva}",
    response_model=ReservaResponse,
    summary="Cancelar reserva",
    description="Cancelar una reserva. Solo se puede cancelar con al menos 2 horas de anticipación."
)
async def cancelar_reserva(
    id_reserva: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db_session)
):
    """Cancelar una reserva."""
    
    # Obtener vecino actual
    current_vecino = await get_current_vecino(credentials, db)
    
    service = ReservaService(db)
    
    try:
        return await service.cancelar_reserva(
            id_reserva=id_reserva,
            id_vecino=current_vecino.id_vecino
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.post(
    "/disponibilidad",
    response_model=DisponibilidadResponse,
    summary="Consultar disponibilidad",
    description="Consultar disponibilidad de un espacio en una fecha específica."
)
async def consultar_disponibilidad(
    disponibilidad_data: DisponibilidadRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db_session)
):
    """Consultar disponibilidad de un espacio."""
    
    # Verificar autenticación (no necesariamente vecino)
    await get_current_vecino(credentials, db)
    
    service = ReservaService(db)
    
    try:
        return await service.consultar_disponibilidad(
            id_espacio=disponibilidad_data.id_espacio,
            fecha=disponibilidad_data.fecha
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


# Endpoint adicional para listar espacios disponibles
@router.get(
    "/espacios/disponibles",
    summary="Listar espacios disponibles",
    description="Obtener lista de espacios disponibles para reservar."
)
async def listar_espacios_disponibles(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db_session)
):
    """Listar espacios disponibles para reservar."""
    
    # Obtener vecino actual para verificar su junta
    current_vecino = await get_current_vecino(credentials, db)
    
    from src.database.models import Espacio
    from sqlalchemy import select
    
    try:
        # Obtener espacios activos de la junta del vecino
        query = select(Espacio).where(
            Espacio.id_junta == current_vecino.id_junta,
            Espacio.activo == True
        ).order_by(Espacio.nombre)
        
        result = await db.execute(query)
        espacios = result.scalars().all()
        
        from src.schemas.reserva_schemas import EspacioResponse
        
        return [
            EspacioResponse(
                id_espacio=espacio.id_espacio,
                id_junta=espacio.id_junta,
                nombre=espacio.nombre,
                tipo=espacio.tipo,
                capacidad=espacio.capacidad,
                activo=espacio.activo
            )
            for espacio in espacios
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )