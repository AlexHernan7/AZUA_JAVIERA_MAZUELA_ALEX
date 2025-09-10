import { Component } from '@angular/core';
import { CommonModule } from '@angular/common'; // ✅ habilita *ngIf, *ngFor

@Component({
  selector: 'app-menu',
  standalone: true,
  imports: [CommonModule],        // ✅ importante para *ngIf
  templateUrl: './menu.component.html',
})
export class MenuComponent {
  menuOpen = false;               // ✅ propiedad requerida en el template
  toggle() { this.menuOpen = !this.menuOpen; } // opcional (más limpio)
}