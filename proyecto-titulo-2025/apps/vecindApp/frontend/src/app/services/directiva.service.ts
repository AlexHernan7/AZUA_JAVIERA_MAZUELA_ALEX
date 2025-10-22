import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse, HttpHeaders } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { 
  DirectivaRegistroRequest, 
  DirectivaRegistroResponse, 
  DirectivaResponse,
  DirectivaFormData,
  DirectivaApiError 
} from '../interfaces/directiva.interface';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class DirectivaService {
  private readonly API_URL = 'http://localhost:8000/api'; // URL base del backend

  constructor(private http: HttpClient, private authService: AuthService) {}

  /**
   * Registra un nuevo directivo (Solo Admin)
   */
  registerDirectivo(directivaData: DirectivaFormData, idJunta: number): Observable<DirectivaRegistroResponse> {
    // Obtener token de autorización
    const token = this.authService.getToken();
    if (!token) {
      return throwError(() => new Error('Token de autorización requerido'));
    }

    // Configurar headers con autorización
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });

    // Convertir los datos del formulario al formato esperado por la API
    const apiRequest: DirectivaRegistroRequest = {
      rut: directivaData.rut,
      nombres: directivaData.nombres,
      apellido_paterno: directivaData.apellido_paterno,
      apellido_materno: directivaData.apellido_materno || undefined,
      telefono: directivaData.telefono,
      email: directivaData.email,
      cargo: directivaData.cargo.toLowerCase(), // El backend espera minúsculas
      fecha_inicio_cargo: directivaData.fecha_inicio || new Date().toISOString().split('T')[0], // Fecha actual si no se especifica
      fecha_termino_cargo: directivaData.fecha_termino || undefined,
      id_junta: idJunta,
      password: directivaData.password,
      confirm_password: directivaData.password, // Confirmación igual a la contraseña
      foto_perfil: directivaData.foto_perfil || undefined
    };

    return this.http.post<DirectivaRegistroResponse>(`${this.API_URL}/directiva/register`, apiRequest, { headers })
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Obtiene los directivos de una junta específica
   */
  getDirectivosByJunta(juntaId: number, activosOnly: boolean = false): Observable<DirectivaResponse[]> {
    const params = activosOnly ? '?activos_only=true' : '';
    return this.http.get<DirectivaResponse[]>(`${this.API_URL}/directiva/junta/${juntaId}${params}`)
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Obtiene los directivos de la junta del usuario autenticado
   */
  getMyJuntaDirectivos(activosOnly: boolean = false): Observable<DirectivaResponse[]> {
    // Obtener token de autorización
    const token = this.authService.getToken();
    if (!token) {
      return throwError(() => new Error('Token de autorización requerido'));
    }

    // Configurar headers con autorización
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });

    const params = activosOnly ? '?activos_only=true' : '';
    return this.http.get<DirectivaResponse[]>(`${this.API_URL}/directiva/mi-junta${params}`, { headers })
      .pipe(
        catchError(this.handleError)
      );
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
          // Errores 400 - Bad Request (como duplicados, validaciones de negocio)
          const detalle = apiError.detalle || apiError.error || '';
          
          if (detalle.includes('RUT ya está registrado') || detalle.includes('RUT')) {
            errorMessage = 'Este RUT ya está registrado como directivo';
          } else if (detalle.includes('email ya registrado') || detalle.includes('email')) {
            errorMessage = 'Este email ya está registrado en la junta';
          } else if (detalle.includes('cargo') && detalle.includes('activo')) {
            errorMessage = 'Ya existe un directivo activo con este cargo en la junta';
          } else if (detalle.includes('junta no existe')) {
            errorMessage = 'La junta especificada no existe';
          } else if (detalle.includes('Contraseña inválida')) {
            errorMessage = 'La contraseña debe tener al menos 8 caracteres';
          } else {
            errorMessage = detalle || 'Error en los datos enviados';
          }
        } else if (error.status === 409) {
          // Conflictos (duplicados)
          errorMessage = 'Ya existe un registro con estos datos';
        } else if (error.status === 500) {
          errorMessage = 'Error interno del servidor. Por favor, intenta más tarde.';
        } else {
          errorMessage = apiError.detalle || apiError.error || 'Error del servidor';
        }
      } else {
        errorMessage = `Error ${error.status}: ${error.message}`;
      }
    }

    return throwError(() => new Error(errorMessage));
  };

  /**
   * Valida los datos del formulario antes de enviar
   */
  validateFormData(data: DirectivaFormData): string[] {
    const errors: string[] = [];

    if (!data.nombres?.trim()) {
      errors.push('Los nombres son obligatorios');
    }

    if (!data.apellido_paterno?.trim()) {
      errors.push('El apellido paterno es obligatorio');
    }

    if (!data.rut?.trim()) {
      errors.push('El RUT es obligatorio');
    }

    if (!data.email?.trim()) {
      errors.push('El email es obligatorio');
    }

    if (!data.telefono?.trim()) {
      errors.push('El teléfono es obligatorio');
    }

    if (!data.cargo?.trim()) {
      errors.push('El cargo es obligatorio');
    }

    if (!data.password?.trim()) {
      errors.push('La contraseña es obligatoria');
    } else if (data.password.length < 8) {
      errors.push('La contraseña debe tener al menos 8 caracteres');
    }

    return errors;
  }
}
