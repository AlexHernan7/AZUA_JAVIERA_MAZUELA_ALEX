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
    "/maipu",
    response_model=Union[NewsResponse, NewsErrorResponse],
    summary="Obtener noticias de Maipú",
    description="Obtiene las últimas noticias de la comuna de Maipú desde La Voz de Maipú. "
    "Las noticias se obtienen del feed RSS en tiempo real y no se almacenan en la base de datos. "
    "Incluye noticias locales relevantes para los vecinos de Maipú.",
)
async def get_maipu_news(
    limit: int = Query(default=10, ge=1, le=20, description="Número de noticias a obtener (1-20)")
):
    """
    Obtiene las últimas noticias de Maipú.
    
    Args:
        limit: Número de noticias a obtener (1-20, defecto 10)
    """
    try:
        news_service = NewsService()
        articles, total_results = await news_service.get_maipu_news(limit=limit)
        
        return NewsResponse(
            articles=articles,
            total_results=total_results,
            status="success",
            message=f"Se obtuvieron {len(articles)} noticias de Maipú correctamente"
        )
        
    except Exception as e:
        return NewsErrorResponse(
            status="error",
            message=str(e)
        )


@router.get(
    "/health",
    summary="Verificar estado del servicio de noticias RSS",
    description="Endpoint para verificar si el servicio de noticias RSS está funcionando correctamente."
)
async def news_health_check():
    """
    Verifica el estado del servicio de noticias.
    """
    try:
        news_service = NewsService()
        # Intentar obtener solo 1 noticia para verificar conectividad
        articles, total = await news_service.get_maipu_news(limit=1)
        
        return {
            "status": "OK",
            "message": "Servicio de noticias RSS funcionando correctamente",
            "rss_connection": "active",
            "feed_source": "La Voz de Maipú",
            "test_results": f"Obtenida {len(articles)} noticia de prueba"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Servicio de noticias no disponible: {str(e)}"
        )
