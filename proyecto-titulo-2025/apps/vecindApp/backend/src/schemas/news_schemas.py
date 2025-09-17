"""
Esquemas para el manejo de noticias.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class NewsArticle(BaseModel):
    """Esquema para un artículo de noticia individual."""
    
    title: str = Field(..., description="Título del artículo")
    description: Optional[str] = Field(None, description="Descripción breve del artículo")
    url: str = Field(..., description="URL del artículo original")
    image_url: Optional[str] = Field(None, description="URL de la imagen principal")
    published_at: Optional[str] = Field(None, description="Fecha de publicación")
    source_name: Optional[str] = Field(None, description="Nombre de la fuente")
    author: Optional[str] = Field(None, description="Autor del artículo")


class NewsResponse(BaseModel):
    """Respuesta para el endpoint de noticias."""
    
    articles: List[NewsArticle] = Field(..., description="Lista de artículos")
    total_results: int = Field(..., description="Número total de resultados")
    status: str = Field("success", description="Estado de la respuesta")
    message: str = Field("Noticias obtenidas correctamente", description="Mensaje informativo")


class NewsErrorResponse(BaseModel):
    """Respuesta de error para el endpoint de noticias."""
    
    status: str = Field("error", description="Estado de error")
    message: str = Field(..., description="Mensaje de error")
