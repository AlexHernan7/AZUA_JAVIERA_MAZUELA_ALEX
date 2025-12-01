import { Injectable } from '@angular/core';
import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
//import { AuthService } from '../services/auth.service';
import { HttpClient, HttpErrorResponse, HttpParams } from '@angular/common/http';
import { Observable, BehaviorSubject, throwError } from 'rxjs';
import { tap, catchError } from 'rxjs/operators';
import { LoginRequest, LoginResponse, UserLoginData, ApiError, RegisterRequest, RegisterResponse, UpdateProfileRequest, UpdateProfileResponse, ComunasList, JuntasList, ChangePasswordRequest, ChangePasswordResponse, VecinoListItem, DirectivaListItem } from '../interfaces/auth.interface';
import { environment } from '../../environments/environment';

export const authGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  const router = inject(Router);

  if (auth.isAuthenticated()) return true;
  router.navigate(['/login']);
  return false;
};

export const directivaGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  const router = inject(Router);

  const user = auth.getCurrentUser();
  const hasAccess = auth.isAuthenticated() && user?.roles && 
                    (user.roles.includes('directiva') || user.roles.includes('admin'));
  
  if (hasAccess) {
    return true;
  }
  router.navigate(['/']);
  return false;
};

@Injectable({
  providedIn: 'root'
})



export class AuthService {
  private readonly API_URL = environment.apiUrl; // URL del backend desde environment
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
          // Actualizar todos los campos editables
          currentUser.nombres = response.nombres;
          currentUser.apellido_paterno = response.apellido_paterno;
          currentUser.apellido_materno = response.apellido_materno || '';
          currentUser.email = response.email;
          currentUser.vecino.apellido_paterno = response.apellido_paterno;
          currentUser.vecino.apellido_materno = response.apellido_materno || '';
          currentUser.vecino.rut = response.rut;
          currentUser.vecino.fecha_nacimiento = response.fecha_nacimiento;
          currentUser.vecino.telefono = response.telefono;
          currentUser.vecino.direccion = response.direccion;
          currentUser.vecino.comuna = response.comuna;
          currentUser.vecino.region = response.region;
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
   * Cambia la contraseña del usuario
   */
  changePassword(passwordData: ChangePasswordRequest): Observable<ChangePasswordResponse> {
    const token = this.getToken();
    if (!token) {
      return throwError(() => new Error('Token no encontrado'));
    }

    const headers = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };

    return this.http.post<ChangePasswordResponse>(
      `${this.API_URL}/users/change-password`,
      passwordData,
      { headers }
    ).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Obtiene la lista de vecinos de la junta del usuario autenticado
   */
  getVecinosMyJunta(activosOnly: boolean = false): Observable<VecinoListItem[]> {
    const token = this.getToken();
    if (!token) {
      return throwError(() => new Error('Token no encontrado'));
    }

    const headers = { 
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };
    
    let params = new HttpParams();
    if (activosOnly) {
      params = params.set('activos_only', 'true');
    }
    
    return this.http.get<VecinoListItem[]>(
      `${this.API_URL}/users/vecinos/mi-junta`,
      { headers, params }
    ).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Obtiene la lista de directivos de la junta del usuario autenticado
   */
  getDirectivosMyJunta(activosOnly: boolean = false): Observable<DirectivaListItem[]> {
    const token = this.getToken();
    if (!token) {
      return throwError(() => new Error('Token no encontrado'));
    }

    const headers = { 
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };
    
    let params = new HttpParams();
    if (activosOnly) {
      params = params.set('activos_only', 'true');
    }
    
    return this.http.get<DirectivaListItem[]>(
      `${this.API_URL}/directiva/mi-junta`,
      { headers, params }
    ).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Obtiene TODOS los vecinos del sistema (solo para admin)
   */
  getAllVecinosAdmin(): Observable<VecinoListItem[]> {
    return this.http.get<VecinoListItem[]>(
      `${this.API_URL}/users/vecinos/admin/all`
    ).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Obtiene TODOS los directivos del sistema (solo para admin)
   */
  getAllDirectivosAdmin(): Observable<DirectivaListItem[]> {
    return this.http.get<DirectivaListItem[]>(
      `${this.API_URL}/directiva/admin/all`
    ).pipe(
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
  getComunasByRegion(regionId: number): Observable<any> {
    return this.http.get(`${this.API_URL}/auth/comunas/region/${regionId}`)
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Obtiene todas las juntas disponibles (sin filtro de comuna)
   */
  getAllJuntas(limit: number = 100): Observable<JuntasList> {
    return this.http.get<JuntasList>(`${this.API_URL}/juntas?limit=${limit}`)
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

    return throwError(() => new Error(errorMessage));
  };
}
