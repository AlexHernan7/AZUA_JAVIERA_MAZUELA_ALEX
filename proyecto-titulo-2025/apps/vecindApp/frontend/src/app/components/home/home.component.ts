import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './home.component.html',
  styleUrl: './home.component.css',
})
export class HomeComponent {
  constructor(
    private router: Router,
    public authService: AuthService
  ) {}

  // -------- Helpers de roles ----------
  private roles(): string[] {
    return this.authService.getCurrentUser()?.roles || [];
  }
  get isAdmin(): boolean     { return this.roles().includes('admin'); }
  get isDirectiva(): boolean { return this.roles().includes('directiva'); }
  get isVecino(): boolean    { return this.roles().includes('vecino'); }

  // -------- Navegaciones existentes ----------
  goToRegister() { this.router.navigate(['/register']); }

  goToMyJunta() {
    const idJunta = this.authService.getCurrentUser()?.vecino?.id_junta || 1;
    this.router.navigate(['/juntas', idJunta]);
  }

  goToCertificado() {
    if (this.authService.isAuthenticated()) this.router.navigate(['/certificados/residencia/crear']);
    else this.router.navigate(['/login']);
  }

  goToReserva() {
    if (this.authService.isAuthenticated()) this.router.navigate(['/reservas']);
    else this.router.navigate(['/login']);
  }

  // -------- Navegaciones nuevas (según tarjetas) ----------
  goToNoticias()         { this.router.navigate(['/news']); }
  goToTramites()         { this.router.navigate(['/tramites']); }
  goToReportes()         { this.router.navigate(['/reportes']); }
  goToCrearEspacio()     { this.router.navigate(['/espacios/crear']); }
  goToCrearDirectivo()   { this.router.navigate(['/directiva/nuevo']); }
  goToCrearJunta()       { this.router.navigate(['/juntas/nueva']); }
  goToGestionUsuarios()  { this.router.navigate(['/list_user']); }
}
