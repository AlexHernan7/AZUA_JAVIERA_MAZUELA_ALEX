"""
Servicio para generar reportes y estadísticas de la junta.
"""

import logging
from datetime import datetime, date
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from src.database.models.espacio import Espacio
from src.database.models.reserva import Reserva
from src.database.models.certificado_pedido import CertificadoPedido
from src.database.models.vecino import Vecino
from src.database.models.directiva import Directiva
from src.database.models.usuario import Usuario
from src.database.models.junta import Junta

logger = logging.getLogger(__name__)


class ReporteService:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _filtrar_por_meses_especificos(self, query, meses_especificos: List[str], campo_fecha):
        """
        Filtra una consulta por meses específicos.
        
        Args:
            query: Consulta SQLAlchemy
            meses_especificos: Lista de meses en formato YYYY-MM
            campo_fecha: Campo de fecha a filtrar
            
        Returns:
            Consulta filtrada
        """
        if not meses_especificos:
            return query
            
        # Crear condiciones para cada mes
        condiciones = []
        for mes in meses_especificos:
            # Convertir YYYY-MM a rango de fechas
            año, mes_num = mes.split('-')
            fecha_inicio = datetime(int(año), int(mes_num), 1)
            if int(mes_num) == 12:
                fecha_fin = datetime(int(año) + 1, 1, 1)
            else:
                fecha_fin = datetime(int(año), int(mes_num) + 1, 1)
            
            condiciones.append(
                and_(
                    campo_fecha >= fecha_inicio,
                    campo_fecha < fecha_fin
                )
            )
        
        # Combinar todas las condiciones con OR
        if condiciones:
            query = query.where(or_(*condiciones))
            
        return query

    async def get_estadisticas_junta(
        self, 
        id_junta: int, 
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        meses_especificos: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas generales de una junta específica.
        
        Args:
            id_junta: ID de la junta
            fecha_desde: Fecha desde para filtrar (opcional)
            fecha_hasta: Fecha hasta para filtrar (opcional)
            meses_especificos: Lista de meses específicos en formato YYYY-MM (opcional)
            
        Returns:
            Diccionario con las estadísticas de la junta
        """
        try:
            # Si no se especifican fechas, usar el último año
            if not fecha_desde:
                fecha_desde = date.today().replace(month=1, day=1)
            if not fecha_hasta:
                fecha_hasta = date.today()

            # Debug: verificar que la junta existe
            junta_query = select(Junta).where(Junta.id_junta == id_junta)
            junta_result = await self.db.execute(junta_query)
            junta = junta_result.scalar_one_or_none()

            # 1. Espacios arrendados (total de reservas/arriendos)
            from datetime import datetime
            fecha_desde_dt = datetime.combine(fecha_desde, datetime.min.time())
            fecha_hasta_dt = datetime.combine(fecha_hasta, datetime.max.time())
            
            if meses_especificos:
                # Si hay meses específicos, contar reservas solo de esos meses
                logger.info(f"🔍 Debug - Contando arriendos para meses específicos: {meses_especificos}")
                arriendos_query = select(func.count(Reserva.id_reserva)).where(
                    Reserva.id_junta == id_junta
                )
                arriendos_query = self._filtrar_por_meses_especificos(arriendos_query, meses_especificos, Reserva.inicio)
            else:
                # Si no hay meses específicos, contar reservas en el rango de fechas
                logger.info(f"🔍 Debug - Contando arriendos en rango de fechas: {fecha_desde} - {fecha_hasta}")
                arriendos_query = select(func.count(Reserva.id_reserva)).where(
                    and_(
                        Reserva.id_junta == id_junta,
                        Reserva.inicio >= fecha_desde_dt,
                        Reserva.inicio <= fecha_hasta_dt
                    )
                )
            
            logger.info(f"🔍 Debug - Query de arriendos: {arriendos_query}")
            total_arriendos = await self.db.scalar(arriendos_query)
            logger.info(f"🔍 Debug - Total arriendos: {total_arriendos}")
            
            # Debug adicional: listar reservas por espacio
            if meses_especificos:
                reservas_por_espacio_query = select(
                    Espacio.nombre,
                    func.count(Reserva.id_reserva).label('total_reservas')
                ).select_from(
                    Espacio
                ).outerjoin(
                    Reserva, and_(
                        Reserva.id_espacio == Espacio.id_espacio,
                        Reserva.id_junta == id_junta
                    )
                ).where(
                    Espacio.id_junta == id_junta
                )
                # Aplicar filtro de meses específicos
                condiciones_meses = []
                for mes in meses_especificos:
                    año, mes_num = mes.split('-')
                    fecha_inicio = datetime(int(año), int(mes_num), 1)
                    if int(mes_num) == 12:
                        fecha_fin = datetime(int(año) + 1, 1, 1)
                    else:
                        fecha_fin = datetime(int(año), int(mes_num) + 1, 1)
                    
                    condiciones_meses.append(
                        and_(
                            Reserva.inicio >= fecha_inicio,
                            Reserva.inicio < fecha_fin
                        )
                    )
                
                if condiciones_meses:
                    reservas_por_espacio_query = reservas_por_espacio_query.where(
                        or_(*condiciones_meses)
                    )
            else:
                reservas_por_espacio_query = select(
                    Espacio.nombre,
                    func.count(Reserva.id_reserva).label('total_reservas')
                ).select_from(
                    Espacio
                ).outerjoin(
                    Reserva, and_(
                        Reserva.id_espacio == Espacio.id_espacio,
                        Reserva.id_junta == id_junta,
                        Reserva.inicio >= fecha_desde_dt,
                        Reserva.inicio <= fecha_hasta_dt
                    )
                ).where(
                    Espacio.id_junta == id_junta
                )
            
            reservas_por_espacio_query = reservas_por_espacio_query.group_by(
                Espacio.id_espacio, Espacio.nombre
            ).order_by(func.count(Reserva.id_reserva).desc())
            
            reservas_por_espacio_result = await self.db.execute(reservas_por_espacio_query)
            reservas_por_espacio = reservas_por_espacio_result.fetchall()
            logger.info(f"🔍 Debug - Reservas por espacio: {[(r.nombre, r.total_reservas) for r in reservas_por_espacio]}")

            # 2. Cantidad de certificados emitidos/descargados
            if meses_especificos:
                # Si hay meses específicos, usar solo esos meses
                certificados_query = select(func.count(CertificadoPedido.id_pedido)).where(
                    CertificadoPedido.id_junta == id_junta
                )
                certificados_query = self._filtrar_por_meses_especificos(certificados_query, meses_especificos, CertificadoPedido.created_at)
            else:
                # Si no hay meses específicos, usar el rango de fechas
                certificados_query = select(func.count(CertificadoPedido.id_pedido)).where(
                    and_(
                        CertificadoPedido.id_junta == id_junta,
                        CertificadoPedido.created_at >= fecha_desde,
                        CertificadoPedido.created_at <= fecha_hasta
                    )
                )
            
            total_certificados = await self.db.scalar(certificados_query)

            # 3. Ingresos totales (certificados + reservas)
            # Ingresos de certificados
            if meses_especificos:
                # Si hay meses específicos, usar solo esos meses
                ingresos_certificados_query = select(func.sum(CertificadoPedido.valor_certificado)).where(
                    and_(
                        CertificadoPedido.id_junta == id_junta,
                        CertificadoPedido.valor_certificado.isnot(None)
                    )
                )
                ingresos_certificados_query = self._filtrar_por_meses_especificos(ingresos_certificados_query, meses_especificos, CertificadoPedido.created_at)
            else:
                # Si no hay meses específicos, usar el rango de fechas
                ingresos_certificados_query = select(func.sum(CertificadoPedido.valor_certificado)).where(
                    and_(
                        CertificadoPedido.id_junta == id_junta,
                        CertificadoPedido.created_at >= fecha_desde,
                        CertificadoPedido.created_at <= fecha_hasta,
                        CertificadoPedido.valor_certificado.isnot(None)
                    )
                )
            
            ingresos_certificados = await self.db.scalar(ingresos_certificados_query) or 0

            # Ingresos de reservas
            
            if meses_especificos:
                # Si hay meses específicos, usar solo esos meses
                ingresos_reservas_query = select(func.sum(Reserva.valor_reserva)).where(
                    and_(
                        Reserva.id_junta == id_junta,
                        Reserva.valor_reserva.isnot(None)
                    )
                )
                ingresos_reservas_query = self._filtrar_por_meses_especificos(ingresos_reservas_query, meses_especificos, Reserva.inicio)
            else:
                # Si no hay meses específicos, usar el rango de fechas
                ingresos_reservas_query = select(func.sum(Reserva.valor_reserva)).where(
                    and_(
                        Reserva.id_junta == id_junta,
                        Reserva.inicio >= fecha_desde_dt,
                        Reserva.inicio <= fecha_hasta_dt,
                        Reserva.valor_reserva.isnot(None)
                    )
                )
            
            ingresos_reservas = await self.db.scalar(ingresos_reservas_query) or 0

            total_ingresos = ingresos_certificados + ingresos_reservas

            # 4. Usuarios registrados y activos de la junta
            # Total de vecinos registrados
            vecinos_query = select(func.count(Vecino.id_vecino)).where(
                Vecino.id_junta == id_junta
            )
            total_vecinos = await self.db.scalar(vecinos_query)

            # Total de directivos
            directivos_query = select(func.count(Directiva.id_directiva)).where(
                Directiva.id_junta == id_junta
            )
            total_directivos = await self.db.scalar(directivos_query)

            total_usuarios = total_vecinos + total_directivos

            # 5. Reservas totales en el período
            reservas_query = select(func.count(Reserva.id_reserva)).where(
                and_(
                    Reserva.id_junta == id_junta,
                    Reserva.inicio >= fecha_desde_dt,
                    Reserva.inicio <= fecha_hasta_dt
                )
            )
            
            # Aplicar filtro de meses específicos si se proporcionan
            if meses_especificos:
                reservas_query = self._filtrar_por_meses_especificos(reservas_query, meses_especificos, Reserva.inicio)
            
            total_reservas = await self.db.scalar(reservas_query)

            # 6. Estadísticas por espacio (optimizada con join más eficiente)
            # Construir condiciones del join
            join_conditions = and_(
                Reserva.id_espacio == Espacio.id_espacio,
                Reserva.inicio >= fecha_desde_dt,
                Reserva.inicio <= fecha_hasta_dt,
                Reserva.valor_reserva.isnot(None)
            )
            
            # Aplicar filtro de meses específicos si se proporcionan
            if meses_especificos:
                # Crear condiciones para cada mes
                condiciones_meses = []
                for mes in meses_especificos:
                    año, mes_num = mes.split('-')
                    fecha_inicio = datetime(int(año), int(mes_num), 1)
                    if int(mes_num) == 12:
                        fecha_fin = datetime(int(año) + 1, 1, 1)
                    else:
                        fecha_fin = datetime(int(año), int(mes_num) + 1, 1)
                    
                    condiciones_meses.append(
                        and_(
                            Reserva.inicio >= fecha_inicio,
                            Reserva.inicio < fecha_fin
                        )
                    )
                
                if condiciones_meses:
                    join_conditions = and_(
                        Reserva.id_espacio == Espacio.id_espacio,
                        or_(*condiciones_meses),
                        Reserva.valor_reserva.isnot(None)
                    )

            espacios_stats_query = select(
                Espacio.nombre,
                func.count(Reserva.id_reserva).label('total_reservas'),
                func.coalesce(func.sum(Reserva.valor_reserva), 0).label('ingresos_espacio')
            ).select_from(
                Espacio
            ).outerjoin(
                Reserva, join_conditions
            ).where(
                Espacio.id_junta == id_junta
            ).group_by(
                Espacio.id_espacio, Espacio.nombre
            ).order_by(
                func.count(Reserva.id_reserva).desc()
            )

            espacios_stats_result = await self.db.execute(espacios_stats_query)
            espacios_stats = [
                {
                    'nombre': row.nombre,
                    'total_reservas': row.total_reservas or 0,
                    'ingresos': row.ingresos_espacio or 0
                }
                for row in espacios_stats_result
            ]

            # 7. Estadísticas mensuales de ingresos
            # Definir la expresión una sola vez para evitar problemas de GROUP BY
            mes_trunc = func.date_trunc('month', Reserva.inicio)
            
            ingresos_mensuales_query = select(
                mes_trunc.label('mes'),
                func.sum(Reserva.valor_reserva).label('ingresos_reservas'),
                func.count(Reserva.id_reserva).label('cantidad_reservas')
            ).where(
                and_(
                    Reserva.id_junta == id_junta,
                    Reserva.inicio >= fecha_desde_dt,
                    Reserva.inicio <= fecha_hasta_dt,
                    Reserva.valor_reserva.isnot(None)
                )
            )
            
            # Aplicar filtro de meses específicos si se proporcionan
            if meses_especificos:
                ingresos_mensuales_query = self._filtrar_por_meses_especificos(ingresos_mensuales_query, meses_especificos, Reserva.inicio)
            
            ingresos_mensuales_query = ingresos_mensuales_query.group_by(mes_trunc).order_by('mes')

            ingresos_mensuales_result = await self.db.execute(ingresos_mensuales_query)
            ingresos_mensuales = [
                {
                    'mes': row.mes.strftime('%Y-%m'),
                    'ingresos': row.ingresos_reservas or 0,
                    'cantidad_reservas': row.cantidad_reservas or 0
                }
                for row in ingresos_mensuales_result
            ]

            estadisticas = {
                'total_espacios': total_arriendos,  # Cambiado para mostrar total de arriendos
                'total_certificados': total_certificados,
                'total_ingresos': total_ingresos,
                'ingresos_certificados': ingresos_certificados,
                'ingresos_reservas': ingresos_reservas,
                'total_usuarios': total_usuarios,
                'total_vecinos': total_vecinos,
                'total_directivos': total_directivos,
                'total_reservas': total_reservas,
                'espacios_stats': espacios_stats,
                'ingresos_mensuales': ingresos_mensuales,
                'periodo': {
                    'fecha_desde': fecha_desde.isoformat(),
                    'fecha_hasta': fecha_hasta.isoformat()
                }
            }

            return estadisticas

        except Exception as e:
            logger.error(f"❌ Error generando estadísticas para junta {id_junta}: {e}")
            raise

    async def get_ingresos_por_mes(
        self, 
        id_junta: int, 
        meses: int = 12
    ) -> List[Dict[str, Any]]:
        """
        Obtiene ingresos por mes para los últimos N meses.
        
        Args:
            id_junta: ID de la junta
            meses: Número de meses hacia atrás
            
        Returns:
            Lista de ingresos por mes
        """
        try:
            from datetime import timedelta, datetime
            
            fecha_desde = date.today() - timedelta(days=meses * 30)
            fecha_desde_dt = datetime.combine(fecha_desde, datetime.min.time())
            fecha_hasta_dt = datetime.now()
            
            # Ingresos de reservas por mes
            # Definir la expresión una sola vez para evitar problemas de GROUP BY
            mes_trunc = func.date_trunc('month', Reserva.inicio)
            
            query = select(
                mes_trunc.label('mes'),
                func.sum(Reserva.valor_reserva).label('ingresos')
            ).where(
                and_(
                    Reserva.id_junta == id_junta,
                    Reserva.inicio >= fecha_desde_dt,
                    Reserva.inicio <= fecha_hasta_dt,
                    Reserva.valor_reserva.isnot(None)
                )
            ).group_by(
                mes_trunc
            ).order_by('mes')

            result = await self.db.execute(query)
            return [
                {
                    'mes': row.mes.strftime('%Y-%m'),
                    'ingresos': row.ingresos or 0
                }
                for row in result
            ]

        except Exception as e:
            logger.error(f"❌ Error obteniendo ingresos por mes: {e}")
            raise

    async def get_distribucion_reservas(
        self, 
        id_junta: int, 
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        meses_especificos: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene distribución de reservas por espacio.
        
        Args:
            id_junta: ID de la junta
            fecha_desde: Fecha desde (opcional)
            fecha_hasta: Fecha hasta (opcional)
            meses_especificos: Lista de meses específicos en formato YYYY-MM (opcional)
            
        Returns:
            Lista de distribución por espacio
        """
        try:
            if not fecha_desde:
                fecha_desde = date.today().replace(month=1, day=1)
            if not fecha_hasta:
                fecha_hasta = date.today()

            from datetime import datetime
            fecha_desde_dt = datetime.combine(fecha_desde, datetime.min.time())
            fecha_hasta_dt = datetime.combine(fecha_hasta, datetime.max.time())

            # Construir condiciones del join
            join_conditions = and_(
                Reserva.id_espacio == Espacio.id_espacio,
                Reserva.inicio >= fecha_desde_dt,
                Reserva.inicio <= fecha_hasta_dt
            )
            
            # Aplicar filtro de meses específicos si se proporcionan
            if meses_especificos:
                # Crear condiciones para cada mes
                condiciones_meses = []
                for mes in meses_especificos:
                    año, mes_num = mes.split('-')
                    fecha_inicio = datetime(int(año), int(mes_num), 1)
                    if int(mes_num) == 12:
                        fecha_fin = datetime(int(año) + 1, 1, 1)
                    else:
                        fecha_fin = datetime(int(año), int(mes_num) + 1, 1)
                    
                    condiciones_meses.append(
                        and_(
                            Reserva.inicio >= fecha_inicio,
                            Reserva.inicio < fecha_fin
                        )
                    )
                
                if condiciones_meses:
                    join_conditions = and_(
                        Reserva.id_espacio == Espacio.id_espacio,
                        or_(*condiciones_meses)
                    )

            query = select(
                Espacio.nombre,
                func.count(Reserva.id_reserva).label('cantidad')
            ).select_from(
                Espacio
            ).outerjoin(
                Reserva, join_conditions
            ).where(
                Espacio.id_junta == id_junta
            ).group_by(
                Espacio.id_espacio, Espacio.nombre
            ).order_by(
                func.count(Reserva.id_reserva).desc()
            ).limit(10)  # Limitar a los 10 espacios más utilizados

            result = await self.db.execute(query)
            return [
                {
                    'espacio': row.nombre,
                    'cantidad': row.cantidad or 0
                }
                for row in result
            ]

        except Exception as e:
            logger.error(f"❌ Error obteniendo distribución de reservas: {e}")
            raise

    async def get_certificados_por_mes(
        self, 
        id_junta: int, 
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        meses_especificos: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene certificados emitidos por mes.
        
        Args:
            id_junta: ID de la junta
            fecha_desde: Fecha desde (opcional)
            fecha_hasta: Fecha hasta (opcional)
            meses_especificos: Lista de meses específicos en formato YYYY-MM (opcional)
            
        Returns:
            Lista de certificados por mes
        """
        try:
            if not fecha_desde:
                fecha_desde = date.today().replace(month=1, day=1)
            if not fecha_hasta:
                fecha_hasta = date.today()

            from datetime import datetime
            fecha_desde_dt = datetime.combine(fecha_desde, datetime.min.time())
            fecha_hasta_dt = datetime.combine(fecha_hasta, datetime.max.time())

            # Definir la expresión una sola vez para evitar problemas de GROUP BY
            mes_trunc = func.date_trunc('month', CertificadoPedido.created_at)
            
            query = select(
                mes_trunc.label('mes'),
                func.count(CertificadoPedido.id_pedido).label('cantidad')
            ).where(
                and_(
                    CertificadoPedido.id_junta == id_junta,
                    CertificadoPedido.created_at >= fecha_desde_dt,
                    CertificadoPedido.created_at <= fecha_hasta_dt
                )
            )
            
            # Aplicar filtro de meses específicos si se proporcionan
            if meses_especificos:
                query = self._filtrar_por_meses_especificos(query, meses_especificos, CertificadoPedido.created_at)
            
            query = query.group_by(mes_trunc).order_by('mes')

            result = await self.db.execute(query)
            return [
                {
                    'mes': row.mes.strftime('%Y-%m'),
                    'cantidad': row.cantidad or 0
                }
                for row in result
            ]

        except Exception as e:
            logger.error(f"❌ Error obteniendo certificados por mes: {e}")
            raise

    async def get_usuarios_por_mes(
        self, 
        id_junta: int, 
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        meses_especificos: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene usuarios nuevos registrados por mes.
        
        Args:
            id_junta: ID de la junta
            fecha_desde: Fecha desde (opcional)
            fecha_hasta: Fecha hasta (opcional)
            meses_especificos: Lista de meses específicos en formato YYYY-MM (opcional)
            
        Returns:
            Lista de usuarios nuevos por mes
        """
        try:
            if not fecha_desde:
                fecha_desde = date.today().replace(month=1, day=1)
            if not fecha_hasta:
                fecha_hasta = date.today()

            from datetime import datetime
            fecha_desde_dt = datetime.combine(fecha_desde, datetime.min.time())
            fecha_hasta_dt = datetime.combine(fecha_hasta, datetime.max.time())

            # Usar la fecha de creación del usuario para agrupar por mes
            # Formatear directamente usando to_char para evitar problemas de zona horaria
            # date_trunc devuelve un timestamp, y to_char lo formatea usando la zona horaria del timestamp
            mes_trunc = func.date_trunc('month', Usuario.created_at)
            mes_formateado = func.to_char(mes_trunc, 'YYYY-MM')
            
            query = select(
                mes_formateado.label('mes'),
                func.count(Usuario.id_usuario).label('cantidad')
            ).where(
                and_(
                    Usuario.id_junta == id_junta,
                    Usuario.created_at >= fecha_desde_dt,
                    Usuario.created_at <= fecha_hasta_dt
                )
            )
            
            # Aplicar filtro de meses específicos si se proporcionan
            if meses_especificos:
                query = self._filtrar_por_meses_especificos(query, meses_especificos, Usuario.created_at)
            
            query = query.group_by(mes_formateado).order_by('mes')

            result = await self.db.execute(query)
            return [
                {
                    'mes': row.mes,
                    'cantidad': row.cantidad or 0
                }
                for row in result
            ]

        except Exception as e:
            logger.error(f"❌ Error obteniendo usuarios por mes: {e}")
            raise
