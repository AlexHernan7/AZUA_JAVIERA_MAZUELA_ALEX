"""Servicio para gestión de reservas de espacios."""

from datetime import datetime, timedelta, time
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import and_, or_, func, select
from fastapi import HTTPException, status

from src.database.models import Reserva, Espacio, Vecino
from src.schemas.reserva_schemas import (
    ReservaCreate,
    ReservaUpdate,
    ReservaResponse,
    DisponibilidadResponse,
    EstadoReserva,
    TipoEspacio
)


class ReservaService:
    """Servicio para gestión de reservas."""
    
    # Configuración de horarios
    HORA_INICIO = 12  # 12:00 PM
    HORA_FIN = 22     # 22:00 PM (10:00 PM)
    
    # Configuración de duración por tipo de espacio
    DURACION_MAXIMA = {
        TipoEspacio.CANCHA: 3,  # 3 horas máximo para canchas
        TipoEspacio.SALA: 6,    # 6 horas máximo para salas
        TipoEspacio.PLAZA: 4,   # 4 horas máximo para plazas
        TipoEspacio.OTRO: 2,    # 2 horas máximo para otros
    }
    
    DURACION_MINIMA = {
        TipoEspacio.CANCHA: 1,  # 1 hora mínimo para canchas
        TipoEspacio.SALA: 1,    # 1 hora mínimo para salas
        TipoEspacio.PLAZA: 1,   # 1 hora mínimo para plazas
        TipoEspacio.OTRO: 1,    # 1 hora mínimo para otros
    }

    def __init__(self, db: AsyncSession):
        self.db = db

    async def crear_reserva(
        self, 
        reserva_data: ReservaCreate, 
        id_vecino: int, 
        id_usuario: int
    ) -> ReservaResponse:
        """Crear una nueva reserva."""
        
        # Verificar que el espacio existe y está activo
        query = select(Espacio).where(
            Espacio.id_espacio == reserva_data.id_espacio,
            Espacio.activo == True
        )
        result = await self.db.execute(query)
        espacio = result.scalar_one_or_none()
        
        if not espacio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Espacio no encontrado o no activo"
            )
        
        # Verificar que el vecino existe y pertenece a la misma junta
        query = select(Vecino).where(Vecino.id_vecino == id_vecino)
        result = await self.db.execute(query)
        vecino = result.scalar_one_or_none()
        
        if not vecino:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vecino no encontrado"
            )
        
        if vecino.id_junta != espacio.id_junta:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo puedes reservar espacios de tu junta vecinal"
            )
        
        # Validar duración de la reserva
        self._validar_duracion_reserva(reserva_data, espacio.tipo)
        
        # Verificar disponibilidad
        disponible = await self._verificar_disponibilidad(
            reserva_data.id_espacio, 
            reserva_data.inicio, 
            reserva_data.fin
        )
        
        if not disponible:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El espacio no está disponible en el horario solicitado"
            )
        
        # Crear la reserva
        nueva_reserva = Reserva(
            id_junta=espacio.id_junta,
            id_espacio=reserva_data.id_espacio,
            id_vecino=id_vecino,
            creado_por=id_usuario,
            inicio=reserva_data.inicio,
            fin=reserva_data.fin,
            estado=EstadoReserva.PENDIENTE,
            observaciones=reserva_data.observaciones
        )
        
        self.db.add(nueva_reserva)
        await self.db.commit()
        await self.db.refresh(nueva_reserva)
        
        return await self._convertir_a_response(nueva_reserva)

    async def obtener_reserva(self, id_reserva: int, id_vecino: int) -> ReservaResponse:
        """Obtener una reserva específica."""
        
        query = select(Reserva).options(
            selectinload(Reserva.espacio)
        ).where(
            Reserva.id_reserva == id_reserva,
            Reserva.id_vecino == id_vecino
        )
        
        result = await self.db.execute(query)
        reserva = result.scalar_one_or_none()
        
        if not reserva:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reserva no encontrada"
            )
        
        return await self._convertir_a_response(reserva)

    async def listar_reservas_vecino(
        self, 
        id_vecino: int, 
        estado: Optional[EstadoReserva] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        pagina: int = 1,
        por_pagina: int = 10
    ) -> Dict[str, Any]:
        """Listar reservas de un vecino."""
        
        query = select(Reserva).options(
            selectinload(Reserva.espacio)
        ).where(Reserva.id_vecino == id_vecino)
        
        if estado:
            query = query.where(Reserva.estado == estado)
        
        if fecha_desde:
            query = query.where(Reserva.inicio >= fecha_desde)
        
        if fecha_hasta:
            query = query.where(Reserva.fin <= fecha_hasta)
        
        # Ordenar por fecha de inicio descendente
        query = query.order_by(Reserva.inicio.desc())
        
        # Contar total
        count_query = select(func.count()).select_from(
            query.subquery()
        )
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        # Paginación
        offset = (pagina - 1) * por_pagina
        query = query.offset(offset).limit(por_pagina)
        
        result = await self.db.execute(query)
        reservas = result.scalars().all()
        
        reservas_response = []
        for reserva in reservas:
            reservas_response.append(await self._convertir_a_response(reserva))
        
        return {
            "reservas": reservas_response,
            "total": total,
            "pagina": pagina,
            "por_pagina": por_pagina
        }

    async def actualizar_reserva(
        self, 
        id_reserva: int, 
        reserva_data: ReservaUpdate, 
        id_vecino: int
    ) -> ReservaResponse:
        """Actualizar una reserva."""
        
        query = select(Reserva).where(
            Reserva.id_reserva == id_reserva,
            Reserva.id_vecino == id_vecino
        )
        result = await self.db.execute(query)
        reserva = result.scalar_one_or_none()
        
        if not reserva:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reserva no encontrada"
            )
        
        # Solo se pueden modificar reservas pendientes
        if reserva.estado not in [EstadoReserva.PENDIENTE]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se pueden modificar reservas pendientes"
            )
        
        # Actualizar campos
        if reserva_data.inicio is not None:
            reserva.inicio = reserva_data.inicio
        
        if reserva_data.fin is not None:
            reserva.fin = reserva_data.fin
        
        if reserva_data.observaciones is not None:
            reserva.observaciones = reserva_data.observaciones
        
        if reserva_data.estado is not None:
            reserva.estado = reserva_data.estado
        
        # Validar nueva duración si se cambió
        if reserva_data.inicio or reserva_data.fin:
            espacio_query = select(Espacio).where(
                Espacio.id_espacio == reserva.id_espacio
            )
            espacio_result = await self.db.execute(espacio_query)
            espacio = espacio_result.scalar_one()
            
            reserva_temp = ReservaCreate(
                id_espacio=reserva.id_espacio,
                inicio=reserva.inicio,
                fin=reserva.fin
            )
            self._validar_duracion_reserva(reserva_temp, espacio.tipo)
            
            # Verificar disponibilidad excluyendo la reserva actual
            disponible = await self._verificar_disponibilidad(
                reserva.id_espacio, 
                reserva.inicio, 
                reserva.fin,
                excluir_reserva_id=id_reserva
            )
            
            if not disponible:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="El espacio no está disponible en el nuevo horario"
                )
        
        await self.db.commit()
        await self.db.refresh(reserva)
        
        return await self._convertir_a_response(reserva)

    async def cancelar_reserva(self, id_reserva: int, id_vecino: int) -> ReservaResponse:
        """Cancelar una reserva."""
        
        query = select(Reserva).where(
            Reserva.id_reserva == id_reserva,
            Reserva.id_vecino == id_vecino
        )
        result = await self.db.execute(query)
        reserva = result.scalar_one_or_none()
        
        if not reserva:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reserva no encontrada"
            )
        
        # Verificar que se puede cancelar
        if reserva.estado in [EstadoReserva.CANCELADA, EstadoReserva.RECHAZADA]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La reserva ya está cancelada o rechazada"
            )
        
        # Verificar que no sea muy tarde para cancelar (ej: 2 horas antes)
        if reserva.inicio <= datetime.now() + timedelta(hours=2):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede cancelar una reserva con menos de 2 horas de anticipación"
            )
        
        reserva.estado = EstadoReserva.CANCELADA
        await self.db.commit()
        await self.db.refresh(reserva)
        
        return await self._convertir_a_response(reserva)

    async def consultar_disponibilidad(
        self, 
        id_espacio: int, 
        fecha: datetime
    ) -> DisponibilidadResponse:
        """Consultar disponibilidad de un espacio en una fecha específica."""
        
        # Verificar que el espacio existe
        query = select(Espacio).where(
            Espacio.id_espacio == id_espacio,
            Espacio.activo == True
        )
        result = await self.db.execute(query)
        espacio = result.scalar_one_or_none()
        
        if not espacio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Espacio no encontrado"
            )
        
        # Obtener reservas del día
        inicio_dia = fecha.replace(hour=0, minute=0, second=0, microsecond=0)
        fin_dia = inicio_dia + timedelta(days=1)
        
        query = select(Reserva).where(
            Reserva.id_espacio == id_espacio,
            Reserva.inicio >= inicio_dia,
            Reserva.inicio < fin_dia,
            Reserva.estado.in_([
                EstadoReserva.PENDIENTE,
                EstadoReserva.APROBADA,
                EstadoReserva.CONFIRMADA,
                EstadoReserva.PAGADA
            ])
        ).order_by(Reserva.inicio)
        
        result = await self.db.execute(query)
        reservas_dia = result.scalars().all()
        
        # Generar horarios disponibles y ocupados
        horarios_disponibles = []
        horarios_ocupados = []
        
        # Crear slots de 1 hora desde HORA_INICIO hasta HORA_FIN
        for hora in range(self.HORA_INICIO, self.HORA_FIN):
            inicio_slot = fecha.replace(hour=hora, minute=0, second=0, microsecond=0)
            fin_slot = inicio_slot + timedelta(hours=1)
            
            # Verificar si el slot está ocupado
            ocupado = False
            for reserva in reservas_dia:
                if (inicio_slot < reserva.fin and fin_slot > reserva.inicio):
                    ocupado = True
                    horarios_ocupados.append({
                        "inicio": reserva.inicio.strftime("%H:%M"),
                        "fin": reserva.fin.strftime("%H:%M"),
                        "id_reserva": reserva.id_reserva,
                        "estado": reserva.estado
                    })
                    break
            
            if not ocupado:
                horarios_disponibles.append({
                    "inicio": inicio_slot.strftime("%H:%M"),
                    "fin": fin_slot.strftime("%H:%M")
                })
        
        return DisponibilidadResponse(
            id_espacio=id_espacio,
            fecha=fecha,
            horarios_disponibles=horarios_disponibles,
            horarios_ocupados=horarios_ocupados
        )

    def _validar_duracion_reserva(self, reserva: ReservaCreate, tipo_espacio: str) -> None:
        """Validar que la duración de la reserva sea apropiada para el tipo de espacio."""
        
        duracion = reserva.fin - reserva.inicio
        horas = duracion.total_seconds() / 3600
        
        tipo_enum = TipoEspacio(tipo_espacio)
        
        duracion_min = self.DURACION_MINIMA.get(tipo_enum, 1)
        duracion_max = self.DURACION_MAXIMA.get(tipo_enum, 2)
        
        if horas < duracion_min:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La duración mínima para {tipo_espacio} es {duracion_min} hora(s)"
            )
        
        if horas > duracion_max:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La duración máxima para {tipo_espacio} es {duracion_max} hora(s)"
            )

    async def _verificar_disponibilidad(
        self, 
        id_espacio: int, 
        inicio: datetime, 
        fin: datetime,
        excluir_reserva_id: Optional[int] = None
    ) -> bool:
        """Verificar si un espacio está disponible en un horario específico."""
        
        query = select(func.count(Reserva.id_reserva)).where(
            Reserva.id_espacio == id_espacio,
            Reserva.estado.in_([
                EstadoReserva.PENDIENTE,
                EstadoReserva.APROBADA,
                EstadoReserva.CONFIRMADA,
                EstadoReserva.PAGADA
            ]),
            # Verificar solapamiento: (inicio < reserva.fin AND fin > reserva.inicio)
            and_(
                inicio < Reserva.fin,
                fin > Reserva.inicio
            )
        )
        
        if excluir_reserva_id:
            query = query.where(Reserva.id_reserva != excluir_reserva_id)
        
        result = await self.db.execute(query)
        conflictos = result.scalar()
        
        return conflictos == 0

    async def _convertir_a_response(self, reserva: Reserva) -> ReservaResponse:
        """Convertir modelo de reserva a schema de respuesta."""
        
        from src.schemas.reserva_schemas import EspacioResponse
        
        espacio_response = None
        if hasattr(reserva, 'espacio') and reserva.espacio:
            espacio_response = EspacioResponse(
                id_espacio=reserva.espacio.id_espacio,
                id_junta=reserva.espacio.id_junta,
                nombre=reserva.espacio.nombre,
                tipo=reserva.espacio.tipo,
                capacidad=reserva.espacio.capacidad,
                activo=reserva.espacio.activo
            )
        
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
            espacio=espacio_response
        )