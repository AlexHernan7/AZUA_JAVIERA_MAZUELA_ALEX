import { Component } from '@angular/core';
import { CommonModule } from '@angular/common'; 
import { Router } from '@angular/router';

@Component({
  selector: 'app-menu',
  standalone: true,
  imports: [CommonModule],       
  templateUrl: './menu.component.html',
})
export class MenuComponent {
  constructor(private router: Router) {}
  menuOpen = false;               
  toggle() { this.menuOpen = !this.menuOpen; } 

<<<<<<< HEAD
goToLogin() { this.router.navigate(['/login']); }
  goToHome() { this.router.navigate(['/']); }  // Corregido: navegar a la ruta raíz
=======
  goToLogin() { this.router.navigate(['/login']); }
  goToHome() { this.router.navigate(['/']); }
>>>>>>> ec6da5a52b07923f2e5fd8750cd778f5eadf9f82
  goToRegister() { this.router.navigate(['/register']); }

isActive(route: string): boolean {
    return this.router.url === route;}
}