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

    this.newsService.getChileNews(limit)
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
          console.error('Error cargando noticias:', error);
        }
      });
  }

  /**
   * Actualiza la cantidad de noticias a mostrar
   */
  updateLimit(newLimit: number): void {
    if (newLimit >= 1 && newLimit <= 50) {
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
      // En lugar de ocultar, mostrar una imagen de fallback
      target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDQwMCAyMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSI0MDAiIGhlaWdodD0iMjAwIiBmaWxsPSIjRjNGNEY2Ii8+CjxwYXRoIGQ9Ik0xNzUgNzVIMjI1VjEyNUgxNzVWNzVaIiBmaWxsPSIjOUI1OUI2Ii8+CjxwYXRoIGQ9Ik0xOTUgOTVMMjA1IDEwNUwyMTUgOTVMMjI1IDEwNVYxMjVIMTc1VjEwNUwxODUgOTVMMTk1IDk1WiIgZmlsbD0iIzlCNTlCNiIvPgo8L3N2Zz4K';
      target.alt = 'Imagen no disponible';
      target.style.opacity = '0.7';
      
      // Marcar como cargada (aunque con error)
      const originalSrc = target.getAttribute('data-original-src');
      if (originalSrc) {
        this.imageLoadingStates[originalSrc] = false;
      }
    }
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
}
