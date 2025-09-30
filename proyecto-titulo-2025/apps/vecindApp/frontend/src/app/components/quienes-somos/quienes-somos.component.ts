import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';

// Si ya tienes un AuthService, lo inyectamos para ocultar/mostrar el CTA.
import { AuthService } from '../../services/auth.service';

type Founder = {
  nombre: string;
  rol: string;
  foto: string;     // /images/...
  linkedin?: string;
};

@Component({
  selector: 'app-quienes-somos',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './quienes-somos.component.html'
})
export class QuienesSomosComponent {
  // Hero e imágenes (ajusta rutas según tu proyecto: public/images o assets/images)
  heroImg = '/images/hero_vecindapp23.png';
  cardImg = '/images/Logo_vecindapp.png';

  founders: Founder[] = [
    {
      nombre: 'Javiera Azúa',
      rol: 'Cofundadora – Ingeniería en Informática, Duoc UC (Maipú)',
      foto: '/images/javi-perfil.jpg'
    },
    {
      nombre: 'Alex Mazuela',
      rol: 'Cofundador – Ingeniería en Informática, Duoc UC (Maipú)',
      foto: '/images/ale-perfil1.jpg'
    }
  ];

  valores = [
    { icon: 'bi-people', titulo: 'Participación', desc: 'Impulsamos espacios para que los vecinos se informen y participen activamente.' },
    { icon: 'bi-shield-check', titulo: 'Transparencia', desc: 'Procesos claros, trazables y con foco en la confianza comunitaria.' },
    { icon: 'bi-lightning-charge', titulo: 'Eficiencia', desc: 'Digitalizamos trámites para ahorrar tiempo, costos y esfuerzo.' },
    { icon: 'bi-heart', titulo: 'Cercanía', desc: 'Tecnología con sentido social, pensada para el barrio.' }
  ];

  constructor(public auth: AuthService, private router: Router) {}

  goToRegister() {
    this.router.navigateByUrl('/register'); // ajusta si tu ruta es distinta
  }
}
