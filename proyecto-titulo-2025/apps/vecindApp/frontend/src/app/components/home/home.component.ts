import { Component } from '@angular/core';
import { CommonModule } from '@angular/common'; 
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule],    
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
}
