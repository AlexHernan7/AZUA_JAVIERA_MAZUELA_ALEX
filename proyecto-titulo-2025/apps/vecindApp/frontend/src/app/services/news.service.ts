import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse, HttpParams } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { NewsResponse, NewsErrorResponse, NewsHealthCheck } from '../interfaces/news.interface';

@Injectable({
  providedIn: 'root'
})
export class NewsService {
  private readonly API_URL = 'http://localhost:8000/api'; // URL base del backend

  constructor(private http: HttpClient) {}

  /**
   * Obtiene las noticias de Chile
   * @param limit Número de noticias a obtener (1-50, por defecto 10)
   */
  getChileNews(limit: number = 10): Observable<NewsResponse> {
    const params = new HttpParams().set('limit', limit.toString());
    
    return this.http.get<NewsResponse>(`${this.API_URL}/news/chile`, { params })
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Verifica el estado del servicio de noticias
   */
  checkNewsHealth(): Observable<NewsHealthCheck> {
    return this.http.get<NewsHealthCheck>(`${this.API_URL}/news/health`)
      .pipe(
        catchError(this.handleError)
      );
  }

  private handleError = (error: HttpErrorResponse): Observable<never> => {
    let errorMessage = 'Error desconocido al obtener noticias';
    
    if (error.error instanceof ErrorEvent) {
      // Error del lado del cliente
      errorMessage = `Error de conexión: ${error.error.message}`;
    } else {
      // Error del servidor
      console.error('Error completo del servidor:', error);
      console.error('Status:', error.status);
      console.error('Error body:', error.error);
      
      if (error.error && typeof error.error === 'object') {
        const apiError = error.error as any;
        
        if (error.status === 503) {
          errorMessage = 'Servicio de noticias no disponible temporalmente';
        } else if (error.status === 422 && apiError.detail) {
          errorMessage = 'Parámetros inválidos para obtener noticias';
        } else if (apiError.message) {
          errorMessage = apiError.message;
        } else {
          errorMessage = `Error ${error.status}: No se pudieron obtener las noticias`;
        }
      } else {
        errorMessage = `Error ${error.status}: ${error.message}`;
      }
    }

    console.error('Error en NewsService:', errorMessage);
    return throwError(() => new Error(errorMessage));
  };
}
