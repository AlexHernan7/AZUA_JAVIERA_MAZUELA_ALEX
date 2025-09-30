import { Component, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators, FormGroup } from '@angular/forms';

type Espacio = {
  id: string;
  nombre: string;
  capacidad: number;
  valor: number;          // CLP
  foto: string;           // ruta a assets
  permitido: string[];
  noPermitido: string[];
  maxHoras: number;
};

@Component({
  selector: 'app-reservas',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './reservas.component.html'
})
export class ReservasComponent {

  // 3 espacios disponibles
  espacios: Espacio[] = [
    {
      id: 'cancha',
      nombre: 'Cancha',
      capacidad: 20,
      valor: 5000,
      foto: '/images/Cancha_vecindapp3.jpg',
      permitido: ['Fútbol 5', 'Básquetbol', 'Actividades recreativas'],
      noPermitido: ['Eventos con alcohol', 'Música a alto volumen'],
      maxHoras: 3
    },
    {
      id: 'sala1',
      nombre: 'Sala multiuso 1',
      capacidad: 40,
      valor: 7000,
      foto: '/images/sede-vecinal1.jpg',
      permitido: ['Reuniones', 'Cumpleaños familiares', 'Talleres'],
      noPermitido: ['Humo dentro de la sala', 'Amplificación excesiva'],
      maxHoras: 4
    },
    {
      id: 'sala2',
      nombre: 'Sala multiuso 2',
      capacidad: 25,
      valor: 6000,
      foto: '/images/sede-vecinal2.jpg',
      permitido: ['Clases', 'Charlas', 'Reuniones pequeñas'],
      noPermitido: ['Consumo de alcohol', 'Fiestas masivas'],
      maxHoras: 4
    }
  ];

  // UI state
  seleccionado = signal<Espacio | null>(null);
  panelAbierto = computed(() => this.seleccionado() !== null);

  // “calendario” simple: selector de horas (solo UI)
  horas = ['08:00','09:00','10:00','11:00','12:00','13:00','14:00','15:00','16:00','17:00'];

  // formulario (se inicializa en el constructor)
  form!: FormGroup;

  disponibilidad: 'ok' | 'no' | null = null;

  constructor(private fb: FormBuilder) {
    this.form = this.fb.group({
      fecha: ['', Validators.required],
      horaInicio: ['', Validators.required],
      horaTermino: ['', Validators.required],
      motivo: ['', Validators.required],
      asistentes: [null as number | null],
      aceptaReglamento: [false, Validators.requiredTrue]
    });
  }

  // Abrir panel de reserva con el espacio elegido
  reservar(espacio: Espacio) {
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
  }

  // Simular chequeo de disponibilidad (solo UI)
  comprobarDisponibilidad() {
    const s = this.seleccionado();
    if (!s) return;

    const hi = this.form.value.horaInicio ?? '';
    const ht = this.form.value.horaTermino ?? '';
    const dur = this.diffHoras(hi, ht);

    if (dur <= 0 || dur > s.maxHoras) {
      this.disponibilidad = 'no';
    } else {
      this.disponibilidad = 'ok';
    }
  }

  irAPagar() {
    alert('💳 Ir a pagar (UI de ejemplo)');
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
}
