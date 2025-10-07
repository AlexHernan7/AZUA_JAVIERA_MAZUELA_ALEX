"""
Servicio para manejo de reservas de espacios comunitarios.

Maneja la creación, actualización y consulta de reservas con validación de solapamiento.
"""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from typing import Optional, List, Dict, Any
from datetime import datetime, date, time, timedelta
from decimal import Decimal

from src.database.models.reserva import Reserva
from src.database.models.espacio import Espacio
from src.database.models.vecino import Vecino
from src.database.models.junta import Junta
from src.database.models.estado_reserva import EstadoReserva
from src.schemas.reserva_schemas import (
    ReservaCreateRequest,
    ReservaUpdateRequest,
    ReservaResponse,
    ReservaListResponse,
    DisponibilidadRequest,
    DisponibilidadResponse,
    ReservaConPagoRequest
)
from src.schemas.payment_schemas import PaymentIntentResponse
from src.services.payment_service import PaymentService

logger = logging.getLogger(__name__)


class ReservaService:
    """
    Servicio para manejar reservas de espacios comunitarios.
    """

    def __init__(self, db: AsyncSession):
        """Inicializa el servicio con la sesión de base de datos."""
        self.db = db
        self.payment_service = PaymentService(db)

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

            # 5. Validar duración máxima de reserva y calcular valor
            from datetime import timezone
            inicio_dt = datetime.combine(reserva_data.fecha, time.fromisoformat(reserva_data.hora_inicio), timezone.utc)
            fin_dt = datetime.combine(reserva_data.fecha, time.fromisoformat(reserva_data.hora_termino), timezone.utc)
            duracion_horas = (fin_dt - inicio_dt).total_seconds() / 3600
            
            if duracion_horas > espacio.max_horas:
                raise ValueError(f"La duración máxima permitida es {espacio.max_horas} horas")
            
            # Calcular valor total de la reserva
            valor_total = Decimal(str(duracion_horas)) * espacio.valor

            # 6. Verificar disponibilidad (validación de solapamiento)
            disponible = await self._verificar_disponibilidad(
                reserva_data.id_espacio,
                inicio_dt,
                fin_dt
            )
            
            if not disponible:
                raise ValueError("El horario seleccionado no está disponible. Ya existe una reserva en ese período.")

            # 7. Obtener ID del estado "pendiente"
            estado_pendiente = await self._get_estado_by_nombre("pendiente")
            if not estado_pendiente:
                raise ValueError("No se encontró el estado 'pendiente' en la base de datos")

            # 8. Crear la reserva
            nueva_reserva = Reserva(
                id_junta=reserva_data.id_junta,
                id_espacio=reserva_data.id_espacio,
                id_vecino=reserva_data.id_vecino,
                creado_por=user_id,
                id_estado=estado_pendiente.id_estado,
                inicio=inicio_dt,
                fin=fin_dt,
                observaciones=reserva_data.observaciones,
                valor_reserva=valor_total
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
                    id_estado=estado_pendiente.id_estado,
                    inicio=nueva_reserva.inicio,
                    fin=nueva_reserva.fin,
                    estado=estado_pendiente.nombre_estado,
                    observaciones=nueva_reserva.observaciones,
                    created_at=nueva_reserva.created_at,
                    valor_reserva=nueva_reserva.valor_reserva,
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
            # Convertir a datetime con zona horaria UTC
            from datetime import timezone
            inicio_dt = datetime.combine(disponibilidad_data.fecha, time.fromisoformat(disponibilidad_data.hora_inicio), timezone.utc)
            fin_dt = datetime.combine(disponibilidad_data.fecha, time.fromisoformat(disponibilidad_data.hora_termino), timezone.utc)
            
            logger.info(f"🕐 Verificando disponibilidad:")
            logger.info(f"   - Espacio ID: {disponibilidad_data.id_espacio}")
            logger.info(f"   - Fecha: {disponibilidad_data.fecha}")
            logger.info(f"   - Hora inicio: {disponibilidad_data.hora_inicio} -> {inicio_dt}")
            logger.info(f"   - Hora fin: {disponibilidad_data.hora_termino} -> {fin_dt}")

            # Validar que no sea fecha pasada
            hoy = datetime.now().date()
            if disponibilidad_data.fecha < hoy:
                return DisponibilidadResponse(
                    disponible=False,
                    mensaje="No se pueden hacer reservas para fechas pasadas"
                )

            # Validación de horarios pasados deshabilitada - permitir reservas en cualquier momento
            # (Comentado para permitir reservas sin restricciones de tiempo)
            # from datetime import timezone
            # ahora = datetime.now(timezone.utc)
            # if disponibilidad_data.fecha == hoy:
            #     hora_actual = ahora.time()
            #     hora_inicio = time.fromisoformat(disponibilidad_data.hora_inicio)
            #     if hora_inicio <= hora_actual:
            #         return DisponibilidadResponse(
            #             disponible=False,
            #             mensaje="No se pueden hacer reservas para horarios pasados"
            #         )

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

            logger.info(f"🎯 Resultado de disponibilidad: {disponible}")

            if disponible:
                logger.info("✅ Horario disponible")
                return DisponibilidadResponse(
                    disponible=True,
                    mensaje="El horario seleccionado está disponible"
                )
            else:
                logger.info("❌ Horario no disponible, obteniendo detalles de conflicto")
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
            logger.error(f"Tipo de error: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback completo: {traceback.format_exc()}")
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

    async def _get_estado_by_nombre(self, nombre_estado: str) -> Optional[EstadoReserva]:
        """
        Obtiene un estado de reserva por su nombre.
        
        Args:
            nombre_estado: Nombre del estado a buscar
            
        Returns:
            EstadoReserva o None si no se encuentra
        """
        try:
            query = select(EstadoReserva).where(EstadoReserva.nombre_estado == nombre_estado)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error al obtener estado '{nombre_estado}': {e}")
            return None

    async def _get_estados_activos_ids(self) -> List[int]:
        """
        Obtiene los IDs de los estados de reserva que se consideran activos.
        
        Returns:
            Lista de IDs de estados activos
        """
        try:
            # Primero, obtener todos los estados para debug
            query_all = select(EstadoReserva)
            result_all = await self.db.execute(query_all)
            all_estados = result_all.scalars().all()
            
            logger.info(f"🔍 Todos los estados en la BD: {len(all_estados)}")
            for estado in all_estados:
                logger.info(f"   - ID: {estado.id_estado}, Nombre: {estado.nombre_estado}, Activo: {estado.activo}")
            
            # Buscar estados activos
            query = select(EstadoReserva.id_estado).where(
                and_(
                    EstadoReserva.activo == True,
                    EstadoReserva.nombre_estado.in_(['pendiente', 'pagada', 'aprobada', 'confirmada'])
                )
            )
            result = await self.db.execute(query)
            estados_ids = [row[0] for row in result.fetchall()]
            
            logger.info(f"✅ Estados activos encontrados: {estados_ids}")
            
            if not estados_ids:
                logger.warning("⚠️ No se encontraron estados activos, usando fallback")
                return [1, 2, 3, 4]  # IDs por defecto
            
            return estados_ids
        except Exception as e:
            logger.error(f"Error al obtener estados activos: {e}")
            # Fallback a estados por defecto si hay error
            return [1, 2, 3, 4]  # IDs por defecto

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
            
            logger.info(f"🔍 Buscando reservas en conflicto para espacio {id_espacio}")
            logger.info(f"   - Rango: {inicio} a {fin}")
            
            # Obtener IDs de estados activos
            estados_activos_ids = await self._get_estados_activos_ids()
            logger.info(f"📊 Estados activos IDs: {estados_activos_ids}")
            
            # Primero, mostrar todas las reservas del espacio para esa fecha
            query_todas = select(Reserva).options(
                selectinload(Reserva.estado)
            ).where(
                and_(
                    Reserva.id_espacio == id_espacio,
                    Reserva.id_estado.in_(estados_activos_ids),
                    func.date(Reserva.inicio) == inicio.date()
                )
            )
            result_todas = await self.db.execute(query_todas)
            todas_reservas = result_todas.scalars().all()
            
            logger.info(f"📅 Todas las reservas del día {inicio.date()}: {len(todas_reservas)}")
            for reserva in todas_reservas:
                estado_nombre = reserva.estado.nombre_estado if reserva.estado else f"ID:{reserva.id_estado}"
                logger.info(f"   - Reserva {reserva.id_reserva}: {reserva.inicio} a {reserva.fin} (estado: {estado_nombre})")
            
            # Lógica de solapamiento mejorada:
            # Dos intervalos se solapan si:
            # - El inicio de uno es menor que el fin del otro Y
            # - El fin de uno es mayor que el inicio del otro
            # Pero excluimos solapamientos en los bordes (inicio = fin)
            query = select(Reserva).options(
                selectinload(Reserva.estado)
            ).where(
                and_(
                    Reserva.id_espacio == id_espacio,
                    Reserva.id_estado.in_(estados_activos_ids),
                    Reserva.inicio < fin,    # La reserva existente empieza antes de que termine la nueva
                    Reserva.fin > inicio     # La reserva existente termina después de que empiece la nueva
                )
            )
            
            result = await self.db.execute(query)
            reservas_conflicto = result.scalars().all()
            
            logger.info(f"📋 Reservas en conflicto encontradas: {len(reservas_conflicto)}")
            for reserva in reservas_conflicto:
                estado_nombre = reserva.estado.nombre_estado if reserva.estado else f"ID:{reserva.id_estado}"
                logger.info(f"   - Reserva {reserva.id_reserva}: {reserva.inicio} a {reserva.fin} (estado: {estado_nombre})")
                
                # Verificar si realmente hay solapamiento
                solapamiento_real = (
                    reserva.inicio < fin and 
                    reserva.fin > inicio
                )
                logger.info(f"     🔍 Solapamiento real: {solapamiento_real}")
                logger.info(f"     📅 Reserva inicio < fin solicitado: {reserva.inicio} < {fin} = {reserva.inicio < fin}")
                logger.info(f"     📅 Reserva fin > inicio solicitado: {reserva.fin} > {inicio} = {reserva.fin > inicio}")
            
            # Si hay reservas que se solapan, no está disponible
            disponible = len(reservas_conflicto) == 0
            logger.info(f"✅ Disponible: {disponible}")
            return disponible
            
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
            # Obtener IDs de estados activos
            estados_activos_ids = await self._get_estados_activos_ids()
            
            query = select(Reserva).options(
                selectinload(Reserva.estado)
            ).where(
                and_(
                    Reserva.id_espacio == id_espacio,
                    Reserva.id_estado.in_(estados_activos_ids),
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
                    "estado": reserva.estado.nombre_estado if reserva.estado else None
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
                selectinload(Reserva.espacio).selectinload(Espacio.tipo_espacio),
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
                id_estado=reserva.id_estado,
                inicio=reserva.inicio,
                fin=reserva.fin,
                estado=reserva.estado.nombre_estado if reserva.estado else None,
                observaciones=reserva.observaciones,
                created_at=reserva.created_at,
                valor_reserva=reserva.valor_reserva,
                espacio_nombre=reserva.espacio.nombre if reserva.espacio else None,
                espacio_tipo=reserva.espacio.tipo_espacio.tipo if reserva.espacio and reserva.espacio.tipo_espacio else None,
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

    async def crear_reserva_con_pago(
        self, 
        reserva_data: ReservaConPagoRequest,
        user_id: int
    ) -> tuple[ReservaResponse, PaymentIntentResponse]:
        """
        Crea una reserva pendiente de pago y genera la intención de pago.
        
        Args:
            reserva_data: Datos de la reserva a crear
            user_id: ID del usuario que crea la reserva
            
        Returns:
            Tupla (ReservaResponse, PaymentIntentResponse)
            
        Raises:
            ValueError: Si hay errores en la creación
        """
        try:
            # 1. Obtener datos del vecino para la descripción
            result = await self.db.execute(
                select(Vecino).where(Vecino.id_usuario == user_id)
            )
            vecino = result.scalar_one_or_none()
            if not vecino:
                raise ValueError("No se encontró perfil de vecino asociado")
            
            # 2. Crear reserva (estado: pendiente)
            reserva = await self.create_reserva(reserva_data, user_id)
            
            # 3. Crear intención de pago
            payment_intent = await self.payment_service.create_payment_intent(
                user_id=user_id,
                entity_type="reserva",
                entity_id=reserva.id_reserva,
                amount=reserva.valor_reserva,
                description=f"Reserva de espacio - {reserva.espacio_nombre}",
                extra_data={
                    "reserva_id": reserva.id_reserva,
                    "espacio_nombre": reserva.espacio_nombre,
                    "fecha": reserva.inicio.strftime("%Y-%m-%d"),
                    "hora_inicio": reserva.inicio.strftime("%H:%M"),
                    "hora_termino": reserva.fin.strftime("%H:%M"),
                    "vecino_rut": vecino.rut
                }
            )
            
            logger.info(f"🏟️💳 Reserva con pago creada: reserva={reserva.id_reserva}, payment={payment_intent.id_payment_intent}")
            
            return reserva, payment_intent
            
        except Exception as e:
            logger.error(f"💥 Error creando reserva con pago: {str(e)}")
            raise ValueError(f"Error creando reserva con pago: {str(e)}")

    async def crear_reserva_con_webpay(
        self, 
        reserva_data: ReservaConPagoRequest,
        user_id: int
    ) -> tuple[ReservaResponse, PaymentIntentResponse, str, str]:
        """
        Crea una reserva pendiente de pago y genera la intención de pago con Webpay.
        
        Args:
            reserva_data: Datos de la reserva a crear
            user_id: ID del usuario que crea la reserva
            
        Returns:
            Tupla (ReservaResponse, PaymentIntentResponse, webpay_url, webpay_token)
            
        Raises:
            ValueError: Si hay errores en la creación
        """
        try:
            # 1. Obtener datos del vecino para la descripción
            result = await self.db.execute(
                select(Vecino).where(Vecino.id_usuario == user_id)
            )
            vecino = result.scalar_one_or_none()
            if not vecino:
                raise ValueError("No se encontró perfil de vecino asociado")
            
            # 2. Crear reserva (estado: pendiente_pago)
            reserva = await self.create_reserva(reserva_data, user_id)
            
            # 3. Crear intención de pago con Webpay
            logger.info(f"💰 Valor de reserva: {reserva.valor_reserva} (tipo: {type(reserva.valor_reserva)})")
            
            # Verificar que el valor sea mayor a 0
            if reserva.valor_reserva <= 0:
                raise ValueError(f"El valor de la reserva debe ser mayor a 0. Valor actual: {reserva.valor_reserva}")
            
            # Usar monto real de la reserva
            monto_webpay = reserva.valor_reserva
            logger.info(f"💰 Usando monto real de reserva: {monto_webpay}")
            
            payment_intent, webpay_url, webpay_token = await self.payment_service.create_webpay_payment_intent(
                user_id=user_id,
                entity_type="reserva",  # Usar entity_type correcto
                entity_id=reserva.id_reserva,
                amount=monto_webpay,  # Usar monto real
                description=f"Reserva {reserva.espacio_nombre}",  # Descripción correcta del espacio
                extra_data={
                    "reserva_id": reserva.id_reserva,
                    "espacio_nombre": reserva.espacio_nombre,
                    "fecha": reserva.inicio.strftime("%Y-%m-%d"),
                    "hora_inicio": reserva.inicio.strftime("%H:%M"),
                    "hora_termino": reserva.fin.strftime("%H:%M"),
                    "vecino_rut": vecino.rut
                }
            )
            
            logger.info(f"🏟️💳 Reserva con Webpay creada: reserva={reserva.id_reserva}, payment={payment_intent.id_payment_intent}")
            
            return reserva, payment_intent, webpay_url, webpay_token
            
        except Exception as e:
            logger.error(f"💥 Error creando reserva con Webpay: {str(e)}")
            raise ValueError(f"Error creando reserva con Webpay: {str(e)}")