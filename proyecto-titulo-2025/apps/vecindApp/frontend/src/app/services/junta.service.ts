import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse, HttpHeaders } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { 
  JuntaCreateRequest, 
  JuntaCreateResponse, 
  JuntaResponse, 
  JuntasList,
  JuntaUpdateRequest,
  JuntaUpdateResponse,
  RegionsList,
  ComunasList,
  ApiError 
} from '../interfaces/junta.interface';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class JuntaService {
  private readonly API_URL = environment.apiUrl; // URL del backend desde environment

  constructor(private http: HttpClient) {}

  /**
   * Crea una nueva junta de vecinos
   */
  createJunta(juntaData: JuntaCreateRequest): Observable<JuntaCreateResponse> {
    const headers = this.getAuthHeaders();
    
    return this.http.post<JuntaCreateResponse>(`${this.API_URL}/juntas`, juntaData, { headers })
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Obtiene una junta por su ID
   */
  getJuntaById(juntaId: number): Observable<JuntaResponse> {
    return this.http.get<JuntaResponse>(`${this.API_URL}/juntas/${juntaId}`)
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Lista todas las juntas con filtros opcionales
   */
  listJuntas(params?: {
    skip?: number;
    limit?: number;
    activa?: boolean;
    comuna_id?: number;
  }): Observable<JuntasList> {
    let queryParams = '';
    
    if (params) {
      const searchParams = new URLSearchParams();
      if (params.skip !== undefined) searchParams.set('skip', params.skip.toString());
      if (params.limit !== undefined) searchParams.set('limit', params.limit.toString());
      if (params.activa !== undefined) searchParams.set('activa', params.activa.toString());
      if (params.comuna_id !== undefined) searchParams.set('comuna_id', params.comuna_id.toString());
      
      queryParams = searchParams.toString();
    }
    
    const url = queryParams ? `${this.API_URL}/juntas?${queryParams}` : `${this.API_URL}/juntas`;
    
    return this.http.get<JuntasList>(url)
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Obtiene juntas por comuna
   */
  getJuntasByComuna(comunaId: number): Observable<JuntaResponse[]> {
    return this.http.get<JuntaResponse[]>(`${this.API_URL}/juntas/comuna/${comunaId}`)
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Actualiza los datos de una junta (solo para usuarios directiva)
   */
  updateJunta(juntaId: number, updateData: JuntaUpdateRequest): Observable<JuntaUpdateResponse> {
    const headers = this.getAuthHeaders();
    
    return this.http.patch<JuntaUpdateResponse>(`${this.API_URL}/juntas/${juntaId}`, updateData, { headers })
      .pipe(
        catchError(this.handleError)
      );
  }


  /**
   * Obtiene todas las comunas con sus IDs desde el backend
   */
  getAllComunas(): Observable<ComunasList> {
    return this.http.get<ComunasList>(`${this.API_URL}/auth/comunas`)
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Busca el ID de una comuna por su nombre
   */
  getComunaIdByName(nombreComuna: string): Observable<number | null> {
    return this.getAllComunas().pipe(
      catchError(this.handleError),
      map(response => {
        const comuna = response.comunas.find(c => 
          c.nombre.toLowerCase() === nombreComuna.toLowerCase()
        );
        return comuna ? comuna.id_comuna : null;
      })
    );
  }

  /**
   * Obtiene headers de autenticación
   */
  private getAuthHeaders(): HttpHeaders {
    const token = localStorage.getItem('vecindapp_token');
    
    if (!token) {
      throw new Error('Token de autenticación no encontrado');
    }
    
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
  }

  /**
   * Maneja errores de HTTP
   */
  private handleError = (error: HttpErrorResponse): Observable<never> => {
    let errorMessage = 'Error desconocido';
    let errorDetails = '';

    if (error.error instanceof ErrorEvent) {
      // Error del lado del cliente
      errorMessage = 'Error de conexión';
      errorDetails = error.error.message;
    } else {
      // Error del servidor
      if (error.error && typeof error.error === 'object') {
        const apiError = error.error as ApiError;
        errorMessage = apiError.error || 'Error del servidor';
        errorDetails = apiError.detalle || '';
      } else if (typeof error.error === 'string') {
        errorMessage = error.error;
      } else {
        switch (error.status) {
          case 400:
            errorMessage = 'Datos inválidos';
            break;
          case 401:
            errorMessage = 'No autorizado. Inicia sesión nuevamente.';
            break;
          case 403:
            errorMessage = 'No tienes permisos para realizar esta acción';
            break;
          case 404:
            errorMessage = 'Recurso no encontrado';
            break;
          case 409:
            errorMessage = 'Conflicto de datos. El registro ya existe.';
            break;
          case 500:
            errorMessage = 'Error interno del servidor';
            break;
          default:
            errorMessage = `Error ${error.status}: ${error.statusText}`;
        }
      }
    }
    return throwError(() => ({
      message: errorMessage,
      details: errorDetails,
      status: error.status
    }));
  };
}
