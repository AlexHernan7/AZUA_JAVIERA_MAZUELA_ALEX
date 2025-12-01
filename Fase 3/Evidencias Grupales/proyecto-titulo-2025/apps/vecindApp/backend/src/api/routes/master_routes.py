"""
Rutas para tablas maestras.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.database.session import get_db_session
from src.schemas.master_schemas import (
    EstadoCertificadoResponse,
    MotivoSolicitudResponse,
    TipoEspacioResponse,
    EstadoReservaResponse,
    MotivosAgrupadosResponse
)
from src.services.master_service import MasterService

router = APIRouter(prefix="/master", tags=["Master Data"])


@router.get("/estados-certificado", response_model=List[EstadoCertificadoResponse])
async def get_estados_certificado(
    activo: bool = True,
    db: AsyncSession = Depends(get_db_session)
):
    """Obtiene todos los estados de certificado."""
    try:
        service = MasterService(db)
        estados = await service.get_estados_certificado(activo=activo)
        return estados
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estados de certificado: {str(e)}")


@router.get("/motivos-solicitud", response_model=List[MotivoSolicitudResponse])
async def get_motivos_solicitud(
    activo: bool = True,
    db: AsyncSession = Depends(get_db_session)
):
    """Obtiene todos los motivos de solicitud."""
    try:
        service = MasterService(db)
        motivos = await service.get_motivos_solicitud(activo=activo)
        return motivos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener motivos de solicitud: {str(e)}")


@router.get("/motivos-solicitud-agrupados", response_model=MotivosAgrupadosResponse)
async def get_motivos_solicitud_agrupados(
    activo: bool = True,
    db: AsyncSession = Depends(get_db_session)
):
    """Obtiene motivos de solicitud agrupados por categoría."""
    try:
        service = MasterService(db)
        motivos_agrupados = await service.get_motivos_solicitud_agrupados(activo=activo)
        return motivos_agrupados
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener motivos agrupados: {str(e)}")


@router.get("/tipos-espacio", response_model=List[TipoEspacioResponse])
async def get_tipos_espacio(
    activo: bool = True,
    db: AsyncSession = Depends(get_db_session)
):
    """Obtiene todos los tipos de espacio."""
    try:
        service = MasterService(db)
        tipos = await service.get_tipos_espacio(activo=activo)
        return tipos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener tipos de espacio: {str(e)}")


@router.get("/estados-reserva", response_model=List[EstadoReservaResponse])
async def get_estados_reserva(
    activo: bool = True,
    db: AsyncSession = Depends(get_db_session)
):
    """Obtiene todos los estados de reserva."""
    try:
        service = MasterService(db)
        estados = await service.get_estados_reserva(activo=activo)
        return estados
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estados de reserva: {str(e)}")
