import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { PaymentService } from '../../services/payment.service';

@Component({
  selector: 'app-payment-failure',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="container mt-5">
      <div class="row justify-content-center">
        <div class="col-md-8">
          <!-- Fallo -->
          <div class="card border-danger">
            <div class="card-header bg-danger text-white text-center">
              <i class="bi bi-x-circle-fill fs-1"></i>
              <h3 class="mt-2">Pago No Completado</h3>
            </div>
            <div class="card-body text-center">
              <h5 class="card-title text-danger">El pago no pudo ser procesado</h5>
              <p class="card-text">
                No te preocupes, tu solicitud de certificado sigue activa.
                Puedes intentar pagar nuevamente cuando quieras.
              </p>
              
              <!-- Información del error -->
              <div class="alert alert-warning" *ngIf="errorReason">
                <h6><i class="bi bi-info-circle"></i> Motivo</h6>
                <p>{{ errorReason }}</p>
              </div>
              
              <!-- Información útil -->
              <div class="alert alert-info">
                <h6><i class="bi bi-lightbulb"></i> ¿Qué puedes hacer?</h6>
                <ul class="text-start">
                  <li>Verificar que tu tarjeta tenga fondos suficientes</li>
                  <li>Comprobar que los datos ingresados sean correctos</li>
                  <li>Intentar con otra tarjeta o método de pago</li>
                  <li>Contactar a tu banco si el problema persiste</li>
                </ul>
              </div>
              
              <!-- Acciones -->
              <div class="mt-4">
                <button class="btn btn-primary me-2" (click)="intentarNuevamente()">
                  <i class="bi bi-credit-card"></i> Intentar Pago Nuevamente
                </button>
                <button class="btn btn-outline-secondary me-2" (click)="irACertificados()">
                  <i class="bi bi-list"></i> Ver Mis Solicitudes
                </button>
                <button class="btn btn-outline-primary" (click)="irAInicio()">
                  <i class="bi bi-house"></i> Ir al Inicio
                </button>
              </div>
            </div>
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
    ul {
      margin-bottom: 0;
    }
  `]
})
export class PaymentFailureComponent implements OnInit {
  errorReason = '';
  
  // Parámetros de la URL
  paymentId: string | null = null;
  preferenceId: string | null = null;
  status: string | null = null;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private paymentService: PaymentService
  ) {}

  ngOnInit() {
    // Obtener parámetros de MercadoPago
    this.route.queryParams.subscribe(params => {
      this.paymentId = params['payment_id'] || null;
      this.preferenceId = params['preference_id'] || null;
      this.status = params['status'] || null;
      
      
      // Determinar motivo del error
      this.determinarMotivo(params);
    });
  }

  private determinarMotivo(params: any) {
    const status = params['status'];
    const statusDetail = params['status_detail'];
    
    switch (status) {
      case 'rejected':
        if (statusDetail === 'cc_rejected_insufficient_amount') {
          this.errorReason = 'Fondos insuficientes en la tarjeta';
        } else if (statusDetail === 'cc_rejected_bad_filled_card_number') {
          this.errorReason = 'Número de tarjeta incorrecto';
        } else if (statusDetail === 'cc_rejected_bad_filled_date') {
          this.errorReason = 'Fecha de vencimiento incorrecta';
        } else if (statusDetail === 'cc_rejected_bad_filled_security_code') {
          this.errorReason = 'Código de seguridad incorrecto';
        } else {
          this.errorReason = 'El pago fue rechazado por el banco';
        }
        break;
      case 'cancelled':
        this.errorReason = 'El pago fue cancelado';
        break;
      default:
        this.errorReason = 'No se pudo completar el pago. Inténtalo nuevamente.';
    }
  }

  intentarNuevamente() {
    // Volver a la página de creación de certificados para reintentar
    this.router.navigate(['/certificados/residencia/crear']);
  }

  irACertificados() {
    this.router.navigate(['/certificados']);
  }

  irAInicio() {
    this.router.navigate(['/']);
  }
}
