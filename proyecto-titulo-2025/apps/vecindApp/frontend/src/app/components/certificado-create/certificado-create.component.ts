import { Component, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, FormGroup, Validators } from '@angular/forms';
import { Subscription } from 'rxjs';
import { AuthService } from '../../services/auth.service';
import { CertificadoService } from '../../services/certificado.service';
import { UserLoginData } from '../../interfaces/auth.interface';
import { 
  CertificadoPedidoResponse, 
  CertificadoResponse, 
  MotivoGrupo 
} from '../../interfaces/certificado.interface';
import { CertificadoConPagoResponse } from '../../interfaces/payment.interface';

@Component({
  selector: 'app-certificado-create',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './certificado-create.component.html',
  styleUrls: ['./certificado-create.component.css'],
})
export class CertificadoCreateComponent implements OnInit, OnDestroy {
  form!: FormGroup;
  currentUser: UserLoginData | null = null;
  sub = new Subscription();
  
  // Estados del componente
  isLoading = false;
  errorMessage = '';
  successMessage = '';
  
  // Estados del proceso
  solicitudCreada: CertificadoPedidoResponse | null = null;
  certificadoGenerado: CertificadoResponse | null = null;
  certificadoConPago: CertificadoConPagoResponse | null = null;
  
  // Estados de los botones
  puedeGenerar = false;
  puedeDescargar = false;

  // Fecha de emisión (hoy)
  today = new Date();
  fechaEmisionTexto = this.today.toLocaleDateString('es-CL', {
    day: '2-digit', month: '2-digit', year: 'numeric'
  });

  // Catálogo de motivos (grupos y opciones) - mantengo los que ya tienes
  motivosCatalog: MotivoGrupo[] = [
  {
    grupo: 'Trámites ante instituciones públicas',
    items: [
      'Postulación a beneficios sociales (Registro Social de Hogares, subsidios habitacionales, bonos)',
      'Procesos en municipalidades (inscripción en juntas de vecinos, becas municipales o ayudas sociales)',
      'Solicitudes en el SII o Tesorería para acreditar domicilio tributario',
    ],
  },
  {
    grupo: 'Procesos judiciales o notariales',
    items: [
      'Juicios civiles, laborales o de familia (para demostrar residencia)',
      'Trámites de posesión efectiva, herencias o escrituras',
      'Cambio de domicilio en causas judiciales',
    ],
  },
  {
    grupo: 'Trámites migratorios',
    items: [
      'Acreditar residencia ante el Servicio Nacional de Migraciones',
      'Solicitudes de permanencia definitiva, visados o nacionalización',
    ],
  },
  {
    grupo: 'Instituciones privadas',
    items: [
      'Bancos o financieras (abrir cuentas, solicitar créditos)',
      'Aseguradoras o instituciones educativas para validar dirección',
    ],
  },
  {
    grupo: 'Otros casos prácticos',
    items: [
      'Postulación a colegios con criterios de cercanía',
      'Contratos de arriendo o servicios básicos sin boletas propias',
    ],
  },
];

  constructor(
    private fb: FormBuilder, 
    private auth: AuthService,
    private certificadoService: CertificadoService
  ) {}

  ngOnInit(): void {
    this.form = this.fb.group({
      motivo: ['', Validators.required],
      confirmo: [false],
    }); 

    this.sub.add(this.auth.currentUser$.subscribe(u => {
      this.currentUser = u;
      this.checkFormState();
    }));
    
    // Escuchar cambios en el formulario para actualizar estados
    this.sub.add(this.form.valueChanges.subscribe(() => {
      this.checkFormState();
    }));
  }

  ngOnDestroy(): void { this.sub.unsubscribe(); }

  // Helpers de solo lectura
  get nombreCompleto(): string {
    const u = this.currentUser;
    if (!u) return '';
    return `${u.nombres} ${u.apellido_paterno} ${u.apellido_materno ?? ''}`.trim();
  }
  get rut(): string       { return this.currentUser?.vecino?.rut ?? ''; }
  get direccion(): string { return this.currentUser?.vecino?.direccion ?? ''; }
  get comuna(): string    { return this.currentUser?.vecino?.comuna ?? ''; }
  get region(): string    { return this.currentUser?.vecino?.region ?? ''; }
  get telefono(): string  { return this.currentUser?.vecino?.telefono ?? ''; }
  get junta(): string     { return this.currentUser?.vecino?.junta ?? ''; }




  /**
   * Verifica el estado del formulario y actualiza los botones
   */
  private checkFormState(): void {
    const motivoValido = this.form.get('motivo')?.valid;
    const confirmado = this.form.get('confirmo')?.value;
    
    this.puedeGenerar = !!(motivoValido && confirmado && !this.isLoading);
    this.puedeDescargar = !!(this.certificadoGenerado && !this.isLoading);
  }

  /**
   * Maneja el click del botón "Generar Certificado" - NUEVO: con Webpay
   */
  onGenerarClick(): void {
    if (!this.puedeGenerar) return;
    
    this.clearMessages();
    this.isLoading = true;
    
    const motivo = this.form.get('motivo')?.value;
    
    // NUEVO: Solicitar certificado con Webpay
    const request = {
      motivo_solicitud: motivo
    };
    
    this.sub.add(
      this.certificadoService.solicitarCertificadoConWebpay(request)
        .subscribe({
          next: (response) => {
            console.log('✅ Certificado con Webpay creado:', response);
            this.certificadoConPago = response;
            this.successMessage = `Solicitud creada. Redirigiendo al pago con Webpay de $${response.payment_intent.amount} CLP...`;
            this.isLoading = false;
            this.checkFormState();
            
            // Redirigir a Webpay después de 2 segundos
            setTimeout(() => {
              if (response.webpay_token) {
                this.redirectToWebpay(response.payment_url, response.webpay_token);
              } else {
                console.error('❌ Token de Webpay no encontrado en la respuesta');
                this.errorMessage = 'Error: No se pudo obtener el token de pago';
                this.isLoading = false;
                this.checkFormState();
              }
            }, 2000);
          },
          error: (error) => {
            console.error('❌ Error creando certificado con Webpay:', error);
            this.errorMessage = error.message || 'Error al crear la solicitud de certificado';
            this.isLoading = false;
            this.checkFormState();
          }
        })
    );
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

  /**
   * Maneja el click del botón "Descargar PDF"
   */
  onDescargarClick(): void {
    if (!this.certificadoGenerado || !this.puedeDescargar) return;
    
    this.clearMessages();
    this.isLoading = true;
    
    this.sub.add(
      this.certificadoService.descargarCertificadoPDF(this.certificadoGenerado.id_certificado)
        .subscribe({
          next: (blob) => {
            console.log('✅ PDF descargado');
            const filename = `certificado_residencia_${this.certificadoGenerado!.numero}.pdf`;
            this.certificadoService.downloadBlob(blob, filename);
            this.successMessage = 'PDF descargado exitosamente';
            this.isLoading = false;
            this.checkFormState();
          },
          error: (error) => {
            console.error('❌ Error descargando PDF:', error);
            this.errorMessage = error.message || 'Error al descargar el PDF';
            this.isLoading = false;
            this.checkFormState();
          }
        })
    );
  }

  /**
   * Limpia los mensajes de error y éxito
   */
  clearMessages(): void {
    this.errorMessage = '';
    this.successMessage = '';
  }

  /**
   * Resetea el formulario para una nueva solicitud
   */
  onNuevaSolicitud(): void {
    this.form.reset();
    this.solicitudCreada = null;
    this.certificadoGenerado = null;
    this.clearMessages();
    this.checkFormState();
  }
}
