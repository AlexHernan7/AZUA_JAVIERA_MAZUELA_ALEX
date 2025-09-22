import { Component, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, FormGroup, Validators } from '@angular/forms';
import { Subscription } from 'rxjs';
import { AuthService } from '../../services/auth.service';
import { UserLoginData } from '../../interfaces/auth.interface';

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

  // Fecha de emisión (hoy)
  today = new Date();
  fechaEmisionTexto = this.today.toLocaleDateString('es-CL', {
    day: '2-digit', month: '2-digit', year: 'numeric'
  });

  // Catálogo de motivos (grupos y opciones)
  motivosCatalog = [
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

  constructor(private fb: FormBuilder, private auth: AuthService) {}

  ngOnInit(): void {
    this.form = this.fb.group({
  motivo: ['', Validators.required],
  confirmo: [false],
}); 


    this.sub.add(this.auth.currentUser$.subscribe(u => this.currentUser = u));
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




  // Por ahora los botones no hacen nada real:
  onPagarClick() {
  const motivoCtrl = this.form.get('motivo');
  const confirmo = this.form.value.confirmo;

  motivoCtrl?.markAsTouched();

  if (!motivoCtrl?.value) return;  // exige motivo
  if (!confirmo) return;           // exige confirmación

  console.log('Pagar (placeholder). Motivo:', motivoCtrl.value);
}

  onDescargarClick(){ console.log('Descargar PDF (bloqueado hasta pago)'); }
}
