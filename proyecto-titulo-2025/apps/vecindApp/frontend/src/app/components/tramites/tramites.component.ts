import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { Subject, takeUntil } from 'rxjs';
import { CertificadoService } from '../../services/certificado.service';
import { ReservaService } from '../../services/reserva.service';
import { CertificadoResponse } from '../../interfaces/certificado.interface';
import { ReservaResponse } from '../../interfaces/reserva.interface';

type CertificadoDisplay = {
  titulo: string;
  fecha: string;   // texto formateado
  id: number;
  esUltimo: boolean; // indica si es el último certificado emitido
};

type ReservaDisplay = {
  espacio: string;
  fecha: string;   // texto formateado
  id: number;
};

@Component({
  selector: 'app-tramites',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './tramites.component.html',
  styleUrls: ['./tramites.component.css']
})
export class TramitesComponent implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>();

  certificados: CertificadoDisplay[] = [];
  reservas: ReservaDisplay[] = [];
  
  totalCertificados = 0; // Total real de certificados del vecino
  totalReservas = 0; // Total real de reservas del vecino
  
  isLoading = true;
  errorMessage = '';

  constructor(
    private router: Router,
    private certificadoService: CertificadoService,
    private reservaService: ReservaService
  ) {}

  ngOnInit() {
    this.cargarDatos();
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }

  /**
   * Carga certificados y reservas del usuario
   */
  cargarDatos() {
    this.isLoading = true;
    this.errorMessage = '';

    // Cargar certificados
    this.certificadoService.getMisCertificados()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (certs: CertificadoResponse[]) => {
          // Guardar el total real
          this.totalCertificados = certs.length;

          // Ordenar por fecha de emisión descendente y tomar los primeros 3
          const certsSorted = [...certs].sort((a, b) => {
            const dateA = new Date(a.fecha_emision).getTime();
            const dateB = new Date(b.fecha_emision).getTime();
            return dateB - dateA;
          }).slice(0, 3);

          // Mapear a formato de display
          this.certificados = certsSorted.map((cert, index) => ({
            titulo: `Certificado de Residencia N° ${cert.numero}`,
            fecha: this.formatearFecha(cert.fecha_emision),
            id: cert.id_certificado,
            esUltimo: index === 0 // El primero es el más reciente
          }));
        },
        error: (error) => {
          this.errorMessage = 'Error al cargar certificados';
        }
      });

    // Cargar reservas - primero obtener todas para saber el total
    this.reservaService.getMisReservas(100) // Obtener más para calcular el total
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (reservas: ReservaResponse[]) => {
          // Guardar el total real
          this.totalReservas = reservas.length;

          // Tomar las primeras 3 (ya vienen ordenadas por fecha descendente)
          this.reservas = reservas.slice(0, 3).map(reserva => ({
            espacio: reserva.espacio_nombre || 'Espacio',
            fecha: this.formatearFechaReserva(reserva.inicio, reserva.fin),
            id: reserva.id_reserva
          }));
          this.isLoading = false;
        },
        error: (error) => {
          this.errorMessage = 'Error al cargar reservas';
          this.isLoading = false;
        }
      });
  }

  /**
   * Formatea una fecha ISO a formato legible en español
   */
  formatearFecha(fechaISO: string): string {
    const fecha = new Date(fechaISO);
    return fecha.toLocaleDateString('es-CL', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    });
  }

  /**
   * Formatea una fecha de reserva con rango de horarios (inicio - fin)
   * Extrae la hora directamente del string ISO sin conversión de zona horaria
   */
  formatearFechaReserva(inicioISO: string, finISO: string): string {
    // Parsear manualmente el string ISO para evitar conversión de zona horaria
    // Formato esperado: "2025-10-30T11:00:00+00:00" o "2025-10-30T11:00:00.000000+00:00"
    
    // Extraer fecha y hora de inicio
    const [fechaInicio, horaCompletaInicio] = inicioISO.split('T');
    const horaInicio = horaCompletaInicio.split(':').slice(0, 2).join(':'); // HH:MM
    
    // Extraer hora de fin (solo necesitamos la hora, la fecha es la misma)
    const horaCompletaFin = finISO.split('T')[1];
    const horaFin = horaCompletaFin.split(':').slice(0, 2).join(':'); // HH:MM
    
    // Formatear la fecha usando Date para obtener el formato legible
    const [year, month, day] = fechaInicio.split('-');
    const fecha = new Date(parseInt(year), parseInt(month) - 1, parseInt(day));
    
    const fechaFormateada = fecha.toLocaleDateString('es-CL', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    });

    return `${fechaFormateada}, ${horaInicio} - ${horaFin}`;
  }

  /**
   * Descarga un certificado en PDF
   */
  descargarCertificado(cert: CertificadoDisplay) {
    if (!cert.esUltimo) {
      // Solo el último certificado se puede descargar según requisitos
      return;
    }

    this.certificadoService.descargarCertificadoPDF(cert.id)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (blob: Blob) => {
          this.certificadoService.downloadBlob(blob, `certificado_${cert.id}.pdf`);
        },
        error: (error) => {
          alert('Error al descargar el certificado');
        }
      });
  }

  /**
   * Navega a la página para solicitar un nuevo certificado
   */
  solicitarCertificado() {
    this.router.navigate(['/certificados/residencia/crear']);
  }

  /**
   * Navega a la página para hacer una nueva reserva
   */
  hacerReserva() {
    this.router.navigate(['/reservas']);
  }

  /**
   * Ver detalle de certificado (sin funcionalidad por ahora)
   */
  verDetalleCert(id: number) {
    // No hace nada según requisitos
  }

  /**
   * Ver detalle de reserva (sin funcionalidad por ahora)
   */
  verDetalleReserva(id: number) {
    // No hace nada según requisitos
  }
}
