import { Component, signal, computed, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators, FormGroup } from '@angular/forms';
import { Subject, takeUntil } from 'rxjs';
import { EspacioService } from '../../services/espacio.service';
import { ReservaService } from '../../services/reserva.service';
import { AuthService } from '../../services/auth.service';
import { EspacioResponse } from '../../interfaces/espacio.interface';
import { DisponibilidadRequest, DisponibilidadResponse, ReservaCreateRequest } from '../../interfaces/reserva.interface';
import { UserLoginData } from '../../interfaces/auth.interface';

@Component({
  selector: 'app-reservas',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './reservas.component.html'
})
export class ReservasComponent implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>();

  // Espacios obtenidos del backend
  espacios: EspacioResponse[] = [];
  loading = signal(false);
  error = signal<string | null>(null);

  // UI state
  seleccionado = signal<EspacioResponse | null>(null);
  panelAbierto = computed(() => this.seleccionado() !== null);

  // "calendario" simple: selector de horas (solo UI)
  horas = ['08:00','09:00','10:00','11:00','12:00','13:00','14:00','15:00','16:00','17:00'];

  // formulario (se inicializa en el constructor)
  form!: FormGroup;

  disponibilidad: DisponibilidadResponse | null = null;
  verificandoDisponibilidad = signal(false);
  creandoReserva = signal(false);

  // Usuario autenticado
  currentUser: UserLoginData | null = null;

  constructor(
    private fb: FormBuilder,
    private espacioService: EspacioService,
    private reservaService: ReservaService,
    private authService: AuthService
  ) {
    this.form = this.fb.group({
      fecha: ['', Validators.required],
      horaInicio: ['', Validators.required],
      horaTermino: ['', Validators.required],
      motivo: ['', Validators.required],
      asistentes: [null as number | null],
      aceptaReglamento: [false, Validators.requiredTrue]
    });
  }

  ngOnInit(): void {
    // Obtener usuario autenticado
    this.authService.currentUser$.pipe(
      takeUntil(this.destroy$)
    ).subscribe(user => {
      this.currentUser = user;
      if (user && user.vecino) {
        this.cargarEspacios();
      }
    });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  /**
   * Carga los espacios de la junta del usuario autenticado
   */
  cargarEspacios(): void {
    if (!this.currentUser?.vecino) {
      this.error.set('Usuario no autenticado o sin junta asignada');
      return;
    }

    this.loading.set(true);
    this.error.set(null);

    // Por ahora, vamos a usar un ID de junta hardcodeado para las pruebas
    // En el futuro, esto debería venir del backend en la respuesta de login
    const idJunta = 2; // ID de la junta de Maipú que creamos en los datos iniciales

    this.espacioService.getEspaciosByJunta(idJunta, true, 1, 50)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          this.espacios = response.espacios;
          this.loading.set(false);
        },
        error: (error) => {
          console.error('Error cargando espacios:', error);
          this.error.set('Error al cargar los espacios disponibles');
          this.loading.set(false);
        }
      });
  }

  // Abrir panel de reserva con el espacio elegido
  reservar(espacio: EspacioResponse) {
    this.seleccionado.set(espacio);
    // preset UI de ejemplo
    this.form.reset({
      fecha: this.hoyISO(),
      horaInicio: '10:00',
      horaTermino: '12:00',
      motivo: '',
      asistentes: null,
      aceptaReglamento: false
    });
    this.disponibilidad = null;
  }

  cerrarPanel() {
    this.seleccionado.set(null);
    this.disponibilidad = null;
  }

  // Verificar disponibilidad con el backend
  comprobarDisponibilidad() {
    const espacio = this.seleccionado();
    if (!espacio || !this.form.valid) return;

    this.verificandoDisponibilidad.set(true);
    this.disponibilidad = null;

    const formValue = this.form.value;
    const disponibilidadData: DisponibilidadRequest = {
      id_espacio: espacio.id_espacio,
      fecha: formValue.fecha,
      hora_inicio: formValue.horaInicio,
      hora_termino: formValue.horaTermino
    };

    this.reservaService.verificarDisponibilidad(disponibilidadData)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          this.disponibilidad = response;
          this.verificandoDisponibilidad.set(false);
        },
        error: (error) => {
          console.error('Error verificando disponibilidad:', error);
          this.disponibilidad = {
            disponible: false,
            mensaje: 'Error al verificar disponibilidad'
          };
          this.verificandoDisponibilidad.set(false);
        }
      });
  }

  // Crear reserva
  irAPagar() {
    const espacio = this.seleccionado();
    if (!espacio || !this.form.valid || !this.disponibilidad?.disponible) {
      return;
    }

    // Obtener datos del usuario actual
    const currentUser = this.currentUser;
    if (!currentUser?.vecino) {
      alert('Error: Usuario no autenticado o sin junta asignada');
      return;
    }

    this.creandoReserva.set(true);

    const formValue = this.form.value;
    const reservaData: ReservaCreateRequest = {
      id_espacio: espacio.id_espacio,
      id_junta: 2, // Por ahora hardcodeado, debería venir del usuario
      id_vecino: currentUser.vecino.id_vecino,
      fecha: formValue.fecha,
      hora_inicio: formValue.horaInicio,
      hora_termino: formValue.horaTermino,
      motivo: formValue.motivo,
      asistentes: formValue.asistentes || undefined,
      observaciones: formValue.observaciones || undefined,
      acepta_reglamento: true // Por ahora siempre true, debería venir del formulario
    };


    this.reservaService.createReserva(reservaData)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (reserva) => {
          console.log('Reserva creada exitosamente:', reserva);
          alert(`¡Reserva creada exitosamente! ID: ${reserva.id_reserva}`);
          this.cerrarPanel();
          this.creandoReserva.set(false);
        },
        error: (error) => {
          console.error('Error creando reserva:', error);
          alert('Error al crear la reserva: ' + (error.error?.detail || error.message));
          this.creandoReserva.set(false);
        }
      });
  }

  private hoyISO(): string {
    const d = new Date();
    return d.toISOString().split('T')[0];
  }

  private diffHoras(h1: string, h2: string): number {
    if (!h1 || !h2) return 0;
    const [h1h, h1m] = h1.split(':').map(Number);
    const [h2h, h2m] = h2.split(':').map(Number);
    const m1 = h1h * 60 + h1m;
    const m2 = h2h * 60 + h2m;
    return (m2 - m1) / 60;
  }

  formatoMoneda(n: number): string {
    return n.toLocaleString('es-CL', { style: 'currency', currency: 'CLP', maximumFractionDigits: 0 });
  }

  // Método helper para convertir string a number
  toNumber(value: any): number {
    return Number(value);
  }

  // Métodos helper para verificar arrays
  hasPermitido(): boolean {
    const espacio = this.seleccionado();
    return !!(espacio?.permitido && espacio.permitido.length > 0);
  }

  hasNoPermitido(): boolean {
    const espacio = this.seleccionado();
    return !!(espacio?.no_permitido && espacio.no_permitido.length > 0);
  }

  getPermitido(): string[] {
    const espacio = this.seleccionado();
    return espacio?.permitido || [];
  }

  getNoPermitido(): string[] {
    const espacio = this.seleccionado();
    return espacio?.no_permitido || [];
  }

  // Método para obtener la imagen del espacio
  getEspacioImage(espacio: EspacioResponse): string {
    if (espacio.foto) {
      // Si la foto existe, construir la URL correcta
      if (espacio.foto.startsWith('uploads/')) {
        // Las imágenes se sirven desde /uploads (configurado en main.py)
        return `http://localhost:8000/${espacio.foto}`;
      } else if (espacio.foto.startsWith('http')) {
        // URL absoluta
        return espacio.foto;
      } else if (espacio.foto.startsWith('/')) {
        // Ruta absoluta
        return `http://localhost:8000${espacio.foto}`;
      }
    }
    
    // Imagen por defecto según el tipo de espacio
    switch (espacio.tipo) {
      case 'cancha':
        return 'https://via.placeholder.com/400x225/0f766e/ffffff?text=Cancha';
      case 'sala':
        return 'https://via.placeholder.com/400x225/0d9488/ffffff?text=Sala+Multiuso';
      case 'plaza':
        return 'https://via.placeholder.com/400x225/14b8a6/ffffff?text=Plaza';
      default:
        return 'https://via.placeholder.com/400x225/6b7280/ffffff?text=Espacio+Comunitario';
    }
  }
}
