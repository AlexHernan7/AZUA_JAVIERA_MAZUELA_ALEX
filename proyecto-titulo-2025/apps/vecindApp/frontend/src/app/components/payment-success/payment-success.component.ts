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
    <div class="container mt-5">
      <div class="row justify-content-center">
        <div class="col-md-8">
          <!-- Éxito -->
          <div class="card border-success" *ngIf="!isLoading">
            <div class="card-header bg-success text-white text-center">
              <i class="bi bi-check-circle-fill fs-1"></i>
              <h3 class="mt-2">¡Pago Exitoso!</h3>
            </div>
            <div class="card-body text-center">
              <h5 class="card-title text-success">Tu certificado está siendo procesado</h5>
              <p class="card-text">
                El pago de <strong>\${{ paymentAmount | number:'1.0-0' }} CLP</strong> 
                ha sido procesado exitosamente.
              </p>
              
              <!-- Información del certificado -->
              <div class="alert alert-info" *ngIf="certificado">
                <h6><i class="bi bi-file-earmark-text"></i> Certificado Generado</h6>
                <p><strong>Número:</strong> {{ certificado.numero }}</p>
                <p><strong>Fecha:</strong> {{ certificado.fecha_emision | date:'dd/MM/yyyy' }}</p>
                <button class="btn btn-primary" (click)="descargarCertificado()">
                  <i class="bi bi-download"></i> Descargar PDF
                </button>
              </div>
              
              <!-- Si aún no está listo -->
              <div class="alert alert-warning" *ngIf="!certificado && paymentStatus">
                <h6><i class="bi bi-clock"></i> Procesando...</h6>
                <p>Tu certificado se está generando. Esto puede tomar unos momentos.</p>
                <button class="btn btn-outline-primary" (click)="verificarEstado()">
                  <i class="bi bi-arrow-clockwise"></i> Verificar Estado
                </button>
              </div>
              
              <!-- Acciones -->
              <div class="mt-4">
                <button class="btn btn-outline-secondary me-2" (click)="irACertificados()">
                  <i class="bi bi-list"></i> Ver Mis Certificados
                </button>
                <button class="btn btn-primary" (click)="irAInicio()">
                  <i class="bi bi-house"></i> Ir al Inicio
                </button>
              </div>
            </div>
          </div>
          
          <!-- Loading -->
          <div class="text-center" *ngIf="isLoading">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Cargando...</span>
            </div>
            <p class="mt-2">Verificando el estado del pago...</p>
          </div>
          
          <!-- Error -->
          <div class="alert alert-danger" *ngIf="errorMessage">
            <h6><i class="bi bi-exclamation-triangle"></i> Error</h6>
            <p>{{ errorMessage }}</p>
            <button class="btn btn-outline-danger" (click)="reintentar()">
              <i class="bi bi-arrow-clockwise"></i> Reintentar
            </button>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .card {
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .bi {
      font-size: 1.2em;
    }
  `]
})
export class PaymentSuccessComponent implements OnInit {
  isLoading = true;
  errorMessage = '';
  paymentStatus: PaymentStatusResponse | null = null;
  certificado: CertificadoResponse | null = null;
  paymentAmount = 0;
  
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
    // Obtener parámetros de MercadoPago
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
    
    // Por ahora, simulamos que el pago fue exitoso
    // En una implementación real, aquí consultarías el estado del pago
    setTimeout(() => {
      this.isLoading = false;
      this.paymentAmount = 1000; // $1.000 CLP
      
      // Simular que el certificado ya está listo
      // En la implementación real, consultarías el estado real
      this.verificarCertificado();
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

  irAInicio() {
    this.router.navigate(['/']);
  }
}
