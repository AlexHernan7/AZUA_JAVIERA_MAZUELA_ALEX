"""
Rutas para el manejo de noticias.
"""

from fastapi import APIRouter, HTTPException, status, Query
from typing import Union
from src.services.news_service import NewsService
from src.schemas.news_schemas import NewsResponse, NewsErrorResponse

# Crear router para rutas de noticias
router = APIRouter(prefix="/news", tags=["Noticias"])


@router.get(
    "/chile",
    response_model=Union[NewsResponse, NewsErrorResponse],
    summary="Obtener noticias de Chile",
    description="Obtiene las últimas noticias de Chile usando APITube. "
    "Las noticias se obtienen en tiempo real y no se almacenan en la base de datos. "
    "Incluye noticias específicas de Chile filtradas por país y términos de búsqueda.",
)
async def get_chile_news(
    limit: int = Query(default=10, ge=1, le=50, description="Número de noticias a obtener (1-50)")
):
    """
    Obtiene las últimas noticias de Chile.
    
    Args:
        limit: Número de noticias a obtener (1-50, defecto 10)
    """
    try:
        news_service = NewsService()
        articles, total_results = await news_service.get_chile_news(limit=limit)
        
        return NewsResponse(
            articles=articles,
            total_results=total_results,
            status="success",
            message=f"Se obtuvieron {len(articles)} noticias de Chile correctamente"
        )
        
    except Exception as e:
        return NewsErrorResponse(
            status="error",
            message=str(e)
        )


@router.get(
    "/health",
    summary="Verificar estado del servicio de noticias",
    description="Endpoint para verificar si el servicio de noticias está funcionando correctamente."
)
async def news_health_check():
    """
    Verifica el estado del servicio de noticias.
    """
    try:
        news_service = NewsService()
        # Intentar obtener solo 1 noticia para verificar conectividad
        articles, total = await news_service.get_chile_news(limit=1)
        
        return {
            "status": "OK",
            "message": "Servicio de noticias funcionando correctamente",
            "api_connection": "active",
            "test_results": f"Obtenida {len(articles)} noticia de prueba"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Servicio de noticias no disponible: {str(e)}"
        )
