import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { catchError, throwError } from 'rxjs';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-forgot-password',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  templateUrl: './forgot-password.component.html',
  styleUrls: ['./forgot-password.component.css']
})
export class ForgotPasswordComponent {
  // Estados del flujo
  step: 'email' | 'code' | 'password' = 'email';
  
  // Formularios
  emailForm: FormGroup;
  codeForm: FormGroup;
  passwordForm: FormGroup;
  
  // Estados
  isLoading = false;
  errorMessage = '';
  successMessage = '';
  email = '';
  
  private readonly API_URL = `${environment.apiUrl}/auth`;

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private http: HttpClient
  ) {
    // Formulario para solicitar código
    this.emailForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]]
    });

    // Formulario para ingresar código
    this.codeForm = this.fb.group({
      code: ['', [Validators.required, Validators.pattern(/^\d{6}$/)]]
    });

    // Formulario para nueva contraseña
    this.passwordForm = this.fb.group({
      newPassword: ['', [Validators.required, Validators.minLength(8), Validators.maxLength(12)]],
      confirmPassword: ['', [Validators.required]]
    }, { validators: this.passwordMatchValidator });
  }

  /**
   * Validador personalizado para confirmar que las contraseñas coincidan
   */
  passwordMatchValidator(group: FormGroup) {
    const password = group.get('newPassword')?.value;
    const confirmPassword = group.get('confirmPassword')?.value;
    return password === confirmPassword ? null : { passwordMismatch: true };
  }

  /**
   * Paso 1: Solicitar código de recuperación
   */
  onRequestCode() {
    if (this.emailForm.invalid) return;

    this.isLoading = true;
    this.errorMessage = '';
    this.successMessage = '';
    
    const email = this.emailForm.value.email;
    this.email = email;

    this.http.post<{ message: string; email: string }>(
      `${this.API_URL}/password-reset/request`,
      { email }
    ).pipe(
      catchError(this.handleError.bind(this))
    ).subscribe({
      next: (response) => {
        // Mostrar mensaje del servidor (en desarrollo puede incluir el código)
        this.successMessage = response.message || 'Código enviado a tu email';
        this.step = 'code';
        this.isLoading = false;
      },
      error: (error) => {
        this.isLoading = false;
        // Error ya manejado en handleError
      }
    });
  }

  /**
   * Paso 2: Verificar código
   */
  onVerifyCode() {
    if (this.codeForm.invalid) return;

    this.isLoading = true;
    this.errorMessage = '';
    this.successMessage = '';
    
    const code = this.codeForm.value.code;

    this.http.post<{ message: string; valid: boolean }>(
      `${this.API_URL}/password-reset/verify`,
      { email: this.email, code }
    ).pipe(
      catchError(this.handleError.bind(this))
    ).subscribe({
      next: (response) => {
        this.successMessage = 'Código válido';
        this.step = 'password';
        this.isLoading = false;
      },
      error: (error) => {
        this.isLoading = false;
        // Error ya manejado en handleError
      }
    });
  }

  /**
   * Paso 3: Resetear contraseña
   */
  onResetPassword() {
    if (this.passwordForm.invalid) return;

    this.isLoading = true;
    this.errorMessage = '';
    this.successMessage = '';
    
    const code = this.codeForm.value.code;
    const newPassword = this.passwordForm.value.newPassword;

    this.http.post<{ message: string; success: boolean }>(
      `${this.API_URL}/password-reset/confirm`,
      { 
        email: this.email, 
        code,
        new_password: newPassword
      }
    ).pipe(
      catchError(this.handleError.bind(this))
    ).subscribe({
      next: (response) => {
        this.successMessage = '¡Contraseña actualizada exitosamente!';
        this.isLoading = false;
        
        // Redirigir al login después de 2 segundos
        setTimeout(() => {
          this.router.navigate(['/login']);
        }, 2000);
      },
      error: (error) => {
        this.isLoading = false;
        // Error ya manejado en handleError
      }
    });
  }

  /**
   * Manejo centralizado de errores
   */
  private handleError(error: HttpErrorResponse) {
    let errorMsg = 'Error desconocido';
    
    if (error.error && typeof error.error === 'object') {
      const apiError = error.error as any;
      errorMsg = apiError.detalle || apiError.detail || apiError.error || errorMsg;
    } else if (error.message) {
      errorMsg = error.message;
    }
    
    this.errorMessage = errorMsg;
    return throwError(() => new Error(errorMsg));
  }

  /**
   * Volver al paso anterior
   */
  goBack() {
    if (this.step === 'code') {
      this.step = 'email';
      this.codeForm.reset();
    } else if (this.step === 'password') {
      this.step = 'code';
      this.passwordForm.reset();
    }
    this.errorMessage = '';
    this.successMessage = '';
  }

  /**
   * Cancelar y volver al login
   */
  cancel() {
    this.router.navigate(['/login']);
  }
}

