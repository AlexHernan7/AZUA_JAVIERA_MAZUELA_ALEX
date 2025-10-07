"""
Servicio para tablas maestras.
"""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any
from collections import defaultdict

from src.database.models.estado_certificado import EstadoCertificado
from src.database.models.motivo_solicitud import MotivoSolicitud
from src.database.models.tipo_espacio import TipoEspacio
from src.database.models.estado_reserva import EstadoReserva
from src.schemas.master_schemas import (
    EstadoCertificadoResponse,
    MotivoSolicitudResponse,
    TipoEspacioResponse,
    EstadoReservaResponse,
    MotivosAgrupadosResponse,
    MotivoGrupoResponse
)

logger = logging.getLogger(__name__)


class MasterService:
    """Servicio para manejo de tablas maestras."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_estados_certificado(self, activo: bool = True) -> List[EstadoCertificadoResponse]:
        """Obtiene todos los estados de certificado."""
        try:
            query = select(EstadoCertificado)
            if activo:
                query = query.where(EstadoCertificado.activo == True)
            query = query.order_by(EstadoCertificado.id_estado)
            
            result = await self.db.execute(query)
            estados = result.scalars().all()
            
            return [EstadoCertificadoResponse.model_validate(estado) for estado in estados]
        except Exception as e:
            logger.error(f"Error al obtener estados de certificado: {e}")
            raise

    async def get_motivos_solicitud(self, activo: bool = True) -> List[MotivoSolicitudResponse]:
        """Obtiene todos los motivos de solicitud."""
        try:
            query = select(MotivoSolicitud)
            if activo:
                query = query.where(MotivoSolicitud.activo == True)
            query = query.order_by(MotivoSolicitud.grupo, MotivoSolicitud.motivo)
            
            result = await self.db.execute(query)
            motivos = result.scalars().all()
            
            return [MotivoSolicitudResponse.model_validate(motivo) for motivo in motivos]
        except Exception as e:
            logger.error(f"Error al obtener motivos de solicitud: {e}")
            raise

    async def get_motivos_solicitud_agrupados(self, activo: bool = True) -> MotivosAgrupadosResponse:
        """Obtiene motivos de solicitud agrupados por categoría."""
        try:
            motivos = await self.get_motivos_solicitud(activo=activo)
            
            # Agrupar por grupo
            grupos_dict = defaultdict(list)
            for motivo in motivos:
                grupos_dict[motivo.grupo].append(motivo)
            
            # Crear respuesta agrupada
            grupos = []
            total = 0
            for grupo_nombre, motivos_grupo in grupos_dict.items():
                grupos.append(MotivoGrupoResponse(
                    grupo=grupo_nombre,
                    items=motivos_grupo
                ))
                total += len(motivos_grupo)
            
            return MotivosAgrupadosResponse(
                grupos=grupos,
                total=total
            )
        except Exception as e:
            logger.error(f"Error al obtener motivos agrupados: {e}")
            raise

    async def get_tipos_espacio(self, activo: bool = True) -> List[TipoEspacioResponse]:
        """Obtiene todos los tipos de espacio."""
        try:
            query = select(TipoEspacio)
            if activo:
                query = query.where(TipoEspacio.activo == True)
            query = query.order_by(TipoEspacio.tipo)
            
            result = await self.db.execute(query)
            tipos = result.scalars().all()
            
            return [TipoEspacioResponse.model_validate(tipo) for tipo in tipos]
        except Exception as e:
            logger.error(f"Error al obtener tipos de espacio: {e}")
            raise

    async def get_estados_reserva(self, activo: bool = True) -> List[EstadoReservaResponse]:
        """Obtiene todos los estados de reserva."""
        try:
            query = select(EstadoReserva)
            if activo:
                query = query.where(EstadoReserva.activo == True)
            query = query.order_by(EstadoReserva.id_estado)
            
            result = await self.db.execute(query)
            estados = result.scalars().all()
            
            return [EstadoReservaResponse.model_validate(estado) for estado in estados]
        except Exception as e:
            logger.error(f"Error al obtener estados de reserva: {e}")
            raise

    async def get_estado_certificado_by_id(self, id_estado: int) -> EstadoCertificadoResponse:
        """Obtiene un estado de certificado por ID."""
        try:
            query = select(EstadoCertificado).where(EstadoCertificado.id_estado == id_estado)
            result = await self.db.execute(query)
            estado = result.scalar_one_or_none()
            
            if not estado:
                raise ValueError(f"Estado de certificado con ID {id_estado} no encontrado")
            
            return EstadoCertificadoResponse.model_validate(estado)
        except Exception as e:
            logger.error(f"Error al obtener estado de certificado {id_estado}: {e}")
            raise

    async def get_motivo_solicitud_by_id(self, id_motivo: int) -> MotivoSolicitudResponse:
        """Obtiene un motivo de solicitud por ID."""
        try:
            query = select(MotivoSolicitud).where(MotivoSolicitud.id_motivo == id_motivo)
            result = await self.db.execute(query)
            motivo = result.scalar_one_or_none()
            
            if not motivo:
                raise ValueError(f"Motivo de solicitud con ID {id_motivo} no encontrado")
            
            return MotivoSolicitudResponse.model_validate(motivo)
        except Exception as e:
            logger.error(f"Error al obtener motivo de solicitud {id_motivo}: {e}")
            raise

    async def get_tipo_espacio_by_id(self, id_tipo: int) -> TipoEspacioResponse:
        """Obtiene un tipo de espacio por ID."""
        try:
            query = select(TipoEspacio).where(TipoEspacio.id_tipo == id_tipo)
            result = await self.db.execute(query)
            tipo = result.scalar_one_or_none()
            
            if not tipo:
                raise ValueError(f"Tipo de espacio con ID {id_tipo} no encontrado")
            
            return TipoEspacioResponse.model_validate(tipo)
        except Exception as e:
            logger.error(f"Error al obtener tipo de espacio {id_tipo}: {e}")
            raise

    async def get_estado_reserva_by_id(self, id_estado: int) -> EstadoReservaResponse:
        """Obtiene un estado de reserva por ID."""
        try:
            query = select(EstadoReserva).where(EstadoReserva.id_estado == id_estado)
            result = await self.db.execute(query)
            estado = result.scalar_one_or_none()
            
            if not estado:
                raise ValueError(f"Estado de reserva con ID {id_estado} no encontrado")
            
            return EstadoReservaResponse.model_validate(estado)
        except Exception as e:
            logger.error(f"Error al obtener estado de reserva {id_estado}: {e}")
            raise
