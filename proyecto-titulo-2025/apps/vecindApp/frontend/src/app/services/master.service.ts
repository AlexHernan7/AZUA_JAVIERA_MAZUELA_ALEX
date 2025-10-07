import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse, HttpHeaders } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { AuthService } from './auth.service';

export interface MotivoSolicitudResponse {
  id_motivo: number;
  motivo: string;
  grupo: string;
  descripcion?: string;
  activo: boolean;
}

export interface MotivoGrupoResponse {
  grupo: string;
  items: MotivoSolicitudResponse[];
}

export interface MotivosAgrupadosResponse {
  grupos: MotivoGrupoResponse[];
  total: number;
}

export interface EstadoCertificadoResponse {
  id_estado: number;
  nombre_estado: string;
  descripcion?: string;
  activo: boolean;
}

export interface TipoEspacioResponse {
  id_tipo: number;
  tipo: string;
  descripcion?: string;
  activo: boolean;
}

export interface EstadoReservaResponse {
  id_estado: number;
  nombre_estado: string;
  descripcion?: string;
  activo: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class MasterService {
  private readonly API_URL = 'http://localhost:8000/api/master';

  constructor(private http: HttpClient, private authService: AuthService) {}

  /**
   * Obtiene todos los motivos de solicitud
   */
  getMotivosSolicitud(activo: boolean = true): Observable<MotivoSolicitudResponse[]> {
    const headers = this.getAuthHeaders();
    return this.http.get<MotivoSolicitudResponse[]>(`${this.API_URL}/motivos-solicitud?activo=${activo}`, { headers })
      .pipe(catchError(this.handleError));
  }

  /**
   * Obtiene motivos de solicitud agrupados por categoría
   */
  getMotivosSolicitudAgrupados(activo: boolean = true): Observable<MotivosAgrupadosResponse> {
    const headers = this.getAuthHeaders();
    return this.http.get<MotivosAgrupadosResponse>(`${this.API_URL}/motivos-solicitud-agrupados?activo=${activo}`, { headers })
      .pipe(catchError(this.handleError));
  }

  /**
   * Obtiene todos los estados de certificado
   */
  getEstadosCertificado(activo: boolean = true): Observable<EstadoCertificadoResponse[]> {
    const headers = this.getAuthHeaders();
    return this.http.get<EstadoCertificadoResponse[]>(`${this.API_URL}/estados-certificado?activo=${activo}`, { headers })
      .pipe(catchError(this.handleError));
  }

  /**
   * Obtiene todos los tipos de espacio
   */
  getTiposEspacio(activo: boolean = true): Observable<TipoEspacioResponse[]> {
    const headers = this.getAuthHeaders();
    return this.http.get<TipoEspacioResponse[]>(`${this.API_URL}/tipos-espacio?activo=${activo}`, { headers })
      .pipe(catchError(this.handleError));
  }

  /**
   * Obtiene todos los estados de reserva
   */
  getEstadosReserva(activo: boolean = true): Observable<EstadoReservaResponse[]> {
    const headers = this.getAuthHeaders();
    return this.http.get<EstadoReservaResponse[]>(`${this.API_URL}/estados-reserva?activo=${activo}`, { headers })
      .pipe(catchError(this.handleError));
  }

  /**
   * Obtiene headers de autenticación
   */
  private getAuthHeaders(): HttpHeaders {
    const token = this.authService.getToken();
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
  }

  /**
   * Manejo de errores HTTP
   */
  private handleError = (error: HttpErrorResponse): Observable<never> => {
    let errorMessage = 'Error desconocido';
    
    if (error.error instanceof ErrorEvent) {
      // Error del lado del cliente
      errorMessage = `Error: ${error.error.message}`;
    } else {
      // Error del servidor
      console.error('Error completo del servidor:', error);
      console.error('Status:', error.status);
      console.error('Error body:', error.error);
      
      if (error.error && typeof error.error === 'object') {
        const apiError = error.error as any;
        errorMessage = apiError.detail || apiError.error || `Error ${error.status}`;
      }
    }
    
    return throwError(() => new Error(errorMessage));
  };
}
