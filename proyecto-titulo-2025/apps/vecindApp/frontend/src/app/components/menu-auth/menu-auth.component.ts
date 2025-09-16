
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
    this.router.navigate(['/']);
  }

  go(path: string) { this.router.navigate([path]); }
  
  menuOpen = false;
  toggleMenu() {
  this.menuOpen = !this.menuOpen;
}

}
