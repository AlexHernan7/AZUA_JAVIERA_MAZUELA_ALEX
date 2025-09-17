import { Component } from '@angular/core';
import { CommonModule } from '@angular/common'; 
import { Router, RouterModule } from '@angular/router';

@Component({
  selector: 'app-menu',
  standalone: true,
  imports: [CommonModule, RouterModule],       
  templateUrl: './menu.component.html',
})
export class MenuComponent {
  constructor(private router: Router) {}

  menuOpen = false;               
  toggle() { this.menuOpen = !this.menuOpen; } 
  closeMenu() { this.menuOpen = false; }

  goToLogin() { this.router.navigate(['/login']); }
  goToHome() { this.router.navigate(['/']); }
  goToRegister() { this.router.navigate(['/register']); }
  goToNews() { this.router.navigate(['/news']); }

  
}