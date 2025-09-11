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

  goToLogin() { this.router.navigate(['/login']); }
  goToHome() { this.router.navigate(['/']); }
  goToRegister() { this.router.navigate(['/register']); }

  isActive(route: string): boolean {
    return this.router.url === route;
  }
}