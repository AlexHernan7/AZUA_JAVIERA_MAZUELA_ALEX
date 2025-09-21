import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  FormBuilder,
  Validators,
  ReactiveFormsModule,
  AbstractControl,
  ValidationErrors,
  FormGroup,
} from '@angular/forms';

/* --- Validadores UI --- */
function rutBasicoValidator(ctrl: AbstractControl): ValidationErrors | null {
  const raw = (ctrl.value || '').toString().replace(/[.\-\s]/g, '').toUpperCase();
  if (!raw) return null;
  return /^\d{7,8}[0-9K]$/.test(raw) ? null : { rut: true };
}
function phoneClValidator(ctrl: AbstractControl): ValidationErrors | null {
  const v = (ctrl.value || '').toString();
  if (!v) return null;
  return /^\+56[0-9]{9}$/.test(v) ? null : { phone: true };
}
function samePasswordValidator(group: AbstractControl): ValidationErrors | null {
  const pass = group.get('password')?.value;
  const confirm = group.get('confirmPassword')?.value;
  if (!pass || !confirm) return null;
  return pass === confirm ? null : { mismatch: true };
}

export type DirectivoForm = {
  foto_perfil?: string;
  apellido_paterno: string;
  apellido_materno?: string;
  rut: string;
  cargo: string;
  nombres: string;
  email: string;
  telefono: string;
  fecha_inicio?: string;
  fecha_termino?: string;
  password: string;
};

@Component({
  selector: 'app-directiva-register',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './directiva-register.component.html',
  styleUrls: ['./directiva-register.component.css'],
})
export class DirectivaRegisterComponent {
  @Output() save = new EventEmitter<DirectivoForm>();
  @Output() cancel = new EventEmitter<void>();

  isLoading = false;
  errorMessage = '';
  successMessage = '';
  photoPreview: string | null = null;

  cargos = ['Presidente', 'Vicepresidente', 'Secretario', 'Tesorero', 'Vocal'];

  form!: FormGroup;

  constructor(private fb: FormBuilder) {
    this.form = this.fb.group({
      foto_perfil: [''],
      apellido_paterno: ['', [Validators.required, Validators.minLength(2)]],
      apellido_materno: [''],
      rut: ['', [Validators.required, rutBasicoValidator]],
      cargo: ['', Validators.required],
      nombres: ['', [Validators.required, Validators.minLength(2)]],
      email: ['', [Validators.required, Validators.email]],
      telefono: ['', [Validators.required, phoneClValidator]],
      fecha_inicio: [''],
      fecha_termino: [''],
      passwords: this.fb.group(
        {
          password: ['', [Validators.required, Validators.minLength(8), Validators.maxLength(12)]],
          confirmPassword: ['', Validators.required],
        },
        { validators: samePasswordValidator }
      ),
    });
  }

  g(path: string) {
    return this.form.get(path) as AbstractControl;
  }

  onFileChange(evt: Event): void {
    const input = evt.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      this.errorMessage = 'Imagen inválida.';
      return;
    }
    if (file.size > 2 * 1024 * 1024) {
      this.errorMessage = 'Máximo 2MB.';
      return;
    }

    const reader = new FileReader();
    reader.onload = () => {
      this.photoPreview = reader.result as string;
      this.form.patchValue({ foto_perfil: this.photoPreview });
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
    const payload: DirectivoForm = {
      foto_perfil: f.foto_perfil || undefined,
      apellido_paterno: f.apellido_paterno.trim(),
      apellido_materno: f.apellido_materno?.trim() || undefined,
      rut: (f.rut as string).replace(/[.\-\s]/g, '').toUpperCase(),
      cargo: f.cargo,
      nombres: f.nombres.trim(),
      email: f.email.trim(),
      telefono: f.telefono.trim(),
      fecha_inicio: f.fecha_inicio || undefined,
      fecha_termino: f.fecha_termino || undefined,
      password: f.passwords.password,
    };

    // Solo UI: emite los datos listos. El contenedor hará el POST real.
    this.save.emit(payload);
    this.successMessage = 'Formulario válido listo para enviar.';
  }

  cancelUI(): void {
    this.cancel.emit();
  }
}
