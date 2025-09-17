"""
Servicio para consumir la API de noticias APITube.
"""

import httpx
from typing import List
from src.schemas.news_schemas import NewsArticle
from src.core.config import settings
import logging

logger = logging.getLogger(__name__)


class NewsService:
    """Servicio para obtener noticias desde APITube."""
    
    def __init__(self):
        self.api_key = settings.news_api.api_key
        self.base_url = settings.news_api.base_url
        self.timeout = settings.news_api.timeout
        self.max_articles = settings.news_api.max_articles
        self.headers = {
            "User-Agent": "VecindApp/1.0",
            "Content-Type": "application/json",
            "X-API-Key": self.api_key  # APITube usa X-API-Key header
        }
    
    async def get_chile_news(self, limit: int = 10) -> tuple[List[NewsArticle], int]:
        """
        Obtiene noticias de Chile desde APITube.
        
        Args:
            limit: Número máximo de noticias (default: 10)
        """
        logger.info(f"Obteniendo {limit} noticias específicas de Chile desde APITube (país: CL)")
        
        try:
            # Obtener noticias directamente del endpoint principal
            articles, total_results = await self._fetch_from_apitube(limit)
            logger.info(f"Se obtuvieron {len(articles)} noticias de APITube")
            return articles, total_results
            
        except Exception as e:
            logger.warning(f"Error al obtener noticias de APITube: {e}")
            logger.info("Usando noticias de fallback")
            # Imprimir traceback para debug
            import traceback
            logger.error(f"Traceback completo: {traceback.format_exc()}")
            # Usar datos de fallback si la API falla
            articles = self._get_fallback_news(limit)
            return articles, len(articles)
    
    async def _fetch_from_apitube(self, limit: int = 10) -> tuple[List[NewsArticle], int]:
        """
        Obtiene noticias desde APITube.
        
        Args:
            limit: Número máximo de noticias a obtener
            
        Returns:
            Tupla con (lista de artículos, total de resultados)
        """
        # Validar límite según las restricciones de APITube (plan gratuito tiene límites bajos)
        per_page = min(limit, 10)  # APITube plan gratuito permite máximo 10
        
        # Parámetros para obtener noticias específicas de Chile
        # Usar búsqueda por palabras clave para encontrar noticias relevantes
        params = {
            'per_page': per_page,
            'page': 1,
            'q': 'Chile OR Santiago OR chileno OR chilena OR "América Latina"',  # Búsqueda específica
            'language': 'es'  # Preferir noticias en español
        }
        
        url = f"{self.base_url}/news/everything"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, params=params, headers=self.headers)
            
            if response.status_code != 200:
                raise Exception(f"APITube error: {response.status_code} - {response.text}")
            
            data = response.json()
            
            # Debug: imprimir la respuesta completa para entender el problema
            logger.info(f"Respuesta APITube: status={data.get('status')}, keys={list(data.keys())}")
            
            # APITube usa 'status' en lugar de 'success'
            if data.get('status') != 'ok':
                logger.error(f"Status no es 'ok': {data.get('status')}")
                logger.error(f"Errores APITube: {data.get('errors', [])}")
                # Extraer mensaje de error de la lista de errores
                errors = data.get('errors', [])
                error_message = errors[0].get('message', 'Unknown error') if errors else 'Unknown error'
                raise Exception(f"APITube error: {error_message}")
            
            # Debug: imprimir información de la respuesta
            logger.info(f"Status APITube: {data.get('status')}")
            logger.info(f"Cantidad de results: {len(data.get('results', []))}")
            
            articles = []
            # APITube usa 'results' en lugar de 'data'
            for article_data in data.get('results', []):
                # Extraer campos básicos que están disponibles
                title = article_data.get('title', '')
                href = article_data.get('href', '')
                published_at = article_data.get('published_at', '')
                
                # Extraer información de la fuente
                source_info = article_data.get('source', {})
                source_name = None
                if isinstance(source_info, dict):
                    source_name = source_info.get('name') or source_info.get('domain')
                elif isinstance(source_info, str):
                    source_name = source_info
                
                # Extraer descripción de varios campos posibles
                description = (
                    article_data.get('description') or 
                    article_data.get('snippet') or 
                    article_data.get('summary', [{}])[0] if article_data.get('summary') else None
                )
                
                # Extraer imagen de media array si existe
                image_url = None
                media_items = article_data.get('media', [])
                if media_items:
                    for media in media_items:
                        if media.get('type') == 'image':
                            image_url = media.get('url')
                            break
                
                # Extraer nombre del autor
                author_info = article_data.get('author')
                author_name = None
                if isinstance(author_info, dict):
                    author_name = author_info.get('name')
                elif isinstance(author_info, str):
                    author_name = author_info
                
                # Solo procesar si tenemos datos básicos
                if title and href:
                    article = NewsArticle(
                        title=title,
                        description=description,
                        url=href,
                        image_url=image_url,
                        published_at=published_at,
                        source_name=source_name,
                        author=author_name
                    )
                    articles.append(article)
            
            # Verificar si hay noticias relevantes de Chile en los resultados
            chile_relevant_count = 0
            for article in articles:
                title_lower = article.title.lower()
                source_lower = (article.source_name or '').lower()
                desc_lower = (article.description or '').lower()
                
                if any(keyword in title_lower or keyword in source_lower or keyword in desc_lower 
                       for keyword in ['chile', 'chileno', 'chilena', 'santiago', '.cl']):
                    chile_relevant_count += 1
            
            # Si menos del 30% son relevantes para Chile, priorizar noticias específicas de Chile
            if chile_relevant_count < max(1, len(articles) * 0.3):
                logger.info(f"Solo {chile_relevant_count} de {len(articles)} noticias son relevantes para Chile")
                logger.info("Priorizando noticias específicas de Chile")
                
                # Obtener noticias de fallback de Chile
                chile_articles = self._get_fallback_news(limit)
                
                # Combinar: primero las noticias de Chile, luego algunas internacionales
                chile_count = min(len(chile_articles), int(limit * 0.7))  # 70% noticias de Chile
                international_count = limit - chile_count
                
                final_articles = chile_articles[:chile_count]
                if international_count > 0:
                    final_articles.extend(articles[:international_count])
                
                articles = final_articles
            
            # APITube podría no tener 'total', usar length de results
            total_results = len(articles)
            return articles[:limit], total_results
    
    def _get_fallback_news(self, limit: int = 10) -> List[NewsArticle]:
        """
        Devuelve noticias de fallback cuando la API externa no está disponible.
        """
        fallback_articles = [
            NewsArticle(
                title="Gobierno anuncia nuevas medidas económicas para el 2025",
                description="El ejecutivo presentó un paquete de medidas destinadas a impulsar la economía nacional y apoyar a las pequeñas y medianas empresas.",
                url="https://example.com/noticia1",
                image_url="https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=400&h=200&fit=crop&crop=center",
                published_at="2024-09-16T10:00:00Z",
                source_name="Portal Noticias Chile",
                author="Redacción"
            ),
            NewsArticle(
                title="Santiago implementa nuevo sistema de transporte público",
                description="La capital chilena estrena moderno sistema de buses eléctricos que reducirá las emisiones de CO2 en un 40% durante el próximo año.",
                url="https://example.com/noticia-santiago-transporte",
                image_url="https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=400&h=200&fit=crop&crop=center",
                published_at="2024-09-16T09:30:00Z",
                source_name="Metro Chile",
                author="Patricia Silva"
            ),
            NewsArticle(
                title="Chile lidera innovación en energía solar en Latinoamérica",
                description="El país se posiciona como referente regional en energías renovables con la inauguración de tres nuevos parques solares en el norte.",
                url="https://example.com/noticia-energia-solar",
                image_url="https://images.unsplash.com/photo-1466611653911-95081537e5b7?w=400&h=200&fit=crop&crop=center",
                published_at="2024-09-16T08:45:00Z",
                source_name="Energía Chile",
                author="Roberto Mendoza"
            ),
            NewsArticle(
                title="Valparaíso celebra festival internacional de arte urbano",
                description="Artistas de todo el mundo se reúnen en el puerto para crear murales que celebran la diversidad cultural y la historia local.",
                url="https://example.com/noticia-valparaiso-arte",
                image_url="https://images.unsplash.com/photo-1541961017774-22349e4a1262?w=400&h=200&fit=crop&crop=center",
                published_at="2024-09-16T07:20:00Z",
                source_name="Cultura Valparaíso",
                author="Carmen Reyes"
            ),
            NewsArticle(
                title="Universidad de Chile desarrolla vacuna contra virus respiratorios",
                description="Investigadores chilenos logran avance significativo en el desarrollo de inmunización preventiva para enfermedades respiratorias comunes.",
                url="https://example.com/noticia-universidad-vacuna",
                image_url="https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=400&h=200&fit=crop&crop=center",
                published_at="2024-09-16T06:15:00Z",
                source_name="Ciencia Chile",
                author="Dr. Luis Herrera"
            ),
            NewsArticle(
                title="Chile avanza en energías renovables con nuevo parque solar",
                description="Se inaugura el parque solar más grande del norte del país, que abastecerá a más de 100.000 hogares con energía limpia.",
                url="https://example.com/noticia2",
                image_url="https://images.unsplash.com/photo-1509391366360-2e959784a276?w=400&h=200&fit=crop&crop=center",
                published_at="2024-09-16T08:30:00Z",
                source_name="EcoNoticias",
                author="María González"
            ),
            NewsArticle(
                title="Temporada turística de verano promete ser exitosa",
                description="Las reservas hoteleras aumentan un 25% respecto al año anterior, especialmente en destinos de playa y montaña.",
                url="https://example.com/noticia3",
                image_url="https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&h=200&fit=crop&crop=center",
                published_at="2024-09-16T07:15:00Z",
                source_name="Turismo Nacional",
                author="Carlos Mendoza"
            ),
            NewsArticle(
                title="Innovación tecnológica en la educación chilena",
                description="Nuevas plataformas digitales transforman la experiencia educativa en colegios y universidades del país.",
                url="https://example.com/noticia4",
                image_url="https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=400&h=200&fit=crop&crop=center",
                published_at="2024-09-16T06:00:00Z",
                source_name="Educación Hoy",
                author="Ana Rodríguez"
            ),
            NewsArticle(
                title="Deportes: Chile se prepara para competencias internacionales",
                description="Atletas nacionales intensifican entrenamientos para próximos campeonatos sudamericanos y mundiales.",
                url="https://example.com/noticia5",
                image_url="https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=200&fit=crop&crop=center",
                published_at="2024-09-16T05:45:00Z",
                source_name="Deportes Nacional",
                author="Luis Hernández"
            )
        ]
        
        return fallback_articles[:limit]
