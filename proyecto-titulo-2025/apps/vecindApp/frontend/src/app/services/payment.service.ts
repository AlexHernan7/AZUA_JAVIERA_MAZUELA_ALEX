import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse, HttpHeaders } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { 
  PaymentIntentResponse,
  PaymentStatusResponse,
  PaymentErrorResponse
} from '../interfaces/payment.interface';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class PaymentService {
  private readonly API_URL = 'http://localhost:8000/api/payments';

  constructor(private http: HttpClient, private authService: AuthService) {}

  /**
   * Obtiene headers con autorización
   */
  private getAuthHeaders(): HttpHeaders {
    const token = this.authService.getToken();
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
  }

  /**
   * Consulta el estado de un pago
   */
  getPaymentStatus(paymentIntentId: number): Observable<PaymentStatusResponse> {
    const headers = this.getAuthHeaders();
    return this.http.get<PaymentStatusResponse>(`${this.API_URL}/status/${paymentIntentId}`, { headers })
      .pipe(catchError(this.handleError));
  }

  /**
   * Reintenta un pago fallido
   */
  retryPayment(paymentIntentId: number): Observable<PaymentIntentResponse> {
    const headers = this.getAuthHeaders();
    const body = { payment_intent_id: paymentIntentId };
    return this.http.post<PaymentIntentResponse>(`${this.API_URL}/retry`, body, { headers })
      .pipe(catchError(this.handleError));
  }

  /**
   * Obtiene mis pagos
   */
  getMyPayments(entityType?: string, limit: number = 10): Observable<PaymentIntentResponse[]> {
    const headers = this.getAuthHeaders();
    let url = `${this.API_URL}/my-payments?limit=${limit}`;
    if (entityType) {
      url += `&entity_type=${entityType}`;
    }
    return this.http.get<PaymentIntentResponse[]>(url, { headers })
      .pipe(catchError(this.handleError));
  }

  /**
   * Cancela un pago pendiente
   */
  cancelPayment(paymentIntentId: number): Observable<{message: string}> {
    const headers = this.getAuthHeaders();
    return this.http.post<{message: string}>(`${this.API_URL}/cancel/${paymentIntentId}`, {}, { headers })
      .pipe(catchError(this.handleError));
  }

  /**
   * Manejo de errores HTTP
   */
  private handleError = (error: HttpErrorResponse): Observable<never> => {
    
    let errorMessage = 'Error desconocido en el sistema de pagos';
    
    if (error.error) {
      if (error.error.detail) {
        errorMessage = error.error.detail;
      } else if (error.error.error) {
        errorMessage = error.error.error;
      } else if (typeof error.error === 'string') {
        errorMessage = error.error;
      }
    } else if (error.message) {
      errorMessage = error.message;
    }
    
    return throwError(() => ({
      message: errorMessage,
      status: error.status,
      error: error.error
    }));
  };
}
