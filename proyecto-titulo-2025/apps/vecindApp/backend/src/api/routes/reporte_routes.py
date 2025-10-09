"""
Rutas para reportes y estadísticas.
"""

import logging
from datetime import date, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_db_session
from src.services.reporte_service import ReporteService
from src.schemas.reporte_schemas import (
    EstadisticasJuntaResponse,
    ReporteDashboardResponse,
    KPIResponse,
    IngresoMensualResponse,
    CertificadoMensualResponse,
    DistribucionReservaResponse,
    EspacioStatsResponse,
    PeriodoResponse
)
from src.api.routes.user_routes import verify_user_token
from src.services.auth_service import AuthService

# Crear router para reportes
router = APIRouter(prefix="/reportes", tags=["Reportes"])

logger = logging.getLogger(__name__)


@router.get(
    "/dashboard",
    response_model=ReporteDashboardResponse,
    summary="Obtener dashboard de reportes",
    description="Obtiene el dashboard completo de reportes para la junta del usuario autenticado",
    responses={
        200: {"description": "Dashboard obtenido exitosamente"},
        401: {"description": "Token inválido o expirado"},
        403: {"description": "Usuario no tiene permisos de directiva"},
        404: {"description": "Usuario no tiene junta asociada"},
    }
)
async def get_dashboard_reportes(
    fecha_desde: Optional[date] = Query(None, description="Fecha desde (YYYY-MM-DD)"),
    fecha_hasta: Optional[date] = Query(None, description="Fecha hasta (YYYY-MM-DD)"),
    meses: Optional[str] = Query(None, description="Meses específicos separados por coma (YYYY-MM)"),
    user_id: int = Depends(verify_user_token),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Obtiene el dashboard completo de reportes para la junta del usuario autenticado.
    Solo usuarios con rol 'directiva' pueden acceder a este endpoint.
    """
    try:
        # Verificar que el usuario tenga rol de directiva
        auth_service = AuthService(db)
        user_data = await auth_service.get_user_with_roles(user_id)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        user, roles = user_data
        
        if 'directiva' not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo usuarios con rol 'directiva' pueden acceder a los reportes"
            )

        # Obtener la junta del usuario
        user = user_data[0]
        
        # Verificar si tiene perfil de vecino o directiva
        id_junta = None
        if user.vecino and user.vecino.id_junta:
            id_junta = user.vecino.id_junta
        elif user.directiva and user.directiva.id_junta:
            id_junta = user.directiva.id_junta
        
        if not id_junta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no tiene una junta asociada"
            )

        # Procesar meses específicos si se proporcionan
        meses_especificos = None
        if meses:
            meses_especificos = [mes.strip() for mes in meses.split(',')]

        # Si no se especifican fechas, usar el último año
        if not fecha_desde:
            fecha_desde = date.today().replace(month=1, day=1)
        if not fecha_hasta:
            fecha_hasta = date.today()

        # Crear servicio de reportes
        reporte_service = ReporteService(db)

        # Obtener estadísticas generales
        estadisticas = await reporte_service.get_estadisticas_junta(
            id_junta=id_junta,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            meses_especificos=meses_especificos
        )

        # Crear KPIs
        logger.info(f"🔍 Debug - Total arriendos para KPI: {estadisticas['total_espacios']}")
        kpis = [
            KPIResponse(
                label="Espacios Arrendados",
                value=estadisticas['total_espacios'],
                suffix="arriendos"
            ),
            KPIResponse(
                label="Certificados Emitidos",
                value=estadisticas['total_certificados'],
                suffix="certificados"
            ),
            KPIResponse(
                label="Ingresos Totales",
                value=estadisticas['total_ingresos'],
                prefix="$",
                suffix="CLP"
            ),
            KPIResponse(
                label="Usuarios Activos",
                value=estadisticas['total_usuarios'],
                suffix="usuarios"
            )
        ]

        # Obtener ingresos mensuales
        ingresos_mensuales = [
            IngresoMensualResponse(mes=item['mes'], ingresos=item['ingresos'])
            for item in estadisticas['ingresos_mensuales']
        ]

        # Obtener certificados por mes
        certificados_mensuales = await reporte_service.get_certificados_por_mes(
            id_junta=id_junta,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            meses_especificos=meses_especificos
        )

        certificados_mensuales_response = [
            CertificadoMensualResponse(mes=item['mes'], cantidad=item['cantidad'])
            for item in certificados_mensuales
        ]

        # Obtener distribución de reservas
        distribucion_reservas = await reporte_service.get_distribucion_reservas(
            id_junta=id_junta,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            meses_especificos=meses_especificos
        )

        distribucion_reservas_response = [
            DistribucionReservaResponse(espacio=item['espacio'], cantidad=item['cantidad'])
            for item in distribucion_reservas
        ]

        # Resumen por espacios
        resumen_espacios = [
            EspacioStatsResponse(
                nombre=item['nombre'],
                total_reservas=item['total_reservas'],
                ingresos=item['ingresos']
            )
            for item in estadisticas['espacios_stats']
        ]

        # Crear respuesta
        dashboard = ReporteDashboardResponse(
            kpis=kpis,
            ingresos_mensuales=ingresos_mensuales,
            certificados_mensuales=certificados_mensuales_response,
            distribucion_reservas=distribucion_reservas_response,
            resumen_espacios=resumen_espacios,
            periodo=PeriodoResponse(
                fecha_desde=estadisticas['periodo']['fecha_desde'],
                fecha_hasta=estadisticas['periodo']['fecha_hasta']
            )
        )

        return dashboard

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error generando dashboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get(
    "/estadisticas",
    response_model=EstadisticasJuntaResponse,
    summary="Obtener estadísticas detalladas",
    description="Obtiene estadísticas detalladas de la junta del usuario autenticado",
    responses={
        200: {"description": "Estadísticas obtenidas exitosamente"},
        401: {"description": "Token inválido o expirado"},
        403: {"description": "Usuario no tiene permisos de directiva"},
        404: {"description": "Usuario no tiene junta asociada"},
    }
)
async def get_estadisticas_detalladas(
    fecha_desde: Optional[date] = Query(None, description="Fecha desde (YYYY-MM-DD)"),
    fecha_hasta: Optional[date] = Query(None, description="Fecha hasta (YYYY-MM-DD)"),
    user_id: int = Depends(verify_user_token),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Obtiene estadísticas detalladas de la junta del usuario autenticado.
    Solo usuarios con rol 'directiva' pueden acceder a este endpoint.
    """
    try:
        # Verificar que el usuario tenga rol de directiva
        auth_service = AuthService(db)
        user_data = await auth_service.get_user_with_roles(user_id)
        
        logger.info(f"🔍 Debug - User ID: {user_id}")
        logger.info(f"🔍 Debug - User data: {user_data}")
        
        if not user_data:
            logger.error(f"❌ Usuario {user_id} no encontrado")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        user, roles = user_data
        logger.info(f"🔍 Debug - Usuario: {user.email}")
        logger.info(f"🔍 Debug - Roles: {roles}")
        
        if 'directiva' not in roles:
            logger.error(f"❌ Usuario {user.email} no tiene rol directiva. Roles: {roles}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo usuarios con rol 'directiva' pueden acceder a los reportes"
            )

        # Obtener la junta del usuario
        user = user_data[0]
        logger.info(f"🔍 Debug - User object: {user}")
        logger.info(f"🔍 Debug - User.vecino: {user.vecino}")
        logger.info(f"🔍 Debug - User.directiva: {user.directiva}")
        
        # Verificar si tiene perfil de vecino o directiva
        id_junta = None
        if user.vecino and user.vecino.id_junta:
            id_junta = user.vecino.id_junta
            logger.info(f"🔍 Debug - ID junta desde vecino: {id_junta}")
        elif user.directiva and user.directiva.id_junta:
            id_junta = user.directiva.id_junta
            logger.info(f"🔍 Debug - ID junta desde directiva: {id_junta}")
        
        if not id_junta:
            logger.error(f"❌ Usuario {user.email} no tiene junta asociada")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no tiene una junta asociada"
            )

        # Si no se especifican fechas, usar el último año
        if not fecha_desde:
            fecha_desde = date.today().replace(month=1, day=1)
        if not fecha_hasta:
            fecha_hasta = date.today()

        logger.info(f"📊 Generando estadísticas detalladas para junta {id_junta}")

        # Crear servicio de reportes
        reporte_service = ReporteService(db)

        # Obtener estadísticas
        estadisticas = await reporte_service.get_estadisticas_junta(
            id_junta=id_junta,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta
        )

        # Convertir a response model
        response = EstadisticasJuntaResponse(
            total_espacios=estadisticas['total_espacios'],
            total_certificados=estadisticas['total_certificados'],
            total_ingresos=estadisticas['total_ingresos'],
            ingresos_certificados=estadisticas['ingresos_certificados'],
            ingresos_reservas=estadisticas['ingresos_reservas'],
            total_usuarios=estadisticas['total_usuarios'],
            total_vecinos=estadisticas['total_vecinos'],
            total_directivos=estadisticas['total_directivos'],
            total_reservas=estadisticas['total_reservas'],
            espacios_stats=[
                EspacioStatsResponse(
                    nombre=item['nombre'],
                    total_reservas=item['total_reservas'],
                    ingresos=item['ingresos']
                )
                for item in estadisticas['espacios_stats']
            ],
            ingresos_mensuales=[
                IngresoMensualResponse(mes=item['mes'], ingresos=item['ingresos'])
                for item in estadisticas['ingresos_mensuales']
            ],
            periodo=PeriodoResponse(
                fecha_desde=estadisticas['periodo']['fecha_desde'],
                fecha_hasta=estadisticas['periodo']['fecha_hasta']
            )
        )

        logger.info(f"✅ Estadísticas detalladas generadas para junta {id_junta}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error generando estadísticas detalladas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )
