import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse, HttpHeaders } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { 
  ReservaCreateRequest, 
  ReservaResponse, 
  ReservaListResponse,
  DisponibilidadRequest,
  DisponibilidadResponse,
  ApiError 
} from '../interfaces/reserva.interface';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class ReservaService {
  private readonly API_URL = 'http://localhost:8000/api';

  constructor(private http: HttpClient, private authService: AuthService) {}

  /**
   * Crea una nueva reserva de espacio
   */
  createReserva(reservaData: ReservaCreateRequest): Observable<ReservaResponse> {
    const headers = this.getAuthHeaders();
    
    return this.http.post<ReservaResponse>(`${this.API_URL}/reservas/`, reservaData, { headers })
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Verifica la disponibilidad de un espacio
   */
  verificarDisponibilidad(disponibilidadData: DisponibilidadRequest): Observable<DisponibilidadResponse> {
    return this.http.post<DisponibilidadResponse>(`${this.API_URL}/reservas/verificar-disponibilidad`, disponibilidadData)
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Obtiene una reserva por ID
   */
  getReservaById(id: number): Observable<ReservaResponse> {
    const headers = this.getAuthHeaders();
    
    return this.http.get<ReservaResponse>(`${this.API_URL}/reservas/${id}`, { headers })
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Obtiene las reservas de un espacio específico
   */
  getReservasByEspacio(
    idEspacio: number,
    fechaDesde?: string,
    fechaHasta?: string,
    pagina: number = 1,
    porPagina: number = 10
  ): Observable<ReservaListResponse> {
    let params = new URLSearchParams({
      pagina: pagina.toString(),
      por_pagina: porPagina.toString()
    });

    if (fechaDesde) {
      params.append('fecha_desde', fechaDesde);
    }
    if (fechaHasta) {
      params.append('fecha_hasta', fechaHasta);
    }

    return this.http.get<ReservaListResponse>(`${this.API_URL}/reservas/espacio/${idEspacio}?${params}`)
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Actualiza una reserva existente
   */
  updateReserva(id: number, reservaData: Partial<ReservaCreateRequest>): Observable<ReservaResponse> {
    const headers = this.getAuthHeaders();
    
    return this.http.put<ReservaResponse>(`${this.API_URL}/reservas/${id}`, reservaData, { headers })
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Obtiene headers de autenticación
   */
  private getAuthHeaders(): HttpHeaders {
    const token = this.authService.getToken();
    
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
    
    if (error.error instanceof ErrorEvent) {
      // Error del lado del cliente
      errorMessage = `Error: ${error.error.message}`;
    } else {
      // Error del lado del servidor
      if (error.error && error.error.detail) {
        errorMessage = error.error.detail;
      } else if (error.error && error.error.message) {
        errorMessage = error.error.message;
      } else if (error.status === 0) {
        errorMessage = 'No se pudo conectar con el servidor';
      } else {
        errorMessage = `Error del servidor: ${error.status} - ${error.statusText}`;
      }
    }
    
    return throwError(() => new Error(errorMessage));
  };
}
