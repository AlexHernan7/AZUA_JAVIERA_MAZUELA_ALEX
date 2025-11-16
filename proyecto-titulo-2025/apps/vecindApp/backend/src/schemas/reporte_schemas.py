"""
Schemas para reportes y estadísticas.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date


class EspacioStatsResponse(BaseModel):
    """Estadísticas de un espacio específico."""
    nombre: str = Field(..., description="Nombre del espacio")
    total_reservas: int = Field(..., description="Total de reservas del espacio")
    ingresos: float = Field(..., description="Ingresos generados por el espacio")


class IngresoMensualResponse(BaseModel):
    """Ingresos por mes."""
    mes: str = Field(..., description="Mes en formato YYYY-MM")
    ingresos: float = Field(..., description="Ingresos del mes")
    cantidad_reservas: int = Field(0, description="Cantidad de reservas del mes")


class DistribucionReservaResponse(BaseModel):
    """Distribución de reservas por espacio."""
    espacio: str = Field(..., description="Nombre del espacio")
    cantidad: int = Field(..., description="Cantidad de reservas")


class CertificadoMensualResponse(BaseModel):
    """Certificados emitidos por mes."""
    mes: str = Field(..., description="Mes en formato YYYY-MM")
    cantidad: int = Field(..., description="Cantidad de certificados emitidos")


class PeriodoResponse(BaseModel):
    """Período de consulta."""
    fecha_desde: str = Field(..., description="Fecha desde en formato ISO")
    fecha_hasta: str = Field(..., description="Fecha hasta en formato ISO")


class EstadisticasJuntaResponse(BaseModel):
    """Estadísticas completas de una junta."""
    total_espacios: int = Field(..., description="Total de espacios de la junta")
    total_certificados: int = Field(..., description="Total de certificados emitidos en el período")
    total_ingresos: float = Field(..., description="Ingresos totales (certificados + reservas)")
    ingresos_certificados: float = Field(..., description="Ingresos por certificados")
    ingresos_reservas: float = Field(..., description="Ingresos por reservas")
    total_usuarios: int = Field(..., description="Total de usuarios (vecinos + directivos)")
    total_vecinos: int = Field(..., description="Total de vecinos registrados")
    total_directivos: int = Field(..., description="Total de directivos")
    total_reservas: int = Field(..., description="Total de reservas en el período")
    espacios_stats: List[EspacioStatsResponse] = Field(..., description="Estadísticas por espacio")
    ingresos_mensuales: List[IngresoMensualResponse] = Field(..., description="Ingresos por mes")
    periodo: PeriodoResponse = Field(..., description="Período de consulta")


class ReporteRequest(BaseModel):
    """Request para generar reportes."""
    fecha_desde: Optional[date] = Field(None, description="Fecha desde para filtrar")
    fecha_hasta: Optional[date] = Field(None, description="Fecha hasta para filtrar")
    meses: Optional[int] = Field(12, description="Número de meses para ingresos mensuales")


class KPIResponse(BaseModel):
    """KPI individual."""
    label: str = Field(..., description="Etiqueta del KPI")
    value: float = Field(..., description="Valor del KPI")
    prefix: Optional[str] = Field(None, description="Prefijo del valor")
    suffix: Optional[str] = Field(None, description="Sufijo del valor")


class ReporteDashboardResponse(BaseModel):
    """Respuesta completa del dashboard de reportes."""
    kpis: List[KPIResponse] = Field(..., description="KPIs principales")
    ingresos_mensuales: List[IngresoMensualResponse] = Field(..., description="Ingresos por mes")
    certificados_mensuales: List[CertificadoMensualResponse] = Field(..., description="Certificados por mes")
    distribucion_reservas: List[DistribucionReservaResponse] = Field(..., description="Distribución de reservas")
    resumen_espacios: List[EspacioStatsResponse] = Field(..., description="Resumen por espacios")
    periodo: PeriodoResponse = Field(..., description="Período de consulta")
