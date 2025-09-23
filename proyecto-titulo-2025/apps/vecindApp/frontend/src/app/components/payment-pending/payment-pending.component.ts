import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';

@Component({
  selector: 'app-payment-pending',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="container mt-5">
      <div class="row justify-content-center">
        <div class="col-md-8">
          <!-- Pendiente -->
          <div class="card border-warning">
            <div class="card-header bg-warning text-dark text-center">
              <i class="bi bi-clock-fill fs-1"></i>
              <h3 class="mt-2">Pago Pendiente</h3>
            </div>
            <div class="card-body text-center">
              <h5 class="card-title text-warning">Tu pago está siendo procesado</h5>
              <p class="card-text">
                El pago está pendiente de confirmación. 
                Esto puede tomar unos minutos dependiendo del método de pago utilizado.
              </p>
              
              <!-- Información -->
              <div class="alert alert-info">
                <h6><i class="bi bi-info-circle"></i> ¿Qué significa esto?</h6>
                <ul class="text-start">
                  <li><strong>Transferencia bancaria:</strong> Puede tardar hasta 2 días hábiles</li>
                  <li><strong>Efectivo:</strong> El pago debe completarse en el punto de pago</li>
                  <li><strong>Tarjeta:</strong> Verificación adicional requerida</li>
                </ul>
              </div>
              
              <!-- Instrucciones -->
              <div class="alert alert-warning">
                <h6><i class="bi bi-exclamation-triangle"></i> Importante</h6>
                <p>
                  <strong>No cierres esta ventana</strong> hasta que el pago se complete.
                  Te notificaremos cuando el certificado esté listo.
                </p>
              </div>
              
              <!-- Auto-refresh -->
              <div class="mb-3" *ngIf="isChecking">
                <div class="spinner-border spinner-border-sm text-primary me-2" role="status">
                  <span class="visually-hidden">Verificando...</span>
                </div>
                <small class="text-muted">Verificando estado cada {{ checkInterval / 1000 }} segundos...</small>
              </div>
              
              <!-- Acciones -->
              <div class="mt-4">
                <button class="btn btn-primary me-2" (click)="verificarAhora()" [disabled]="isChecking">
                  <i class="bi bi-arrow-clockwise"></i> 
                  {{ isChecking ? 'Verificando...' : 'Verificar Ahora' }}
                </button>
                <button class="btn btn-outline-secondary me-2" (click)="irACertificados()">
                  <i class="bi bi-list"></i> Ver Mis Solicitudes
                </button>
                <button class="btn btn-outline-primary" (click)="irAInicio()">
                  <i class="bi bi-house"></i> Ir al Inicio
                </button>
              </div>
              
              <!-- Countdown -->
              <div class="mt-3">
                <small class="text-muted">
                  Próxima verificación en: {{ countdown }} segundos
                </small>
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
export class PaymentPendingComponent implements OnInit {
  isChecking = false;
  checkInterval = 30000; // 30 segundos
  countdown = 30;
  
  private intervalId: any;
  private countdownId: any;
  
  // Parámetros de la URL
  paymentId: string | null = null;
  preferenceId: string | null = null;
  status: string | null = null;

  constructor(
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit() {
    // Obtener parámetros de MercadoPago
    this.route.queryParams.subscribe(params => {
      this.paymentId = params['payment_id'] || null;
      this.preferenceId = params['preference_id'] || null;
      this.status = params['status'] || null;
      
      console.log('⏳ Parámetros de pago pendiente:', params);
    });
    
    // Iniciar verificación automática
    this.iniciarVerificacionAutomatica();
  }

  ngOnDestroy() {
    // Limpiar intervalos
    if (this.intervalId) {
      clearInterval(this.intervalId);
    }
    if (this.countdownId) {
      clearInterval(this.countdownId);
    }
  }

  private iniciarVerificacionAutomatica() {
    // Verificar cada 30 segundos
    this.intervalId = setInterval(() => {
      this.verificarAhora();
    }, this.checkInterval);
    
    // Countdown
    this.iniciarCountdown();
  }

  private iniciarCountdown() {
    this.countdown = this.checkInterval / 1000;
    this.countdownId = setInterval(() => {
      this.countdown--;
      if (this.countdown <= 0) {
        this.countdown = this.checkInterval / 1000;
      }
    }, 1000);
  }

  verificarAhora() {
    this.isChecking = true;
    
    // Simular verificación
    setTimeout(() => {
      this.isChecking = false;
      
      // En una implementación real, aquí consultarías el estado del pago
      // Si el pago se completó, redirigir a success
      // Si falló, redirigir a failure
      
      console.log('🔄 Verificación de estado completada');
    }, 2000);
  }

  irACertificados() {
    this.router.navigate(['/certificados']);
  }

  irAInicio() {
    this.router.navigate(['/']);
  }
}
