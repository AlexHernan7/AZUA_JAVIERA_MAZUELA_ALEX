import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse, HttpHeaders } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { 
  EspacioCreateRequest, 
  EspacioResponse, 
  EspacioListResponse,
  ApiError 
} from '../interfaces/espacio.interface';

@Injectable({
  providedIn: 'root'
})
export class EspacioService {
  private readonly API_URL = 'http://localhost:8000/api'; // URL base del backend

  constructor(private http: HttpClient) {}

  /**
   * Crea un nuevo espacio comunitario
   */
  createEspacio(espacioData: EspacioCreateRequest): Observable<EspacioResponse> {
    const headers = this.getAuthHeaders();
    
    return this.http.post<EspacioResponse>(`${this.API_URL}/espacios/`, espacioData, { headers })
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Crea un nuevo espacio comunitario con archivo
   */
  createEspacioWithFile(espacioData: EspacioCreateRequest, file: File): Observable<EspacioResponse> {
    const formData = new FormData();
    
    // Agregar todos los campos del espacio al FormData
    formData.append('nombre', espacioData.nombre);
    formData.append('tipo', espacioData.tipo);
    formData.append('capacidad', espacioData.capacidad.toString());
    formData.append('valor', espacioData.valor.toString());
    formData.append('max_horas', espacioData.max_horas.toString());
    formData.append('activo', espacioData.activo.toString());
    formData.append('id_junta', espacioData.id_junta.toString());
    
    // Agregar arrays si existen
    if (espacioData.permitido && espacioData.permitido.length > 0) {
      espacioData.permitido.forEach(item => formData.append('permitido', item));
    }
    
    if (espacioData.no_permitido && espacioData.no_permitido.length > 0) {
      espacioData.no_permitido.forEach(item => formData.append('no_permitido', item));
    }
    
    // Agregar el archivo
    formData.append('foto', file, file.name);
    
    const headers = this.getAuthHeadersForFile();
    
    return this.http.post<EspacioResponse>(`${this.API_URL}/espacios/`, formData, { headers })
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Obtiene un espacio por su ID
   */
  getEspacioById(id: number): Observable<EspacioResponse> {
    return this.http.get<EspacioResponse>(`${this.API_URL}/espacios/${id}`)
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Obtiene todos los espacios de una junta
   */
  getEspaciosByJunta(
    idJunta: number, 
    activoOnly: boolean = true,
    pagina: number = 1,
    porPagina: number = 10
  ): Observable<EspacioListResponse> {
    const params = new URLSearchParams({
      activo_only: activoOnly.toString(),
      pagina: pagina.toString(),
      por_pagina: porPagina.toString()
    });

    return this.http.get<EspacioListResponse>(`${this.API_URL}/espacios/junta/${idJunta}?${params}`)
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Actualiza un espacio existente
   */
  updateEspacio(id: number, espacioData: Partial<EspacioCreateRequest>): Observable<EspacioResponse> {
    const headers = this.getAuthHeaders();
    
    return this.http.put<EspacioResponse>(`${this.API_URL}/espacios/${id}`, espacioData, { headers })
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Elimina un espacio (soft delete)
   */
  deleteEspacio(id: number): Observable<void> {
    const headers = this.getAuthHeaders();
    
    return this.http.delete<void>(`${this.API_URL}/espacios/${id}`, { headers })
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Obtiene los headers de autenticación
   */
  private getAuthHeaders(): HttpHeaders {
    const token = localStorage.getItem('token');
    return new HttpHeaders({
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    });
  }

  /**
   * Obtiene los headers de autenticación para archivos (sin Content-Type)
   */
  private getAuthHeadersForFile(): HttpHeaders {
    const token = localStorage.getItem('token');
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });
  }

  /**
   * Maneja errores HTTP
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
      } else {
        errorMessage = `Error ${error.status}: ${error.statusText}`;
      }
    }
    
    console.error('Error en EspacioService:', errorMessage);
    return throwError(() => new Error(errorMessage));
  };
}
