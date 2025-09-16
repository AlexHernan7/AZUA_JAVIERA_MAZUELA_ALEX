import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { Subscription } from 'rxjs';
import { AuthService } from '../../services/auth.service';
import { UserLoginData } from '../../interfaces/auth.interface';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.css'],
})
export class ProfileComponent implements OnInit, OnDestroy {
  currentUser: UserLoginData | null = null;
  isLoading: boolean = true;
  error: string | null = null;
  
  private subscription: Subscription = new Subscription();

  // Propiedades calculadas para el template
  get nombreCompleto(): string {
    if (!this.currentUser) return '';
    return `${this.currentUser.nombres} ${this.currentUser.apellido_paterno} ${this.currentUser.apellido_materno || ''}`.trim();
  }

  get avatarUrl(): string {
    const foto = this.currentUser?.vecino?.foto_perfil;
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

  get telefono(): string {
    return this.currentUser?.vecino?.telefono || 'No especificado';
  }

  get direccion(): string {
    return this.currentUser?.vecino?.direccion || 'No especificada';
  }

  get rutFormateado(): string {
    const rut = this.currentUser?.vecino?.rut;
    if (!rut) return 'No especificado';
    
    // Limpiar el RUT de cualquier formato previo
    const cleanRut = rut.replace(/[^0-9Kk]/g, '');
    
    if (cleanRut.length < 8) return rut;
    
    // Separar número y dígito verificador
    const numero = cleanRut.slice(0, -1);
    const dv = cleanRut.slice(-1);
    
    // Formatear con puntos
    const numeroFormateado = numero.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    
    return `${numeroFormateado}-${dv}`;
  }

  get fechaNacimientoFormateada(): string {
    const fecha = this.currentUser?.vecino?.fecha_nacimiento;
    if (!fecha) return 'No especificada';
    
    try {
      const date = new Date(fecha);
      return date.toLocaleDateString('es-CL', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      });
    } catch {
      return fecha;
    }
  }

  get comuna(): string {
    return this.currentUser?.vecino?.comuna || 'No especificada';
  }

  get region(): string {
    return this.currentUser?.vecino?.region || 'No especificada';
  }

  get junta(): string {
    return this.currentUser?.vecino?.junta || 'No especificada';
  }

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadUserData();
  }

  ngOnDestroy(): void {
    this.subscription.unsubscribe();
  }

  loadUserData(): void {
    // Verificar si el usuario está autenticado
    if (!this.authService.isAuthenticated()) {
      this.router.navigate(['/login']);
      return;
    }

    // Suscribirse a los cambios del usuario actual
    this.subscription.add(
      this.authService.currentUser$.subscribe({
        next: (user) => {
          this.currentUser = user;
          this.isLoading = false;
          
          if (!user) {
            // Si no hay usuario logueado, redirigir al login
            this.router.navigate(['/login']);
          }
        },
        error: (error) => {
          console.error('Error al cargar datos del usuario:', error);
          this.error = 'Error al cargar los datos del usuario';
          this.isLoading = false;
        }
      })
    );
  }

  editarPerfil(): void {
    // TODO: Implementar navegación a formulario de edición
    console.log('Editar perfil para usuario:', this.currentUser?.id_usuario);
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }

  onImageError(event: any): void {
    // Si la imagen falla al cargar, usar la imagen por defecto
    console.warn('Error al cargar la imagen de perfil, usando imagen por defecto');
    event.target.src = 'images/avatar-placeholder2.svg';
  }
}