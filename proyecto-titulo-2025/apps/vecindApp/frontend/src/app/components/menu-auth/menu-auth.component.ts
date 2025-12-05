
import { Component, signal, computed , HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule ,NavigationEnd} from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { filter } from 'rxjs/operators';

@Component({
  selector: 'app-menu-auth',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './menu-auth.component.html',
})
export class MenuAuthComponent {
  constructor(private router: Router, public auth: AuthService) { 
    
    this.router.events
      .pipe(filter(ev => ev instanceof NavigationEnd))
      .subscribe(() => this.menuOpen = false);
    }

    toggleMenu() { this.menuOpen = !this.menuOpen; }
  onNav() { this.menuOpen = false; }        // se usa en (click) de cada enlace

  // Si cambias el tamaño de la ventana y vuelves a desktop, asegura estado coherente
  @HostListener('window:resize')
  onResize() {
    if (window.innerWidth >= 992 && this.menuOpen) {
      this.menuOpen = false;
    }
  }

  logout() {
    this.auth.logout();
    this.router.navigate(['/login']);
  }

  go(path: string) { this.router.navigate([path]); }
  
  menuOpen = false;
  
  goToNews() { this.router.navigate(['/news']); }

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

  get avatarUrl(): string {
    const currentUser = this.auth.getCurrentUser();
    
    // Para vecinos y directivos, usar la foto de perfil si existe
    const foto = currentUser?.vecino?.foto_perfil;
    if (foto && foto.trim() !== '') {
      // Verificar que sea una imagen base64 válida
      if (foto.startsWith('data:image/')) {
        return foto;
      }
      // Si no tiene el prefijo data:image/, agregarlo (por compatibilidad)
      return `data:image/jpeg;base64,${foto}`;
    }
    return 'images/avatar-placeholder2.svg';
  }

  onImageError(event: any): void {
    // Si la imagen falla al cargar, usar la imagen por defecto
    event.target.src = 'images/avatar-placeholder2.svg';
  }
}
