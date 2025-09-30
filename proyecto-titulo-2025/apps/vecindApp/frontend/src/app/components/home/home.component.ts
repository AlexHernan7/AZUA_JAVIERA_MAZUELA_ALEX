import { Component } from '@angular/core';
import { CommonModule } from '@angular/common'; 
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { RouterModule } from '@angular/router';

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

  goToRegister() {
    this.router.navigate(['/register']);
  }

  /**
   * Navega al perfil de la junta del usuario
   */
  goToMyJunta() {
    // Por ahora usamos ID fijo 1, en el futuro se podría obtener del usuario
    this.router.navigate(['/juntas', 1]);
  }

  goToCertificado() {
    if (this.authService.isAuthenticated()) {
      this.router.navigate(['/certificados/residencia/crear']);
    } else {
      this.router.navigate(['/login']);
    }
  }

  goToReserva() {
    if (this.authService.isAuthenticated()) {
      this.router.navigate(['/reservas']);
    } else {
      this.router.navigate(['/login']);
    }
  }



}
