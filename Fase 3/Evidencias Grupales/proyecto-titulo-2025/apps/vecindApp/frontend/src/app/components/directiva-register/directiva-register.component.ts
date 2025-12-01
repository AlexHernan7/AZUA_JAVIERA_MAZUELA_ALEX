import { Component, EventEmitter, Output, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import {
  FormBuilder,
  Validators,
  ReactiveFormsModule,
  FormsModule,
  AbstractControl,
  ValidationErrors,
  FormGroup,
} from '@angular/forms';
import { DirectivaService } from '../../services/directiva.service';
import { AuthService } from '../../services/auth.service';

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
  imports: [CommonModule, ReactiveFormsModule, FormsModule, HttpClientModule, RouterModule],
  templateUrl: './directiva-register.component.html',
  styleUrls: ['./directiva-register.component.css'],
})
export class DirectivaRegisterComponent implements OnInit {
  @Output() save = new EventEmitter<DirectivoForm>();
  @Output() cancel = new EventEmitter<void>();

  isLoading = false;
  errorMessage = '';
  successMessage = '';
  photoPreview: string | null = null;

  cargos = ['Presidente', 'Vicepresidente', 'Secretario', 'Tesorero', 'Vocal'];

  // Datos para juntas
  juntas: any[] = [];

  form!: FormGroup;

  constructor(
    private fb: FormBuilder,
    private directivaService: DirectivaService,
    private authService: AuthService,
    private router: Router,
    private http: HttpClient
  ) {
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
      juntaSeleccionada: ['', Validators.required], // Agregar control para junta
      passwords: this.fb.group(
        {
          password: ['', [Validators.required, Validators.minLength(8), Validators.maxLength(12)]],
          confirmPassword: ['', Validators.required],
        },
        { validators: samePasswordValidator }
      ),
    });
  }

  ngOnInit(): void {
    // Cargar juntas disponibles
    this.loadJuntas();
  }

  g(path: string) {
    return this.form.get(path) as AbstractControl;
  }

  // Helper para establecer la junta seleccionada
  setJuntaSeleccionada(idJunta: number) {
    this.form.patchValue({ juntaSeleccionada: idJunta });
  }

  /**
   * Carga las juntas disponibles desde el backend
   */
  private loadJuntas(): void {
    // Cargar todas las juntas directamente (sin filtrar por comuna)
    this.authService.getAllJuntas(100).subscribe({
      next: (response: any) => {
        if (response.juntas && response.juntas.length > 0) {
          this.juntas = response.juntas;
          
          // Si solo hay una junta, seleccionarla automáticamente
          if (this.juntas.length === 1) {
            this.setJuntaSeleccionada(this.juntas[0].id_junta);
          }
        } else {
          // Fallback: usar la junta por defecto
          this.juntas = [
            { id_junta: 1, nombre: 'Junta de Vecinos Barrio Oeste' }
          ];
          if (this.juntas.length > 0) {
            this.setJuntaSeleccionada(this.juntas[0].id_junta);
          }
        }
      },
      error: (error: any) => {
        // Fallback: usar la junta por defecto
        this.juntas = [
          { id_junta: 1, nombre: 'Junta de Vecinos Barrio Oeste' }
        ];
        if (this.juntas.length > 0) {
          this.setJuntaSeleccionada(this.juntas[0].id_junta);
        }
      }
    });
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
    this.successMessage = '';

    // Validar formulario
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      this.errorMessage = 'Revisa los campos marcados.';
      return;
    }

    this.isLoading = true;

    const f = this.form.value as any;
    const juntaSeleccionada = f.juntaSeleccionada;
    
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

    // Llamar al servicio para registrar el directivo
    this.directivaService.registerDirectivo(payload, juntaSeleccionada).subscribe({
      next: (response) => {
        this.isLoading = false;
        this.successMessage = '¡Directivo registrado exitosamente!';
        
        // Limpiar el formulario para permitir registrar otro directivo
        setTimeout(() => {
          this.form.reset();
          this.photoPreview = null;
          this.successMessage = '';
          // Reseleccionar la primera junta por defecto
          if (this.juntas.length > 0) {
            this.setJuntaSeleccionada(this.juntas[0].id_junta);
          }
        }, 2000);
      },
      error: (error) => {
        this.isLoading = false;
        this.errorMessage = error.message || 'Error al registrar directivo. Verifica los datos e intenta nuevamente.';
      }
    });
  }

  cancelUI(): void {
    this.cancel.emit();
  }
}
