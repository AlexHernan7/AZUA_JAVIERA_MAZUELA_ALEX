
import { Component, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-menu-auth',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './menu-auth.component.html',
})
export class MenuAuthComponent {
  constructor(private router: Router, public auth: AuthService) {}

  logout() {
    this.auth.logout();
    this.router.navigate(['/login']);
  }

  go(path: string) { this.router.navigate([path]); }
  
  menuOpen = false;
  toggleMenu() {
    this.menuOpen = !this.menuOpen;
  }

  // Métodos para verificar roles
  get isAdmin(): boolean {
    return this.auth.getCurrentUser()?.roles?.includes('admin') || false;
  }

  get isDirectiva(): boolean {
    return this.auth.getCurrentUser()?.roles?.includes('directiva') || false;
  }

  get isVecino(): boolean {
    return this.auth.getCurrentUser()?.roles?.includes('vecino') || false;
  }
}
