"""
Servicio para manejo de reservas de espacios comunitarios.

Maneja la creación, actualización y consulta de reservas con validación de solapamiento.
"""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from typing import Optional, List, Dict, Any
from datetime import datetime, date, time, timedelta
from decimal import Decimal

from src.database.models.reserva import Reserva
from src.database.models.espacio import Espacio
from src.database.models.vecino import Vecino
from src.database.models.junta import Junta
from src.schemas.reserva_schemas import (
    ReservaCreateRequest,
    ReservaUpdateRequest,
    ReservaResponse,
    ReservaListResponse,
    DisponibilidadRequest,
    DisponibilidadResponse
)

logger = logging.getLogger(__name__)


class ReservaService:
    """
    Servicio para manejar reservas de espacios comunitarios.
    """

    def __init__(self, db: AsyncSession):
        """Inicializa el servicio con la sesión de base de datos."""
        self.db = db

    async def create_reserva(
        self, 
        reserva_data: ReservaCreateRequest,
        user_id: int
    ) -> ReservaResponse:
        """
        Crea una nueva reserva de espacio con validación de solapamiento.
        
        Args:
            reserva_data: Datos de la reserva a crear
            user_id: ID del usuario que crea la reserva
            
        Returns:
            ReservaResponse: Datos de la reserva creada
            
        Raises:
            ValueError: Si hay conflictos de disponibilidad o datos inválidos
            IntegrityError: Si hay conflicto de datos
        """
        try:
            # 1. Verificar que el espacio existe y está activo
            espacio = await self._get_espacio_by_id(reserva_data.id_espacio)
            if not espacio:
                raise ValueError(f"Espacio con ID {reserva_data.id_espacio} no encontrado")
            
            if not espacio.activo:
                raise ValueError("El espacio no está disponible para reservas")

            # 2. Verificar que la junta existe
            junta = await self._get_junta_by_id(reserva_data.id_junta)
            if not junta:
                raise ValueError(f"Junta con ID {reserva_data.id_junta} no encontrada")

            # 3. Verificar que el vecino existe
            vecino = await self._get_vecino_by_id(reserva_data.id_vecino)
            if not vecino:
                raise ValueError(f"Vecino con ID {reserva_data.id_vecino} no encontrado")

            # 4. Validar que el espacio pertenece a la junta
            if espacio.id_junta != reserva_data.id_junta:
                raise ValueError("El espacio no pertenece a la junta especificada")

            # 5. Validar duración máxima de reserva
            inicio_dt = datetime.combine(reserva_data.fecha, time.fromisoformat(reserva_data.hora_inicio))
            fin_dt = datetime.combine(reserva_data.fecha, time.fromisoformat(reserva_data.hora_termino))
            duracion_horas = (fin_dt - inicio_dt).total_seconds() / 3600
            
            if duracion_horas > espacio.max_horas:
                raise ValueError(f"La duración máxima permitida es {espacio.max_horas} horas")

            # 6. Verificar disponibilidad (validación de solapamiento)
            disponible = await self._verificar_disponibilidad(
                reserva_data.id_espacio,
                inicio_dt,
                fin_dt
            )
            
            if not disponible:
                raise ValueError("El horario seleccionado no está disponible. Ya existe una reserva en ese período.")

            # 7. Crear la reserva
            nueva_reserva = Reserva(
                id_junta=reserva_data.id_junta,
                id_espacio=reserva_data.id_espacio,
                id_vecino=reserva_data.id_vecino,
                creado_por=user_id,
                inicio=inicio_dt,
                fin=fin_dt,
                estado="pendiente",
                observaciones=reserva_data.observaciones
            )

            self.db.add(nueva_reserva)
            await self.db.commit()
            await self.db.refresh(nueva_reserva)

            logger.info(f"Reserva creada exitosamente con ID {nueva_reserva.id_reserva}")

            # 8. Obtener la reserva con información adicional
            reserva_completa = await self._get_reserva_with_details(nueva_reserva.id_reserva)
            if not reserva_completa:
                # Si no se puede obtener con detalles, crear una respuesta básica
                logger.warning(f"No se pudo obtener detalles completos de la reserva {nueva_reserva.id_reserva}")
                return ReservaResponse(
                    id_reserva=nueva_reserva.id_reserva,
                    id_junta=nueva_reserva.id_junta,
                    id_espacio=nueva_reserva.id_espacio,
                    id_vecino=nueva_reserva.id_vecino,
                    creado_por=nueva_reserva.creado_por,
                    inicio=nueva_reserva.inicio,
                    fin=nueva_reserva.fin,
                    estado=nueva_reserva.estado,
                    observaciones=nueva_reserva.observaciones,
                    created_at=nueva_reserva.created_at,
                    espacio_nombre=None,
                    espacio_tipo=None,
                    espacio_capacidad=None,
                    espacio_valor=None,
                    vecino_nombre=None,
                    vecino_email=None
                )
            return reserva_completa

        except IntegrityError as e:
            await self.db.rollback()
            logger.error(f"Error de integridad al crear reserva: {e}")
            raise ValueError("Error al crear la reserva. Verifique que los datos sean válidos.")
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error inesperado al crear reserva: {e}")
            raise

    async def verificar_disponibilidad(
        self, 
        disponibilidad_data: DisponibilidadRequest
    ) -> DisponibilidadResponse:
        """
        Verifica la disponibilidad de un espacio en un horario específico.
        
        Args:
            disponibilidad_data: Datos para verificar disponibilidad
            
        Returns:
            DisponibilidadResponse: Resultado de la verificación
        """
        try:
            # Convertir a datetime
            inicio_dt = datetime.combine(disponibilidad_data.fecha, time.fromisoformat(disponibilidad_data.hora_inicio))
            fin_dt = datetime.combine(disponibilidad_data.fecha, time.fromisoformat(disponibilidad_data.hora_termino))

            # Verificar que el espacio existe
            espacio = await self._get_espacio_by_id(disponibilidad_data.id_espacio)
            if not espacio:
                return DisponibilidadResponse(
                    disponible=False,
                    mensaje="Espacio no encontrado"
                )

            if not espacio.activo:
                return DisponibilidadResponse(
                    disponible=False,
                    mensaje="El espacio no está disponible para reservas"
                )

            # Verificar disponibilidad
            disponible = await self._verificar_disponibilidad(
                disponibilidad_data.id_espacio,
                inicio_dt,
                fin_dt
            )

            if disponible:
                return DisponibilidadResponse(
                    disponible=True,
                    mensaje="El horario seleccionado está disponible"
                )
            else:
                # Obtener reservas que causan conflicto
                reservas_conflicto = await self._get_reservas_conflicto(
                    disponibilidad_data.id_espacio,
                    inicio_dt,
                    fin_dt
                )
                
                return DisponibilidadResponse(
                    disponible=False,
                    mensaje="El horario seleccionado NO está disponible",
                    reservas_conflicto=reservas_conflicto
                )

        except Exception as e:
            logger.error(f"Error al verificar disponibilidad: {e}")
            return DisponibilidadResponse(
                disponible=False,
                mensaje="Error al verificar disponibilidad"
            )

    async def get_reserva_by_id(self, reserva_id: int) -> Optional[ReservaResponse]:
        """
        Obtiene una reserva por su ID con información adicional.
        
        Args:
            reserva_id: ID de la reserva
            
        Returns:
            ReservaResponse o None si no existe
        """
        try:
            return await self._get_reserva_with_details(reserva_id)
        except Exception as e:
            logger.error(f"Error al obtener reserva {reserva_id}: {e}")
            return None

    async def get_reservas_by_espacio(
        self,
        id_espacio: int,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        pagina: int = 1,
        por_pagina: int = 10
    ) -> ReservaListResponse:
        """
        Obtiene reservas de un espacio específico.
        
        Args:
            id_espacio: ID del espacio
            fecha_desde: Fecha desde (opcional)
            fecha_hasta: Fecha hasta (opcional)
            pagina: Número de página
            por_pagina: Elementos por página
            
        Returns:
            Lista paginada de reservas
        """
        try:
            # Construir query base
            query = select(Reserva).where(Reserva.id_espacio == id_espacio)
            
            # Aplicar filtros de fecha si se proporcionan
            if fecha_desde:
                query = query.where(Reserva.inicio >= datetime.combine(fecha_desde, time.min))
            if fecha_hasta:
                query = query.where(Reserva.inicio <= datetime.combine(fecha_hasta, time.max))
            
            # Ordenar por fecha de inicio
            query = query.order_by(Reserva.inicio)
            
            # Aplicar paginación
            offset = (pagina - 1) * por_pagina
            query = query.offset(offset).limit(por_pagina)
            
            # Ejecutar query
            result = await self.db.execute(query)
            reservas = result.scalars().all()
            
            # Obtener total para paginación
            count_query = select(Reserva).where(Reserva.id_espacio == id_espacio)
            if fecha_desde:
                count_query = count_query.where(Reserva.inicio >= datetime.combine(fecha_desde, time.min))
            if fecha_hasta:
                count_query = count_query.where(Reserva.inicio <= datetime.combine(fecha_hasta, time.max))
            
            total_result = await self.db.execute(count_query)
            total = len(total_result.scalars().all())
            
            # Convertir a response
            reservas_response = []
            for reserva in reservas:
                reserva_completa = await self._get_reserva_with_details(reserva.id_reserva)
                if reserva_completa:
                    reservas_response.append(reserva_completa)
            
            return ReservaListResponse(
                reservas=reservas_response,
                total=total,
                pagina=pagina,
                por_pagina=por_pagina
            )
            
        except Exception as e:
            logger.error(f"Error al obtener reservas del espacio {id_espacio}: {e}")
            raise

    async def _verificar_disponibilidad(
        self,
        id_espacio: int,
        inicio: datetime,
        fin: datetime
    ) -> bool:
        """
        Verifica si un espacio está disponible en un rango de tiempo específico.
        
        Args:
            id_espacio: ID del espacio
            inicio: Fecha y hora de inicio
            fin: Fecha y hora de fin
            
        Returns:
            True si está disponible, False si hay solapamiento
        """
        try:
            # Buscar reservas que se solapen con el rango de tiempo
            # Un solapamiento ocurre cuando:
            # - La reserva existente empieza antes de que termine la nueva Y
            # - La reserva existente termina después de que empiece la nueva
            
            query = select(Reserva).where(
                and_(
                    Reserva.id_espacio == id_espacio,
                    Reserva.estado.in_(['pendiente', 'pagada', 'aprobada', 'confirmada']),
                    Reserva.inicio < fin,  # La reserva existente empieza antes de que termine la nueva
                    Reserva.fin > inicio   # La reserva existente termina después de que empiece la nueva
                )
            )
            
            result = await self.db.execute(query)
            reservas_conflicto = result.scalars().all()
            
            # Si hay reservas que se solapan, no está disponible
            return len(reservas_conflicto) == 0
            
        except Exception as e:
            logger.error(f"Error al verificar disponibilidad: {e}")
            return False

    async def _get_reservas_conflicto(
        self,
        id_espacio: int,
        inicio: datetime,
        fin: datetime
    ) -> List[Dict[str, Any]]:
        """
        Obtiene las reservas que causan conflicto con un rango de tiempo.
        
        Args:
            id_espacio: ID del espacio
            inicio: Fecha y hora de inicio
            fin: Fecha y hora de fin
            
        Returns:
            Lista de diccionarios con información de las reservas en conflicto
        """
        try:
            query = select(Reserva).where(
                and_(
                    Reserva.id_espacio == id_espacio,
                    Reserva.estado.in_(['pendiente', 'pagada', 'aprobada', 'confirmada']),
                    Reserva.inicio < fin,
                    Reserva.fin > inicio
                )
            )
            
            result = await self.db.execute(query)
            reservas = result.scalars().all()
            
            reservas_conflicto = []
            for reserva in reservas:
                reservas_conflicto.append({
                    "id_reserva": reserva.id_reserva,
                    "inicio": reserva.inicio.isoformat(),
                    "fin": reserva.fin.isoformat(),
                    "estado": reserva.estado
                })
            
            return reservas_conflicto
            
        except Exception as e:
            logger.error(f"Error al obtener reservas en conflicto: {e}")
            return []

    async def _get_reserva_with_details(self, reserva_id: int) -> Optional[ReservaResponse]:
        """
        Obtiene una reserva con información adicional del espacio y vecino.
        
        Args:
            reserva_id: ID de la reserva
            
        Returns:
            ReservaResponse con información completa
        """
        try:
            query = select(Reserva).options(
                selectinload(Reserva.espacio),
                selectinload(Reserva.vecino)
            ).where(Reserva.id_reserva == reserva_id)
            
            result = await self.db.execute(query)
            reserva = result.scalar_one_or_none()
            
            if not reserva:
                return None
            
            # Construir respuesta con información adicional
            return ReservaResponse(
                id_reserva=reserva.id_reserva,
                id_junta=reserva.id_junta,
                id_espacio=reserva.id_espacio,
                id_vecino=reserva.id_vecino,
                creado_por=reserva.creado_por,
                inicio=reserva.inicio,
                fin=reserva.fin,
                estado=reserva.estado,
                observaciones=reserva.observaciones,
                created_at=reserva.created_at,
                espacio_nombre=reserva.espacio.nombre if reserva.espacio else None,
                espacio_tipo=reserva.espacio.tipo if reserva.espacio else None,
                espacio_capacidad=reserva.espacio.capacidad if reserva.espacio else None,
                espacio_valor=reserva.espacio.valor if reserva.espacio else None,
                vecino_nombre=f"{reserva.vecino.nombres} {reserva.vecino.apellido_paterno} {reserva.vecino.apellido_materno or ''}".strip() if reserva.vecino else None,
                vecino_email=reserva.vecino.email if reserva.vecino else None
            )
            
        except Exception as e:
            logger.error(f"Error al obtener reserva con detalles {reserva_id}: {e}")
            return None

    async def _get_espacio_by_id(self, espacio_id: int) -> Optional[Espacio]:
        """Obtiene un espacio por su ID."""
        try:
            query = select(Espacio).where(Espacio.id_espacio == espacio_id)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error al obtener espacio {espacio_id}: {e}")
            return None

    async def _get_junta_by_id(self, junta_id: int) -> Optional[Junta]:
        """Obtiene una junta por su ID."""
        try:
            query = select(Junta).where(Junta.id_junta == junta_id)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error al obtener junta {junta_id}: {e}")
            return None

    async def _get_vecino_by_id(self, vecino_id: int) -> Optional[Vecino]:
        """Obtiene un vecino por su ID."""
        try:
            query = select(Vecino).where(Vecino.id_vecino == vecino_id)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error al obtener vecino {vecino_id}: {e}")
            return None
