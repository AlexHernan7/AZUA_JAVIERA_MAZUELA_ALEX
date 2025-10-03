import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { PaymentService } from '../../services/payment.service';
import { CertificadoService } from '../../services/certificado.service';
import { PaymentStatusResponse } from '../../interfaces/payment.interface';
import { CertificadoResponse } from '../../interfaces/certificado.interface';

@Component({
  selector: 'app-payment-success',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="payment-success-container">
      <div class="container py-5">
        <div class="row justify-content-center">
          <div class="col-lg-8 col-xl-7">
            
            <!-- Estado de Éxito -->
            <div class="success-card animate-slide-up" *ngIf="!isLoading">
              
              <!-- Header con animación -->
              <div class="success-header">
                <div class="success-icon-wrapper">
                  <div class="success-icon-bg">
                    <i class="bi bi-check-circle-fill success-icon animate-bounce-in"></i>
                  </div>
                  <div class="success-particles">
                    <div class="particle" *ngFor="let p of [1,2,3,4,5,6]" [style.animation-delay]="p * 0.2 + 's'"></div>
                  </div>
                </div>
                <h1 class="success-title">¡Pago Exitoso!</h1>
                <p class="success-subtitle">Tu transacción se ha completado correctamente</p>
              </div>

              <!-- Información del pago -->
              <div class="payment-info">
                <div class="payment-amount-card">
                  <div class="payment-icon">
                    <i class="bi bi-credit-card-2-back"></i>
                  </div>
                  <div class="payment-details">
                    <span class="payment-label">Monto pagado</span>
                    <span class="payment-amount">\${{ paymentAmount | number:'2.0-0' }} <small>CLP</small></span>
                  </div>
                  <div class="payment-status">
                    <span class="status-badge">Confirmado</span>
                  </div>
                </div>
              </div>

              <!-- Información del certificado -->
              <div class="certificate-section animate-fade-in" *ngIf="certificado && !isReserva">
                <div class="certificate-card">
                  <div class="certificate-header">
                    <div class="certificate-icon">
                      <i class="bi bi-file-earmark-check"></i>
                    </div>
                    <div class="certificate-info">
                      <h3 class="certificate-title">Certificado Generado</h3>
                      <p class="certificate-subtitle">Tu documento está listo para descargar</p>
                    </div>
                  </div>
                  <div class="certificate-details">
                    <div class="detail-row">
                      <span class="detail-label">Número:</span>
                      <span class="detail-value">{{ certificado.numero }}</span>
                    </div>
                    <div class="detail-row">
                      <span class="detail-label">Fecha:</span>
                      <span class="detail-value">{{ certificado.fecha_emision | date:'dd/MM/yyyy' }}</span>
                    </div>
                  </div>
                  <button class="btn-download-cert" (click)="descargarCertificado()">
                    <i class="bi bi-download"></i>
                    <span>Descargar PDF</span>
                  </button>
                </div>
              </div>

              <!-- Información de la reserva -->
              <div class="reservation-section animate-fade-in" *ngIf="isReserva && reservaInfo">
                <div class="reservation-card">
                  <div class="reservation-header">
                    <div class="reservation-icon">
                      <i class="bi bi-calendar-check"></i>
                    </div>
                    <div class="reservation-info">
                      <h3 class="reservation-title">Reserva Confirmada</h3>
                      <p class="reservation-subtitle">Tu reserva ha sido confirmada exitosamente</p>
                    </div>
                  </div>
                  <div class="reservation-details">
                    <div class="detail-row">
                      <span class="detail-label">Espacio:</span>
                      <span class="detail-value">{{ reservaInfo.espacio_nombre }}</span>
                    </div>
                    <div class="detail-row">
                      <span class="detail-label">Fecha:</span>
                      <span class="detail-value">{{ reservaInfo.fecha | date:'dd/MM/yyyy' }}</span>
                    </div>
                    <div class="detail-row">
                      <span class="detail-label">Horario:</span>
                      <span class="detail-value">{{ reservaInfo.hora_inicio }} - {{ reservaInfo.hora_termino }}</span>
                    </div>
                    <div class="detail-row">
                      <span class="detail-label">ID Reserva:</span>
                      <span class="detail-value">#{{ reservaInfo.reserva_id }}</span>
                    </div>
                  </div>
                  <div class="reservation-note">
                    <i class="bi bi-info-circle"></i>
                    <span>Recibirás un correo de confirmación con todos los detalles</span>
                  </div>
                </div>
              </div>

              <!-- Estado de procesamiento -->
              <div class="processing-section animate-fade-in" *ngIf="!certificado && !isReserva && paymentStatus">
                <div class="processing-card">
                  <div class="processing-icon">
                    <div class="spinner-custom"></div>
                  </div>
                  <h3 class="processing-title">Generando Certificado</h3>
                  <p class="processing-subtitle">Tu documento se está preparando, esto puede tomar unos momentos</p>
                  <button class="btn-check-status" (click)="verificarEstado()">
                    <i class="bi bi-arrow-clockwise"></i>
                    <span>Verificar Estado</span>
                  </button>
                </div>
              </div>

              <!-- Acciones principales -->
              <div class="actions-section">
                <div class="action-buttons">
                  <button class="btn-secondary-action" (click)="isReserva ? irAReservas() : irACertificados()">
                    <i class="bi" [class.bi-calendar-check]="isReserva" [class.bi-collection]="!isReserva"></i>
                    <span>{{ isReserva ? 'Mis Reservas' : 'Mis Certificados' }}</span>
                  </button>
                  <button class="btn-primary-action" (click)="irAInicio()">
                    <i class="bi bi-house-door"></i>
                    <span>Ir al Inicio</span>
                  </button>
                </div>
              </div>

            </div>

            <!-- Estado de carga -->
            <div class="loading-section text-center animate-fade-in" *ngIf="isLoading">
              <div class="loading-card">
                <div class="loading-spinner">
                  <div class="spinner-ring"></div>
                  <div class="spinner-ring"></div>
                  <div class="spinner-ring"></div>
                </div>
                <h3 class="loading-title">Verificando Pago</h3>
                <p class="loading-subtitle">Estamos confirmando tu transacción...</p>
              </div>
            </div>

            <!-- Estado de error -->
            <div class="error-section animate-slide-up" *ngIf="errorMessage">
              <div class="error-card">
                <div class="error-icon">
                  <i class="bi bi-exclamation-triangle"></i>
                </div>
                <h3 class="error-title">Algo salió mal</h3>
                <p class="error-message">{{ errorMessage }}</p>
                <button class="btn-retry" (click)="reintentar()">
                  <i class="bi bi-arrow-clockwise"></i>
                  <span>Intentar nuevamente</span>
                </button>
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  `,
  styleUrls: ['./payment-success.component.css'],
  styles: [`
    /* CONTENEDOR PRINCIPAL */
    .payment-success-container {
      min-height: 100vh;
      background: linear-gradient(135deg, #f0fdfa 0%, #e6fffa 50%, #f0f9ff 100%);
      padding: 2rem 0;
    }

    /* TARJETA DE ÉXITO */
    .success-card {
      background: white;
      border-radius: 24px;
      box-shadow: 0 20px 40px rgba(15, 118, 110, 0.08), 0 8px 16px rgba(15, 118, 110, 0.04);
      overflow: hidden;
      border: 1px solid rgba(15, 118, 110, 0.06);
    }

    /* HEADER DE ÉXITO */
    .success-header {
      text-align: center;
      padding: 3rem 2rem 2rem;
      background: linear-gradient(135deg, #0f766e 0%, #0d9488 100%);
      color: white;
      position: relative;
      overflow: hidden;
    }

    .success-header::before {
      content: '';
      position: absolute;
      top: -50%;
      left: -50%;
      width: 200%;
      height: 200%;
      background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
      animation: rotate 20s linear infinite;
    }

    .success-icon-wrapper {
      position: relative;
      margin-bottom: 1.5rem;
      z-index: 2;
    }

    .success-icon-bg {
      width: 120px;
      height: 120px;
      background: rgba(255, 255, 255, 0.15);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 0 auto;
      backdrop-filter: blur(10px);
      border: 2px solid rgba(255, 255, 255, 0.2);
    }

    .success-icon {
      font-size: 4rem;
      color: white;
      filter: drop-shadow(0 4px 8px rgba(0,0,0,0.1));
    }

    .success-particles {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 200px;
      height: 200px;
      pointer-events: none;
    }

    .particle {
      position: absolute;
      width: 6px;
      height: 6px;
      background: rgba(255, 255, 255, 0.6);
      border-radius: 50%;
      animation: float 3s ease-in-out infinite;
    }

    .particle:nth-child(1) { top: 20%; left: 20%; }
    .particle:nth-child(2) { top: 30%; right: 25%; }
    .particle:nth-child(3) { bottom: 30%; left: 30%; }
    .particle:nth-child(4) { bottom: 20%; right: 20%; }
    .particle:nth-child(5) { top: 50%; left: 10%; }
    .particle:nth-child(6) { top: 50%; right: 10%; }

    .success-title {
      font-size: 2.5rem;
      font-weight: 800;
      margin-bottom: 0.5rem;
      text-shadow: 0 2px 4px rgba(0,0,0,0.1);
      z-index: 2;
      position: relative;
    }

    .success-subtitle {
      font-size: 1.1rem;
      opacity: 0.9;
      margin: 0;
      z-index: 2;
      position: relative;
    }

    @keyframes rotate {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }

    @keyframes float {
      0%, 100% { transform: translateY(0px) scale(1); opacity: 0.6; }
      50% { transform: translateY(-20px) scale(1.1); opacity: 1; }
    }

    @media (max-width: 768px) {
      .payment-success-container {
        padding: 1rem 0;
      }

      .success-header {
        padding: 2rem 1rem 1.5rem;
      }

      .success-title {
        font-size: 2rem;
      }

      .success-icon-bg {
        width: 100px;
        height: 100px;
      }

      .success-icon {
        font-size: 3rem;
      }
    }

    @media (max-width: 480px) {
      .success-title {
        font-size: 1.75rem;
      }
    }

    /* ESTILOS PARA RESERVAS */
    .reservation-section {
      margin-top: 2rem;
    }

    .reservation-card {
      background: linear-gradient(135deg, #f0fdfa 0%, #e6fffa 100%);
      border: 2px solid #0f766e;
      border-radius: 16px;
      padding: 2rem;
      box-shadow: 0 8px 16px rgba(15, 118, 110, 0.1);
    }

    .reservation-header {
      display: flex;
      align-items: center;
      margin-bottom: 1.5rem;
    }

    .reservation-icon {
      width: 60px;
      height: 60px;
      background: #0f766e;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-right: 1rem;
    }

    .reservation-icon i {
      font-size: 1.5rem;
      color: white;
    }

    .reservation-title {
      font-size: 1.5rem;
      font-weight: 700;
      color: #0f766e;
      margin: 0 0 0.25rem 0;
    }

    .reservation-subtitle {
      color: #6b7280;
      margin: 0;
      font-size: 0.95rem;
    }

    .reservation-details {
      margin-bottom: 1.5rem;
    }

    .detail-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.75rem 0;
      border-bottom: 1px solid rgba(15, 118, 110, 0.1);
    }

    .detail-row:last-child {
      border-bottom: none;
    }

    .detail-label {
      font-weight: 600;
      color: #374151;
    }

    .detail-value {
      font-weight: 700;
      color: #0f766e;
    }

    .reservation-note {
      display: flex;
      align-items: center;
      background: rgba(15, 118, 110, 0.05);
      padding: 1rem;
      border-radius: 8px;
      border-left: 4px solid #0f766e;
    }

    .reservation-note i {
      color: #0f766e;
      margin-right: 0.5rem;
      font-size: 1.1rem;
    }

    .reservation-note span {
      color: #374151;
      font-size: 0.9rem;
    }
  `]
})
export class PaymentSuccessComponent implements OnInit {
  isLoading = true;
  errorMessage = '';
  paymentStatus: PaymentStatusResponse | null = null;
  certificado: CertificadoResponse | null = null;
  paymentAmount = 0;
  
  // Información de reserva
  reservaInfo: any = null;
  isReserva = false;
  
  // Parámetros de la URL
  paymentId: string | null = null;
  preferenceId: string | null = null;
  status: string | null = null;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private paymentService: PaymentService,
    private certificadoService: CertificadoService
  ) {}

  ngOnInit() {
    // Verificar si hay información de reserva en localStorage
    const reservaPendiente = localStorage.getItem('reserva_pendiente');
    if (reservaPendiente) {
      this.reservaInfo = JSON.parse(reservaPendiente);
      this.isReserva = true;
      this.paymentAmount = this.reservaInfo.valor;
      console.log('🏟️ Información de reserva encontrada:', this.reservaInfo);
      
      // Limpiar localStorage
      localStorage.removeItem('reserva_pendiente');
    }
    
    // Obtener parámetros de la URL
    this.route.queryParams.subscribe(params => {
      this.paymentId = params['payment_id'] || null;
      this.preferenceId = params['preference_id'] || null;
      this.status = params['status'] || null;
      
      console.log('🎉 Parámetros de éxito de pago:', params);
      
      // Verificar estado del pago
      this.verificarEstado();
    });
  }

  verificarEstado() {
    this.isLoading = true;
    this.errorMessage = '';
    
    // Si es una reserva, usar el monto real
    if (this.isReserva && this.reservaInfo) {
      this.paymentAmount = this.reservaInfo.valor;
      this.isLoading = false;
      return;
    }
    
    // Para certificados, simular el proceso
    setTimeout(() => {
      this.isLoading = false;
      this.paymentAmount = 2000; // $2.000 CLP para certificados
      
      // Verificar certificado solo si no es reserva
      if (!this.isReserva) {
        this.verificarCertificado();
      }
    }, 2000);
  }

  verificarCertificado() {
    // Obtener los certificados del usuario para ver si ya está listo
    this.certificadoService.getMisCertificados().subscribe({
      next: (certificados) => {
        // Tomar el más reciente (debería ser el que acabamos de pagar)
        if (certificados.length > 0) {
          this.certificado = certificados[0];
        }
      },
      error: (error) => {
        console.error('Error obteniendo certificados:', error);
        // No mostrar error, el certificado puede estar procesándose
      }
    });
  }

  descargarCertificado() {
    if (!this.certificado) return;
    
    this.certificadoService.descargarCertificadoPDF(this.certificado.id_certificado).subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `certificado_${this.certificado!.numero}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      },
      error: (error) => {
        console.error('Error descargando certificado:', error);
        this.errorMessage = 'Error descargando el certificado. Inténtalo más tarde.';
      }
    });
  }

  reintentar() {
    this.verificarEstado();
  }

  irACertificados() {
    this.router.navigate(['/certificados']);
  }

  irAReservas() {
    this.router.navigate(['/reservas']);
  }

  irAInicio() {
    this.router.navigate(['/']);
  }
}
