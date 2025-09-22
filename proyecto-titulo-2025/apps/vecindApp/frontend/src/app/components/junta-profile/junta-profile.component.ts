// src/app/components/junta-profile/junta-profile.component.ts
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { DirectivaService } from '../../services/directiva.service';
import { AuthService } from '../../services/auth.service';
import { DirectivaResponse } from '../../interfaces/directiva.interface';

export interface Junta {
  id_junta: number;
  id_comuna: number;
  nombre: string;
  direccion: string;
  telefono: string;
  email: string;
  descripcion?: string;
  created_at?: string;
  comuna_nombre?: string;
  region_nombre?: string;
  logo_url?: string;
}

// Usamos DirectivaResponse del servicio, pero mantenemos esta interfaz para compatibilidad
export interface Directivo {
  id_usuario?: number;
  nombres: string;
  apellido_paterno: string;
  apellido_materno?: string;
  cargo: 'Presidente' | 'Vicepresidente' | 'Secretario' | 'Tesorero' | 'Vocal' | string;
  email?: string;
  telefono?: string;
  foto_perfil?: string;
}

@Component({
  selector: 'app-junta-profile',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './junta-profile.component.html',
  styleUrls: ['./junta-profile.component.css'],
})
export class JuntaProfileComponent implements OnInit {
  // estados locales
  isLoading = true;
  error: string | null = null;

  // datos a mostrar
  junta: Junta | null = null;
  directiva: Directivo[] = [];

  constructor(
    private route: ActivatedRoute,
    private directivaService: DirectivaService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    // Verificar si el usuario está autenticado
    if (!this.authService.isLoggedIn()) {
      this.error = 'Debes estar logueado para ver esta información.';
      this.isLoading = false;
      return;
    }

    // Cargar datos de la junta y directivos
    this.loadJuntaProfile();
  }

  /**
   * Carga el perfil de la junta del usuario autenticado
   */
  loadJuntaProfile(): void {
    this.isLoading = true;
    this.error = null;

    // Obtener datos del usuario logueado para mostrar info básica de la junta
    const currentUser = this.authService.getCurrentUser();
    if (currentUser && currentUser.vecino) {
      // Crear objeto junta básico con datos del usuario
      this.junta = {
        id_junta: 1,
        id_comuna: 1,
        nombre: currentUser.vecino.junta || 'Junta de Vecinos Barrio Oeste',
        direccion: 'Información disponible próximamente',
        telefono: 'Información disponible próximamente',
        email: 'Información disponible próximamente',
        descripcion: 'Información de la junta de vecinos. Los datos detallados se mostrarán cuando estén disponibles.',
        comuna_nombre: currentUser.vecino.comuna || 'Comuna',
        region_nombre: currentUser.vecino.region || 'Región',
        logo_url: ''
      };
    }

    // Cargar directivos reales de la junta del usuario
    this.loadDirectivos();
  }

  /**
   * Carga los directivos de la junta del usuario autenticado
   */
  private loadDirectivos(): void {
    this.directivaService.getMyJuntaDirectivos(false).subscribe({
      next: (directivos: DirectivaResponse[]) => {
        // Convertir DirectivaResponse a Directivo para compatibilidad con el template
        this.directiva = directivos.map(d => ({
          nombres: d.nombres,
          apellido_paterno: d.apellido_paterno,
          apellido_materno: d.apellido_materno,
          cargo: this.formatCargo(d.cargo),
          email: d.email,
          telefono: d.telefono,
          foto_perfil: d.foto_perfil
        }));

        this.isLoading = false;
      },
      error: (error: any) => {
        console.error('Error al cargar directivos:', error);
        this.error = error.message || 'Error al cargar los directivos de la junta.';
        this.isLoading = false;
      }
    });
  }

  /**
   * Formatea el cargo para mostrar con la primera letra en mayúscula
   */
  private formatCargo(cargo: string): string {
    if (!cargo) return '';
    return cargo.charAt(0).toUpperCase() + cargo.slice(1).toLowerCase();
  }

  get tieneDirectiva(): boolean {
    return this.directiva.length > 0;
  }

  nombreCompleto(d: Directivo): string {
    return `${d.nombres} ${d.apellido_paterno} ${d.apellido_materno ?? ''}`.trim();
  }

  avatar(d: Directivo): string {
    if (!d.foto_perfil) return 'images/avatar-placeholder2.svg';
    return d.foto_perfil.startsWith('data:image')
      ? d.foto_perfil
      : `data:image/jpeg;base64,${d.foto_perfil}`;
  }

  cargoBadgeClass(cargo: string): string {
    const map: Record<string, string> = {
      Presidente: 'bg-primary-soft',
      Vicepresidente: 'bg-info-soft',
      Secretario: 'bg-success-soft',
      Tesorero: 'bg-warning-soft',
      Vocal: 'bg-secondary-soft',
    };
    return map[cargo] ?? 'bg-secondary-soft';
  }
}
