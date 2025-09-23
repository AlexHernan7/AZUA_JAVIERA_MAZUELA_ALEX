import { Injectable } from '@angular/core';
import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
//import { AuthService } from '../services/auth.service';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, BehaviorSubject, throwError } from 'rxjs';
import { tap, catchError } from 'rxjs/operators';
import { LoginRequest, LoginResponse, UserLoginData, ApiError, RegisterRequest, RegisterResponse, UpdateProfileRequest, UpdateProfileResponse, ComunasList, JuntasList } from '../interfaces/auth.interface';

export const authGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  const router = inject(Router);

  if (auth.isAuthenticated()) return true;
  router.navigate(['/login']);
  return false;
};

@Injectable({
  providedIn: 'root'
})



export class AuthService {
  private readonly API_URL = 'http://localhost:8000/api'; // URL base del backend con prefijo /api
  private readonly TOKEN_KEY = 'vecindapp_token';
  private readonly USER_KEY = 'vecindapp_user';

  // BehaviorSubject para manejar el estado de autenticación
  private currentUserSubject!: BehaviorSubject<UserLoginData | null>;
  public currentUser$!: Observable<UserLoginData | null>;

  private isLoggedInSubject!: BehaviorSubject<boolean>;
  public isLoggedIn$!: Observable<boolean>;

  constructor(private http: HttpClient) {
    // Inicializar BehaviorSubjects después de que el constructor esté completo
    this.initializeSubjects();
  }

  private initializeSubjects(): void {
    this.currentUserSubject = new BehaviorSubject<UserLoginData | null>(this.getUserFromStorage());
    this.currentUser$ = this.currentUserSubject.asObservable();

    this.isLoggedInSubject = new BehaviorSubject<boolean>(this.hasValidToken());
    this.isLoggedIn$ = this.isLoggedInSubject.asObservable();
  }

  /**
   * Realiza el login del usuario
   */
  login(credentials: LoginRequest): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${this.API_URL}/auth/login`, credentials)
      .pipe(
        tap(response => {
          // Guardar token y datos del usuario
          this.setToken(response.access_token);
          this.setUser(response.user);
          
          // Actualizar subjects
          this.currentUserSubject.next(response.user);
          this.isLoggedInSubject.next(true);
        }),
        catchError(this.handleError)
      );
  }

  /**
   * Cierra la sesión del usuario
   */
  logout(): void {
    // Limpiar storage
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.USER_KEY);
    
    // Actualizar subjects
    this.currentUserSubject.next(null);
    this.isLoggedInSubject.next(false);
  }

  /**
   * Obtiene el token actual
   */
  getToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  /**
   * Obtiene el usuario actual
   */
  getCurrentUser(): UserLoginData | null {
    return this.currentUserSubject.value;
  }

  /**
   * Verifica si el usuario está autenticado
   */
  isAuthenticated(): boolean {
    return this.hasValidToken();
  }

  /**
   * Método sincrónico para verificar si está logueado (alias de isAuthenticated)
   */
  isLoggedIn(): boolean {
    return this.isAuthenticated();
  }

  // Métodos privados
  private setToken(token: string): void {
    localStorage.setItem(this.TOKEN_KEY, token);
  }

  private setUser(user: UserLoginData): void {
    localStorage.setItem(this.USER_KEY, JSON.stringify(user));
  }

  private getUserFromStorage(): UserLoginData | null {
    const userStr = localStorage.getItem(this.USER_KEY);
    if (userStr) {
      try {
        return JSON.parse(userStr);
      } catch {
        return null;
      }
    }
    return null;
  }

  private hasValidToken(): boolean {
    const token = this.getToken();
    if (!token) return false;

    // Aquí podrías agregar validación de expiración del JWT
    // Por simplicidad, solo verificamos que existe
    return true;
  }

  /**
   * Registra un nuevo usuario
   */
  register(userData: RegisterRequest): Observable<RegisterResponse> {
    return this.http.post<RegisterResponse>(`${this.API_URL}/auth/register`, userData)
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Actualiza el perfil del usuario
   */
  updateProfile(profileData: UpdateProfileRequest): Observable<UpdateProfileResponse> {
    const currentUser = this.getCurrentUser();
    if (!currentUser) {
      return throwError(() => new Error('Usuario no encontrado'));
    }

    const token = this.getToken();
    if (!token) {
      return throwError(() => new Error('Token no encontrado'));
    }

    const headers = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };

    return this.http.patch<UpdateProfileResponse>(
      `${this.API_URL}/users/profile`, 
      profileData,
      { headers }
    ).pipe(
      tap(response => {
        // Actualizar los datos del usuario en el storage y en los subjects
        if (currentUser && currentUser.vecino) {
          currentUser.email = response.email;
          currentUser.vecino.telefono = response.telefono;
          if (response.foto_perfil) {
            currentUser.vecino.foto_perfil = response.foto_perfil;
          }
          
          this.setUser(currentUser);
          this.currentUserSubject.next(currentUser);
        }
      }),
      catchError(this.handleError)
    );
  }

  /**
   * Obtiene la lista de regiones disponibles
   */
  getRegiones(): Observable<any> {
    return this.http.get<any>(`${this.API_URL}/auth/regiones`)
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Obtiene la lista de comunas disponibles
   */
  getComunas(): Observable<ComunasList> {
    return this.http.get<ComunasList>(`${this.API_URL}/auth/comunas`)
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Obtiene las comunas de una región específica
   */
  getComunasByRegion(regionId: number): Observable<ComunasList> {
    return this.http.get<ComunasList>(`${this.API_URL}/auth/comunas/region/${regionId}`)
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Obtiene las juntas de una comuna específica
   */
  getJuntasByComuna(comunaId: number): Observable<JuntasList> {
    return this.http.get<JuntasList>(`${this.API_URL}/auth/juntas/${comunaId}`)
      .pipe(
        catchError(this.handleError)
      );
  }

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
          // Errores 400 - Bad Request (como duplicados)
          const detalle = apiError.detalle || apiError.error || '';
          if (detalle.includes('llave duplicada') || detalle.includes('UniqueViolationError')) {
            if (detalle.includes('rut')) {
              errorMessage = 'Este RUT ya está registrado en el sistema';
            } else if (detalle.includes('email')) {
              errorMessage = 'Este email ya está registrado en el sistema';
            } else {
              errorMessage = 'Ya existe un registro con estos datos';
            }
          } else {
            errorMessage = detalle || 'Error en los datos enviados';
          }
        } else {
          errorMessage = apiError.detalle || apiError.error || 'Error del servidor';
        }
      } else {
        errorMessage = `Error ${error.status}: ${error.message}`;
      }
    }

    console.error('Error en AuthService:', errorMessage);
    return throwError(() => new Error(errorMessage));
  };
}
