// src/app/components/junta-profile/junta-profile.component.ts
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';

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

  constructor(private route: ActivatedRoute) {}

  ngOnInit(): void {
    // lee el :id de la ruta (si luego conectas backend, úsalo para pedir datos)
    const id = Number(this.route.snapshot.paramMap.get('id') ?? 0);

    // MOCK de demostración (reemplaza por llamada a servicio)
    // Simulamos espera corta
    setTimeout(() => {
      if (!id) {
        this.error = 'Junta no encontrada.';
        this.isLoading = false;
        return;
      }

      this.junta = {
        id_junta: id,
        id_comuna: 13112,
        nombre: 'Junta de Vecinos Villa Los Aromos',
        direccion: 'Av. Siempre Viva 1234',
        telefono: '+56 9 9876 5432',
        email: 'junta.losaromos@mail.com',
        descripcion:
          'Somos una organización vecinal que busca mejorar la calidad de vida de nuestros vecinos.',
        created_at: new Date().toISOString(),
        comuna_nombre: 'Maipú',
        region_nombre: 'Región Metropolitana',
        logo_url: '' // si tienes un logo, pon la URL
      };

      this.directiva = [
        { nombres: 'Juan',  apellido_paterno: 'Pérez',   cargo: 'Presidente',     email: 'juan@mail.com',  telefono: '+56 9 1111 1111', foto_perfil: '' },
        { nombres: 'María', apellido_paterno: 'González', cargo: 'Vicepresidente', email: 'maria@mail.com', telefono: '+56 9 2222 2222', foto_perfil: '' },
        { nombres: 'Carlos', apellido_paterno: 'López',   cargo: 'Secretario',     email: 'carlos@mail.com',telefono: '+56 9 3333 3333', foto_perfil: '' },
        { nombres: 'Ana',   apellido_paterno: 'Torres',  cargo: 'Tesorero',       email: 'ana@mail.com',   telefono: '+56 9 4444 4444', foto_perfil: '' },
      ];

      this.isLoading = false;
    }, 400);
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
