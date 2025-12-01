import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, NgForm } from '@angular/forms';
import { Router, ActivatedRoute, RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { LoginRequest } from '../../interfaces/auth.interface';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule, RouterModule],
  templateUrl: './login.component.html',
  styleUrl: './login.component.css',
})
export class LoginComponent implements OnInit {
  loginData: LoginRequest = { email: '', password: '' };

  isLoading = false;
  errorMessage = '';
  successMessage = '';
  submitted = false;
  showPass = false;

  constructor(
    private authService: AuthService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    this.route.queryParams.subscribe(params => {
      if (params['message']) {
        this.successMessage = params['message'];
        setTimeout(() => (this.successMessage = ''), 5000);
      }
    });
  }

  toggleShowPass() {
    this.showPass = !this.showPass;
  }

  /** Mostrar inválido si el control está sucio/tocado o si ya se intentó enviar */
  showInvalid(ctrl: any): boolean {
    return !!ctrl && ctrl.invalid && (ctrl.dirty || ctrl.touched || this.submitted);
  }

  onLogin(form: NgForm): void {
    this.submitted = true;
    this.errorMessage = '';

    if (form.invalid) {
      this.errorMessage = 'Por favor corrige los campos marcados.';
      return;
    }

    // saneo básico
    const payload: LoginRequest = {
      email: (this.loginData.email || '').trim().toLowerCase(),
      password: (this.loginData.password || '').trim(),
    };

    this.isLoading = true;

    this.authService.login(payload).subscribe({
      next: () => {
        this.isLoading = false;
        this.router.navigate(['/']);
      },
      error: (err) => {
        this.isLoading = false;

        // intenta mapear mensajes del backend
        const raw = (err?.error?.error || err?.error?.detalle || err?.message || '').toString();

        if (/inactivo/i.test(raw)) {
          this.errorMessage = 'Tu usuario está inactivo. Contacta a la directiva.';
        } else if (/credenciales inválidas|incorrectos/i.test(raw)) {
          this.errorMessage = 'Email o contraseña incorrectos.';
        } else if (/roles/i.test(raw)) {
          this.errorMessage = 'Tu cuenta no tiene roles asignados. Contacta a la directiva.';
        } else {
          this.errorMessage = 'Error al iniciar sesión. Credenciales invalidas. Intenta nuevamente.';
        }
      },
    });
  }
}
