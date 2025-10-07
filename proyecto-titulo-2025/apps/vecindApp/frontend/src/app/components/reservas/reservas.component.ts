import { Component, signal, computed, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators, FormGroup } from '@angular/forms';
import { Subject, takeUntil } from 'rxjs';
import { EspacioService } from '../../services/espacio.service';
import { ReservaService } from '../../services/reserva.service';
import { AuthService } from '../../services/auth.service';
import { EspacioResponse } from '../../interfaces/espacio.interface';
import { DisponibilidadRequest, DisponibilidadResponse, ReservaCreateRequest, ReservaConPagoRequest, ReservaWebpayResponse } from '../../interfaces/reserva.interface';
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
  horas = ['09:00','10:00','11:00','12:00','13:00','14:00','15:00','16:00','17:00','18:00','19:00','20:00','21:00','22:00','23:00'];

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

    // Listener para actualizar hora término cuando cambie hora inicio
    this.form.get('horaInicio')?.valueChanges.subscribe(() => {
      const horaInicio = this.form.get('horaInicio')?.value;
      const horaTermino = this.form.get('horaTermino')?.value;
      
      if (horaInicio && horaTermino && this.compararHoras(horaTermino, horaInicio) <= 0) {
        // Si la hora término es anterior o igual a la hora inicio, limpiar la selección
        this.form.get('horaTermino')?.setValue('');
      }
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

    if (!this.currentUser.vecino.id_junta) {
      this.error.set('Usuario sin junta asignada');
      return;
    }

    this.loading.set(true);
    this.error.set(null);

    // Usar el ID de junta del usuario autenticado
    const idJunta = this.currentUser.vecino.id_junta;

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
    
    // Calcular hora de inicio por defecto (mínimo 30 minutos desde ahora)
    const horaMinima = this.getHoraMinima();
    const horaTermino = this.calcularHoraTermino(horaMinima);
    
    // preset UI de ejemplo
    this.form.reset({
      fecha: this.hoyISO(),
      horaInicio: horaMinima,
      horaTermino: horaTermino,
      motivo: '',
      asistentes: null,
      aceptaReglamento: false
    });
    this.disponibilidad = null;
  }

  // Calcular hora de término basada en la hora de inicio
  private calcularHoraTermino(horaInicio: string): string {
    const [hora, minuto] = horaInicio.split(':').map(Number);
    const horaTermino = hora + 2; // 2 horas por defecto
    return `${horaTermino.toString().padStart(2, '0')}:${minuto.toString().padStart(2, '0')}`;
  }

  cerrarPanel() {
    this.seleccionado.set(null);
    this.disponibilidad = null;
  }

  // Verificar disponibilidad con el backend
  comprobarDisponibilidad() {
    const espacio = this.seleccionado();
    if (!espacio || !this.form.valid) return;

    const formValue = this.form.value;
    
    // Debug: mostrar información de fecha/hora
    this.debugFechaHora(formValue.fecha, formValue.horaInicio);
    
    // Validar fecha
    if (this.esFechaPasada(formValue.fecha)) {
      this.disponibilidad = {
        disponible: false,
        mensaje: 'No se pueden hacer reservas para fechas u horarios pasados'
      };
      return;
    }

    // Validación de horarios pasados deshabilitada - permitir reservas en cualquier momento
    // if (this.esHorarioPasado(formValue.fecha, formValue.horaInicio)) {
    //   this.disponibilidad = {
    //     disponible: false,
    //     mensaje: 'No se pueden hacer reservas para fechas u horarios pasados'
    //   };
    //   return;
    // }

    this.verificandoDisponibilidad.set(true);
    this.disponibilidad = null;

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

  // Crear reserva con pago
  irAPagar() {
    const espacio = this.seleccionado();
    if (!espacio || !this.form.valid || !this.disponibilidad?.disponible) {
      return;
    }

    // Obtener datos del usuario actual
    const currentUser = this.currentUser;
    if (!currentUser?.vecino || !currentUser.vecino.id_junta) {
      alert('Error: Usuario no autenticado o sin junta asignada');
      return;
    }

    this.creandoReserva.set(true);

    const formValue = this.form.value;
    const reservaData: ReservaConPagoRequest = {
      id_espacio: espacio.id_espacio,
      id_junta: currentUser.vecino.id_junta, // ID de junta del usuario autenticado
      id_vecino: currentUser.vecino.id_vecino,
      fecha: formValue.fecha,
      hora_inicio: formValue.horaInicio,
      hora_termino: formValue.horaTermino,
      motivo: formValue.motivo,
      asistentes: formValue.asistentes || undefined,
      observaciones: formValue.observaciones || undefined,
      acepta_reglamento: formValue.aceptaReglamento
    };

    this.reservaService.createReservaConWebpay(reservaData)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response: ReservaWebpayResponse) => {
          console.log('Reserva con pago creada exitosamente:', response);
          
          // Redirigir a Webpay para completar el pago
          if (response.payment_url && response.webpay_token) {
            // Guardar información de la reserva en localStorage para después del pago
            localStorage.setItem('reserva_pendiente', JSON.stringify({
              reserva_id: response.reserva.id_reserva,
              espacio_nombre: espacio.nombre,
              fecha: formValue.fecha,
              hora_inicio: formValue.horaInicio,
              hora_termino: formValue.horaTermino,
              valor: response.payment_intent.amount
            }));
            
            // Redirigir a Webpay usando POST (como en certificados)
            this.redirectToWebpay(response.payment_url, response.webpay_token);
          } else {
            alert('Error: No se recibió la URL de pago');
            this.creandoReserva.set(false);
          }
        },
        error: (error) => {
          console.error('Error creando reserva con pago:', error);
          alert('Error al crear la reserva: ' + (error.error?.detail || error.message));
          this.creandoReserva.set(false);
        }
      });
  }

  hoyISO(): string {
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

  // Validar si la fecha es pasada
  private esFechaPasada(fecha: string): boolean {
    const hoy = new Date();
    // Crear fecha de reserva en zona horaria local
    const [año, mes, dia] = fecha.split('-').map(Number);
    const fechaReserva = new Date(año, mes - 1, dia);
    
    hoy.setHours(0, 0, 0, 0);
    fechaReserva.setHours(0, 0, 0, 0);
    return fechaReserva < hoy;
  }

  // Validar si el horario es pasado (solo para hoy)
  esHorarioPasado(fecha: string, hora: string): boolean {
    const hoy = new Date();
    // Crear fecha de reserva en zona horaria local
    const [año, mes, dia] = fecha.split('-').map(Number);
    const fechaReserva = new Date(año, mes - 1, dia);
    
    // Si no es hoy, no es horario pasado
    if (fechaReserva.toDateString() !== hoy.toDateString()) {
      return false;
    }
    
    const ahora = new Date();
    const [horaH, horaM] = hora.split(':').map(Number);
    const horarioReserva = new Date();
    horarioReserva.setHours(horaH, horaM, 0, 0);
    
    return horarioReserva <= ahora;
  }

  // Obtener la hora mínima permitida para hoy
  getHoraMinima(): string {
    const ahora = new Date();
    const horaActual = ahora.getHours();
    const minutoActual = ahora.getMinutes();
    
    // Sin margen - permitir reservas hasta el momento actual
    return `${horaActual.toString().padStart(2, '0')}:${minutoActual.toString().padStart(2, '0')}`;
  }

  // Validar si la fecha seleccionada es válida
  esFechaValida(): boolean {
    const fecha = this.form.get('fecha')?.value;
    if (!fecha) return false;
    return !this.esFechaPasada(fecha);
  }

  // Validar si el horario de inicio es válido
  esHorarioInicioValido(): boolean {
    const fecha = this.form.get('fecha')?.value;
    const horaInicio = this.form.get('horaInicio')?.value;
    if (!fecha || !horaInicio) return false;
    return !this.esHorarioPasado(fecha, horaInicio);
  }

  // Validar si el horario de término es válido
  esHorarioTerminoValido(): boolean {
    const fecha = this.form.get('fecha')?.value;
    const horaInicio = this.form.get('horaInicio')?.value;
    const horaTermino = this.form.get('horaTermino')?.value;
    
    if (!fecha || !horaInicio || !horaTermino) return false;
    
    // La hora término debe ser posterior a la hora inicio
    return this.compararHoras(horaTermino, horaInicio) > 0;
  }

  // Obtener horas disponibles para término (posteriores a la hora inicio)
  getHorasTerminoDisponibles(): string[] {
    const horaInicio = this.form.get('horaInicio')?.value;
    if (!horaInicio) return this.horas;
    
    return this.horas.filter(hora => this.compararHoras(hora, horaInicio) > 0);
  }

  // Comparar dos horas (retorna 1 si h1 > h2, -1 si h1 < h2, 0 si son iguales)
  private compararHoras(h1: string, h2: string): number {
    const [h1h, h1m] = h1.split(':').map(Number);
    const [h2h, h2m] = h2.split(':').map(Number);
    
    const minutos1 = h1h * 60 + h1m;
    const minutos2 = h2h * 60 + h2m;
    
    if (minutos1 > minutos2) return 1;
    if (minutos1 < minutos2) return -1;
    return 0;
  }

  formatoMoneda(n: number): string {
    return n.toLocaleString('es-CL', { style: 'currency', currency: 'CLP', maximumFractionDigits: 0 });
  }

  // Función de depuración para diagnosticar problemas de fecha/hora
  debugFechaHora(fecha: string, hora: string): void {
    const hoy = new Date();
    const [año, mes, dia] = fecha.split('-').map(Number);
    const fechaReserva = new Date(año, mes - 1, dia);
    const [horaH, horaM] = hora.split(':').map(Number);
    const horarioReserva = new Date();
    horarioReserva.setHours(horaH, horaM, 0, 0);
    
    console.log('=== DEBUG FECHA/HORA ===');
    console.log('Fecha seleccionada:', fecha);
    console.log('Hora seleccionada:', hora);
    console.log('Hoy:', hoy.toISOString());
    console.log('Fecha reserva:', fechaReserva.toISOString());
    console.log('Horario reserva:', horarioReserva.toISOString());
    console.log('Es fecha pasada:', this.esFechaPasada(fecha));
    console.log('Es horario pasado:', this.esHorarioPasado(fecha, hora));
    console.log('========================');
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

  /**
   * Redirige a Webpay con el token usando POST
   */
  private redirectToWebpay(webpayUrl: string, token: string): void {
    // Crear un formulario dinámico para enviar el token como POST
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = webpayUrl;
    form.style.display = 'none';

    // Crear input para el token
    const tokenInput = document.createElement('input');
    tokenInput.type = 'hidden';
    tokenInput.name = 'token_ws';
    tokenInput.value = token;

    form.appendChild(tokenInput);
    document.body.appendChild(form);

    console.log('🔄 Enviando token a Webpay:', token.substring(0, 20) + '...');
    
    // Enviar el formulario
    form.submit();
  }
}
