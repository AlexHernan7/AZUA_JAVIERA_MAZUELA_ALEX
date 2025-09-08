import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { MenuComponent } from './menu/menu.component'; // <- ajusta la ruta si está en otra carpeta

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  standalone: true,
  imports: [RouterOutlet, MenuComponent] // <- clave
})
export class AppComponent {}