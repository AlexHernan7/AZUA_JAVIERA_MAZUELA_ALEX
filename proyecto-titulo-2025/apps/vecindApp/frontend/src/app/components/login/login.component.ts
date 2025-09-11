import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { LoginRequest } from '../../interfaces/auth.interface';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './login.component.html',
  styleUrl: './login.component.css',
})
export class LoginComponent {
  // Modelo para el formulario
  loginData: LoginRequest = {
    email: '',
    password: ''
  };

  // Estados del componente
  isLoading = false;
  errorMessage = '';

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  /**
   * Maneja el envío del formulario de login
   */
  onLogin(): void {
    // Limpiar mensaje de error previo
    this.errorMessage = '';

    // Validaciones básicas
    if (!this.loginData.email || !this.loginData.password) {
      this.errorMessage = 'Por favor, completa todos los campos';
      return;
    }

    if (!this.isValidEmail(this.loginData.email)) {
      this.errorMessage = 'Por favor, ingresa un email válido';
      return;
    }

    // Iniciar proceso de login
    this.isLoading = true;

    this.authService.login(this.loginData).subscribe({
      next: (response) => {
        console.log('Login exitoso:', response);
        this.isLoading = false;
        
        // Redirigir al usuario a la página principal
        this.router.navigate(['/']);
      },
      error: (error) => {
        console.error('Error en login:', error);
        this.isLoading = false;
        this.errorMessage = error.message || 'Error al iniciar sesión. Verifica tus credenciales.';
      }
    });
  }

  /**
   * Validación simple de email
   */
  private isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }
}
