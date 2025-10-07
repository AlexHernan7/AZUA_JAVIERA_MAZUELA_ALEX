import { Component, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, FormGroup, Validators } from '@angular/forms';
import { Subscription } from 'rxjs';
import { AuthService } from '../../services/auth.service';
import { CertificadoService } from '../../services/certificado.service';
import { MasterService, MotivoSolicitudResponse, MotivoGrupoResponse } from '../../services/master.service';
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

  // Motivos obtenidos del backend
  motivos: MotivoSolicitudResponse[] = [];
  motivosAgrupados: { [grupo: string]: MotivoSolicitudResponse[] } = {};

  // Getter para verificar si hay motivos cargados
  get tieneMotivos(): boolean {
    return Object.keys(this.motivosAgrupados).length > 0;
  }

  constructor(
    private fb: FormBuilder, 
    private auth: AuthService,
    private certificadoService: CertificadoService,
    private masterService: MasterService
  ) {}

  ngOnInit(): void {
    this.form = this.fb.group({
      id_motivo: ['', Validators.required],
      confirmo: [false],
    }); 

    this.sub.add(this.auth.currentUser$.subscribe(u => {
      this.currentUser = u;
      this.checkFormState();
    }));

    // Cargar motivos del backend
    this.cargarMotivos();
    
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
    const motivoValido = this.form.get('id_motivo')?.valid;
    const confirmado = this.form.get('confirmo')?.value;
    
    this.puedeGenerar = !!(motivoValido && confirmado && !this.isLoading);
    this.puedeDescargar = !!(this.certificadoGenerado && !this.isLoading);
  }

  /**
   * Carga los motivos de solicitud desde el backend
   */
  cargarMotivos(): void {
    console.log('🔄 Cargando motivos desde el backend...');
    this.sub.add(
      this.masterService.getMotivosSolicitudAgrupados()
        .subscribe({
          next: (response) => {
            console.log('✅ Respuesta del backend:', response);
            
            // Convertir array de grupos a objeto con claves
            this.motivosAgrupados = {};
            response.grupos.forEach((grupo: MotivoGrupoResponse) => {
              this.motivosAgrupados[grupo.grupo] = grupo.items;
            });
            
            // Crear lista plana de motivos para búsqueda
            this.motivos = response.grupos.flatMap((grupo: MotivoGrupoResponse) => grupo.items);
            
            console.log('✅ Motivos cargados:', this.motivos);
            console.log('✅ Motivos agrupados:', this.motivosAgrupados);
          },
          error: (error) => {
            console.error('❌ Error cargando motivos:', error);
            console.error('❌ Error completo:', error);
            this.errorMessage = 'Error al cargar los motivos de solicitud: ' + error.message;
          }
        })
    );
  }

  /**
   * Maneja el click del botón "Generar Certificado" - NUEVO: con Webpay
   */
  onGenerarClick(): void {
    if (!this.puedeGenerar) return;
    
    this.clearMessages();
    this.isLoading = true;
    
    const id_motivo = this.form.get('id_motivo')?.value;
    
    // NUEVO: Solicitar certificado con Webpay
    const request = {
      id_motivo: id_motivo
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
