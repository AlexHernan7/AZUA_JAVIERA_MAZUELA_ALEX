import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  FormBuilder, Validators, ReactiveFormsModule,
  AbstractControl, ValidationErrors, FormGroup
} from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';

/* Validadores simples */
function phoneClValidator(ctrl: AbstractControl): ValidationErrors | null {
  const v = (ctrl.value || '').toString();
  if (!v) return null;
  return /^\+56[0-9]{9}$/.test(v) ? null : { phone: true };
}
function rutBasicoValidator(ctrl: AbstractControl): ValidationErrors | null {
  const raw = (ctrl.value || '').toString().replace(/[.\-\s]/g, '').toUpperCase();
  if (!raw) return null;
  return /^\d{7,8}[0-9K]$/.test(raw) ? null : { rut: true };
}

export type JuntaForm = {
  nombre: string;
  rut_personeria?: string;
  email_contacto: string;
  telefono_contacto: string;
  direccion_sede: string;
  region: string;
  comuna: string;
  fecha_constitucion?: string;
  activa: boolean;
  logo?: string;         // dataURL (opcional)
  descripcion?: string;
};

@Component({
  selector: 'app-junta-create',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, HttpClientModule],
  templateUrl: './junta-create.component.html',
  styleUrls: ['./junta-create.component.css'],
})
export class JuntaCreateComponent {
  @Output() save = new EventEmitter<JuntaForm>();
  @Output() cancel = new EventEmitter<void>();

  form!: FormGroup;
  isLoading = false;
  errorMessage = '';
  successMessage = '';
  logoPreview: string | null = null;

  regionesComunas: Record<string, string[]> = {};
  regiones: string[] = [];
  comunas: string[] = [];

  constructor(private fb: FormBuilder, private http: HttpClient) {
    this.form = this.fb.group({
      logo: [''],
      nombre: ['Junta de Vecinos Barrio Oeste', [Validators.required, Validators.minLength(3)]],
      rut_personeria: ['', rutBasicoValidator], // opcional
      email_contacto: ['', [Validators.required, Validators.email]],
      telefono_contacto: ['', [Validators.required, phoneClValidator]],
      direccion_sede: ['', [Validators.required, Validators.minLength(5)]],
      region: ['', Validators.required],
      comuna: ['', Validators.required],
      fecha_constitucion: [''],
      activa: [true],
      descripcion: [''],
    });

    // Carga de regiones/comunas
    this.http.get<Record<string, string[]>>('/data/regiones-comunas.json').subscribe({
      next: (data) => {
        this.regionesComunas = data;
        this.regiones = Object.keys(data).sort();
      }
    });

    // Cuando cambia región, limpiamos/actualizamos comunas
    this.form.get('region')!.valueChanges.subscribe((reg: string) => {
      this.comunas = this.regionesComunas[reg] ?? [];
      this.form.get('comuna')!.reset('');
    });
  }

  g(path: string) { return this.form.get(path) as AbstractControl; }

  onLogoChange(evt: Event): void {
    const input = evt.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) { this.errorMessage = 'Selecciona una imagen válida.'; return; }
    if (file.size > 2 * 1024 * 1024) { this.errorMessage = 'El logo no puede superar 2MB.'; return; }

    const reader = new FileReader();
    reader.onload = () => {
      this.logoPreview = reader.result as string;
      this.form.patchValue({ logo: this.logoPreview });
    };
    reader.readAsDataURL(file);
  }

  submitUI(): void {
    this.errorMessage = '';
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      this.errorMessage = 'Revisa los campos marcados.';
      return;
    }
    const f = this.form.value as any;
    const payload: JuntaForm = {
      logo: f.logo || undefined,
      nombre: f.nombre.trim(),
      rut_personeria: f.rut_personeria ? (f.rut_personeria as string).replace(/[.\-\s]/g, '').toUpperCase() : undefined,
      email_contacto: f.email_contacto.trim(),
      telefono_contacto: f.telefono_contacto.trim(),
      direccion_sede: f.direccion_sede.trim(),
      region: f.region,
      comuna: f.comuna,
      fecha_constitucion: f.fecha_constitucion || undefined,
      activa: !!f.activa,
      descripcion: f.descripcion?.trim() || undefined,
    };

    this.save.emit(payload);
    this.successMessage = 'Formulario válido listo para enviar.';
  }

  cancelUI(): void {
    this.cancel.emit();
  }
}
