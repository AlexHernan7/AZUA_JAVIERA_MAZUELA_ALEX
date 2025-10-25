import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { NewsService } from '../../services/news.service';
import { NewsArticle, NewsResponse } from '../../interfaces/news.interface';

@Component({
  selector: 'app-news',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './news.component.html',
  styleUrl: './news.component.css',
})
export class NewsComponent implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>();

  // Estado del componente
  articles: NewsArticle[] = [];
  loading = false;
  error: string | null = null;
  totalResults = 0;
  limit = 10;
  // Nuevo: Seguimiento de tipos de imagen
  imageTypes: { [url: string]: 'real' | 'placeholder' } = {};
  imageLoadingStates: { [url: string]: boolean } = {};

  constructor(private newsService: NewsService) {}

  ngOnInit(): void {
    this.loadNews();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  /**
   * Carga las noticias desde la API
   */
  loadNews(limit: number = this.limit): void {
    this.loading = true;
    this.error = null;

    this.newsService.getMaipuNews(limit)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response: NewsResponse) => {
          this.articles = response.articles;
          this.totalResults = response.total_results;
          this.loading = false;
          
          // Inicializar estados de carga de imágenes
          this.articles.forEach(article => {
            if (article.image_url) {
              this.imageLoadingStates[article.image_url] = true;
            }
          });
        },
        error: (error: Error) => {
          this.error = error.message;
          this.loading = false;
        }
      });
  }

  /**
   * Actualiza la cantidad de noticias a mostrar
   */
  updateLimit(newLimit: number): void {
    // Validar nuevo límite según las restricciones del RSS (1-20)
    if (newLimit >= 1 && newLimit <= 20) {
      this.limit = newLimit;
      this.loadNews(newLimit);
    }
  }

  /**
   * Refresca las noticias
   */
  refreshNews(): void {
    this.loadNews(this.limit);
  }

  /**
   * Formatea la fecha de publicación
   */
  formatDate(dateString: string | undefined): string {
    if (!dateString) return 'Fecha no disponible';
    
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('es-CL', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return 'Fecha no válida';
    }
  }

  /**
   * Abre el artículo en una nueva pestaña
   */
  openArticle(url: string): void {
    window.open(url, '_blank');
  }

  /**
   * Función de tracking para ngFor para mejorar performance
   */
  trackByUrl(index: number, article: NewsArticle): string {
    return article.url;
  }

  /**
   * Maneja el cambio en el selector de límite
   */
  onLimitChange(event: Event): void {
    const target = event.target as HTMLSelectElement;
    if (target && target.value) {
      this.updateLimit(+target.value);
    }
  }

  /**
   * Maneja el error de carga de imagen
   */
  onImageError(event: Event): void {
    const target = event.target as HTMLImageElement;
    if (target) {
      const originalSrc = target.getAttribute('data-original-src') || target.src;
      
      // Si es una imagen placeholder que falló, usar un fallback específico
      if (originalSrc && this.isPlaceholderImage(originalSrc)) {
        // Para placeholders, usar un SVG específico del tipo
        const type = this.getPlaceholderType(originalSrc);
        target.src = this.getPlaceholderFallback(type);
      } else {
        // Para imágenes reales, usar el fallback genérico
        target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDQwMCAyMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSI0MDAiIGhlaWdodD0iMjAwIiBmaWxsPSIjRjNGNEY2Ii8+CjxwYXRoIGQ9Ik0xNzUgNzVIMjI1VjEyNUgxNzVWNzVaIiBmaWxsPSIjOUI1OUI2Ii8+CjxwYXRoIGQ9Ik0xOTUgOTVMMjA1IDEwNUwyMTUgOTVMMjI1IDEwNVYxMjVIMTc1VjEwNUwxODUgOTVMMTk1IDk1WiIgZmlsbD0iIzlCNTlCNiIvPgo8L3N2Zz4K';
      }
      
      target.alt = 'Imagen no disponible';
      target.style.opacity = '0.7';
      
      // Marcar como cargada (aunque con error)
      if (originalSrc) {
        this.imageLoadingStates[originalSrc] = false;
      }
    }
  }

  /**
   * Obtiene un SVG de fallback específico para cada tipo de placeholder
   */
  private getPlaceholderFallback(type: string): string {
    const fallbacks = {
      'político': 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDQwMCAyMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSI0MDAiIGhlaWdodD0iMjAwIiBmaWxsPSIjRUZGNkZGIi8+CjxjaXJjbGUgY3g9IjIwMCIgY3k9IjEwMCIgcj0iNDAiIGZpbGw9IiM2MzY2RjEiLz4KPHRleHQgeD0iMjAwIiB5PSIxNTAiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZpbGw9IiM2MzY2RjEiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNCIgZm9udC13ZWlnaHQ9ImJvbGQiPlBvbMOtdGljYTwvdGV4dD4KPHN2Zz4=',
      'municipal': 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDQwMCAyMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSI0MDAiIGhlaWdodD0iMjAwIiBmaWxsPSIjRkVGM0MyIi8+CjxyZWN0IHg9IjE2MCIgeT0iNjAiIHdpZHRoPSI4MCIgaGVpZ2h0PSI4MCIgZmlsbD0iI0Y1OTUwOSIvPgo8dGV4dCB4PSIyMDAiIHk9IjE2MCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZmlsbD0iI0Y1OTUwOSIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjE0IiBmb250LXdlaWdodD0iYm9sZCI+TXVuaWNpcGFsPC90ZXh0Pgo8L3N2Zz4=',
      'judicial': 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDQwMCAyMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSI0MDAiIGhlaWdodD0iMjAwIiBmaWxsPSIjRjNFOEZGIi8+CjxwYXRoIGQ9Ik0xODAgODBMMjAwIDYwTDIyMCA4MEwyMDAgMTAwWiIgZmlsbD0iIzk0NEE0QyIvPgo8cmVjdCB4PSIxOTUiIHk9IjEwMCIgd2lkdGg9IjEwIiBoZWlnaHQ9IjQwIiBmaWxsPSIjOTQ0QTRDIi8+Cjx0ZXh0IHg9IjIwMCIgeT0iMTYwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWxsPSIjOTQ0QTRDIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTQiIGZvbnQtd2VpZ2h0PSJib2xkIj5KdWRpY2lhbDwvdGV4dD4KPHN2Zz4='
    };
    
    return fallbacks[type as keyof typeof fallbacks] || fallbacks['político'];
  }

  /**
   * Maneja la carga exitosa de imagen
   */
  onImageLoad(event: Event): void {
    const target = event.target as HTMLImageElement;
    if (target) {
      const originalSrc = target.getAttribute('data-original-src') || target.src;
      this.imageLoadingStates[originalSrc] = false;
    }
  }

  /**
   * Maneja el clic en "Leer más"
   */
  onReadMore(event: Event, url: string): void {
    event.stopPropagation();
    this.openArticle(url);
  }

  /**
   * Determina si una imagen es un placeholder temático
   */
  isPlaceholderImage(imageUrl: string | undefined): boolean {
    return imageUrl ? imageUrl.includes('unsplash.com') : false;
  }

  /**
   * Obtiene el tipo de placeholder basado en la URL
   */
  getPlaceholderType(imageUrl: string): string {
    if (!imageUrl || !this.isPlaceholderImage(imageUrl)) {
      return '';
    }
    
    if (imageUrl.includes('photo-1529107386315')) {
      return 'político';
    } else if (imageUrl.includes('photo-1554224155')) {
      return 'municipal';
    } else if (imageUrl.includes('photo-1589829545856')) {
      return 'judicial';
    }
    return 'temático';
  }

  /**
   * Obtiene la clase CSS para el tipo de imagen
   */
  getImageTypeClass(imageUrl: string | undefined): string {
    if (!imageUrl) return '';
    
    if (this.isPlaceholderImage(imageUrl)) {
      const type = this.getPlaceholderType(imageUrl);
      return `image-placeholder image-${type}`;
    }
    
    return 'image-real';
  }
}
