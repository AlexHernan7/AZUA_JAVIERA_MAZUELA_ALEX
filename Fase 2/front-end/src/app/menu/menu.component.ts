import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';   // ← para *ngIf, *ngFor, etc.
import { RouterModule } from '@angular/router';   // ← para routerLink, routerLinkActive

@Component({
  selector: 'app-menu',
  standalone: true,
  imports: [CommonModule, RouterModule],          // ← clave
  templateUrl: './menu.component.html',
  styleUrls: ['./menu.component.css']
})
export class MenuComponent {
  mobileOpen = false;
  toggleMobile() { this.mobileOpen = !this.mobileOpen; }
  closeMobile()  { this.mobileOpen = false; }
}

