import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse, HttpHeaders } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { 
  CertificadoPedidoCreate,
  CertificadoPedidoResponse,
  CertificadoConfirmacionData,
  CertificadoGenerateRequest,
  CertificadoResponse,
  CertificadoApiError
} from '../interfaces/certificado.interface';
import { CertificadoConPagoResponse } from '../interfaces/payment.interface';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class CertificadoService {
  private readonly API_URL = 'http://localhost:8000/api/certificados';

  constructor(private http: HttpClient, private authService: AuthService) {}

  /**
   * Obtiene los datos del vecino para confirmación antes de solicitar certificado
   */
  getDatosConfirmacion(): Observable<CertificadoConfirmacionData> {
    const headers = this.getAuthHeaders();
    return this.http.get<CertificadoConfirmacionData>(`${this.API_URL}/confirmacion-datos`, { headers })
      .pipe(catchError(this.handleError));
  }

  /**
   * Crea una nueva solicitud de certificado
   */
  solicitarCertificado(request: CertificadoPedidoCreate): Observable<CertificadoPedidoResponse> {
    const headers = this.getAuthHeaders();
    return this.http.post<CertificadoPedidoResponse>(`${this.API_URL}/solicitar`, request, { headers })
      .pipe(catchError(this.handleError));
  }

  /**
   * Genera el certificado PDF después de confirmar los datos
   */
  generarCertificado(request: CertificadoGenerateRequest): Observable<CertificadoResponse> {
    const headers = this.getAuthHeaders();
    return this.http.post<CertificadoResponse>(`${this.API_URL}/generar`, request, { headers })
      .pipe(catchError(this.handleError));
  }

  /**
   * NUEVO: Solicita certificado con pago MercadoPago
   */
  solicitarCertificadoConPago(request: CertificadoPedidoCreate): Observable<CertificadoConPagoResponse> {
    const headers = this.getAuthHeaders();
    return this.http.post<CertificadoConPagoResponse>(`${this.API_URL}/solicitar-con-pago`, request, { headers })
      .pipe(catchError(this.handleError));
  }

  /**
   * NUEVO: Solicita certificado con pago Webpay
   */
  solicitarCertificadoConWebpay(request: CertificadoPedidoCreate): Observable<CertificadoConPagoResponse> {
    const headers = this.getAuthHeaders();
    return this.http.post<CertificadoConPagoResponse>(`${this.API_URL}/webpay-payment`, request, { headers })
      .pipe(catchError(this.handleError));
  }

  /**
   * Obtiene todos los certificados del usuario autenticado
   */
  getMisCertificados(): Observable<CertificadoResponse[]> {
    const headers = this.getAuthHeaders();
    return this.http.get<CertificadoResponse[]>(`${this.API_URL}/mis-certificados`, { headers })
      .pipe(catchError(this.handleError));
  }

  /**
   * Descarga el PDF de un certificado específico
   */
  descargarCertificadoPDF(certificadoId: number): Observable<Blob> {
    const headers = this.getAuthHeaders();
    return this.http.get(`${this.API_URL}/${certificadoId}/descargar`, { 
      headers, 
      responseType: 'blob' 
    }).pipe(catchError(this.handleError));
  }

  /**
   * Obtiene los headers de autenticación
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
      
      if (error.error && typeof error.error === 'object') {
        const apiError = error.error as any;
        
        // Para errores 422 de validación, mostrar más detalles
        if (error.status === 422 && apiError.detail) {
          if (Array.isArray(apiError.detail)) {
            // Errores de validación de Pydantic
            const validationErrors = apiError.detail.map((err: any) => 
              `${err.loc?.join('.')} - ${err.msg}`
            ).join('; ');
            errorMessage = `Error de validación: ${validationErrors}`;
          } else if (typeof apiError.detail === 'string') {
            errorMessage = `Error de validación: ${apiError.detail}`;
          } else {
            errorMessage = apiError.detalle || apiError.error || 'Error de validación';
          }
        } else if (error.status === 400) {
          // Errores 400 - Bad Request
          errorMessage = apiError.detalle || apiError.error || 'Solicitud inválida';
        } else if (error.status === 401) {
          // Error de autenticación
          errorMessage = 'No autorizado. Por favor, inicia sesión nuevamente.';
        } else if (error.status === 404) {
          // No encontrado
          errorMessage = apiError.detalle || apiError.error || 'Recurso no encontrado';
        } else if (error.status === 409) {
          // Conflicto (ej: certificado ya existe)
          errorMessage = apiError.detalle || apiError.error || 'Conflicto en la solicitud';
        } else if (error.status === 500) {
          // Error interno del servidor
          errorMessage = 'Error interno del servidor. Intenta nuevamente más tarde.';
        } else {
          // Otros errores
          errorMessage = apiError.detalle || apiError.error || `Error ${error.status}`;
        }
      } else {
        errorMessage = `Error ${error.status}: ${error.message}`;
      }
    }
    
    return throwError(() => new Error(errorMessage));
  };

  /**
   * Utilidad para descargar un archivo blob
   */
  downloadBlob(blob: Blob, filename: string): void {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  }
}
