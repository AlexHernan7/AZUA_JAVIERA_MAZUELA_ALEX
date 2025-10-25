import { Injectable } from '@angular/core';
import { HttpClient, HttpParams, HttpHeaders } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface KPI {
  label: string;
  value: number;
  prefix?: string;
  suffix?: string;
}

export interface IngresoMensual {
  mes: string;
  ingresos: number;
}

export interface DistribucionReserva {
  espacio: string;
  cantidad: number;
}

export interface CertificadoMensual {
  mes: string;
  cantidad: number;
}

export interface EspacioStats {
  nombre: string;
  total_reservas: number;
  ingresos: number;
}

export interface Periodo {
  fecha_desde: string;
  fecha_hasta: string;
}

export interface DashboardResponse {
  kpis: KPI[];
  ingresos_mensuales: IngresoMensual[];
  certificados_mensuales: CertificadoMensual[];
  distribucion_reservas: DistribucionReserva[];
  resumen_espacios: EspacioStats[];
  periodo: Periodo;
}

export interface EstadisticasDetalladasResponse {
  total_espacios: number;
  total_certificados: number;
  total_ingresos: number;
  ingresos_certificados: number;
  ingresos_reservas: number;
  total_usuarios: number;
  total_vecinos: number;
  total_directivos: number;
  total_reservas: number;
  espacios_stats: EspacioStats[];
  ingresos_mensuales: IngresoMensual[];
  periodo: Periodo;
}

@Injectable({
  providedIn: 'root'
})
export class ReporteService {
  private readonly API_URL = `${environment.apiUrl}/reportes`;

  constructor(private http: HttpClient) {}

  /**
   * Obtiene el dashboard completo de reportes
   */
  getDashboard(
    fechaDesde?: string,
    fechaHasta?: string,
    meses?: string[]
  ): Observable<DashboardResponse> {
    let params = new HttpParams();
    
    if (fechaDesde) {
      params = params.set('fecha_desde', fechaDesde);
    }
    
    if (fechaHasta) {
      params = params.set('fecha_hasta', fechaHasta);
    }
    
    if (meses && meses.length > 0) {
      params = params.set('meses', meses.join(','));
    }

    const headers = this.getAuthHeaders();

    return this.http.get<DashboardResponse>(`${this.API_URL}/dashboard`, { 
      params, 
      headers 
    }).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Obtiene estadísticas detalladas
   */
  getEstadisticasDetalladas(
    fechaDesde?: string,
    fechaHasta?: string
  ): Observable<EstadisticasDetalladasResponse> {
    let params = new HttpParams();
    
    if (fechaDesde) {
      params = params.set('fecha_desde', fechaDesde);
    }
    
    if (fechaHasta) {
      params = params.set('fecha_hasta', fechaHasta);
    }

    const headers = this.getAuthHeaders();

    return this.http.get<EstadisticasDetalladasResponse>(`${this.API_URL}/estadisticas`, { 
      params, 
      headers 
    }).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Obtiene headers de autenticación
   */
  private getAuthHeaders(): HttpHeaders {
    const token = localStorage.getItem('vecindapp_token');
    
    if (!token) {
      throw new Error('Token de autorización no encontrado');
    }
    
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
  }

  /**
   * Maneja errores HTTP
   */
  private handleError(error: any): Observable<never> {
    return throwError(() => error);
  }
}
