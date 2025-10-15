import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, Validators, ReactiveFormsModule,  AbstractControl, ValidationErrors, FormGroup, } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { JuntaService } from '../../services/junta.service';
import { AuthService } from '../../services/auth.service';
import { JuntaCreateRequest } from '../../interfaces/junta.interface';
import { forkJoin } from 'rxjs';
import { RouterModule } from '@angular/router';

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
  imports: [CommonModule, ReactiveFormsModule, HttpClientModule, RouterModule],
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

  // Datos para regiones, comunas (desde BD)
  regiones: any[] = [];
  comunas: any[] = [];
  regionSeleccionada = '';
  comunaSeleccionada = '';

  constructor(
    private fb: FormBuilder, 
    private http: HttpClient,
    private juntaService: JuntaService,
    private authService: AuthService
  ) {
    this.form = this.fb.group({
      logo: [''],
      nombre: ['Junta de Vecinos Barrio Oeste', [Validators.required, Validators.minLength(3)]],
      rut_personeria: ['', [Validators.required, rutBasicoValidator]], // obligatorio + formato
      email_contacto: ['', [Validators.required, Validators.email]],
      telefono_contacto: ['', [Validators.required, phoneClValidator]],
      direccion_sede: ['', [Validators.required, Validators.minLength(5)]],
      region: ['', Validators.required],
      comuna: ['', Validators.required],
      fecha_constitucion: [''],
      activa: [true],
      descripcion: [''],
    });

    // Inicializar estado disabled
    this.form.get('comuna')!.disable(); // Comuna deshabilitada hasta que se seleccione región
    
    // Cargar regiones desde la BD
    this.loadRegiones();

    // Cuando cambia región, cargar comunas de esa región
    this.form.get('region')!.valueChanges.subscribe((regionId: string) => {
      this.onRegionChange(regionId);
    });
  }

  g(path: string) { return this.form.get(path) as AbstractControl; }

  /**
   * Carga las regiones desde el backend
   */
  private loadRegiones(): void {
    this.setFormLoadingState(true);
    
    this.authService.getRegiones().subscribe({
      next: (response) => {
        this.regiones = response.regiones;
        this.setFormLoadingState(false);
      },
      error: (error) => {
        console.error('Error cargando regiones:', error);
        this.errorMessage = 'Error cargando regiones';
        this.setFormLoadingState(false);
      }
    });
  }

  /**
   * Habilita/deshabilita el formulario según el estado de loading
   */
  private setFormLoadingState(loading: boolean): void {
    this.isLoading = loading;
    
    if (loading) {
      this.form.get('region')!.disable();
      this.form.get('comuna')!.disable();
    } else {
      this.form.get('region')!.enable();
      // Comuna solo se habilita si hay región seleccionada
      if (this.regionSeleccionada) {
        this.form.get('comuna')!.enable();
      }
    }
  }

  /**
   * Maneja el cambio de región
   */
  private onRegionChange(regionNombre: string): void {
    if (!regionNombre) {
      // Si no hay región seleccionada, deshabilitar comuna
      this.form.get('comuna')!.disable();
      return;
    }
    
    this.regionSeleccionada = regionNombre;
    this.comunaSeleccionada = '';
    this.comunas = [];
    this.form.get('comuna')!.reset('');
    this.form.get('comuna')!.disable(); // Deshabilitar mientras carga
    
    this.authService.getComunasByRegion(regionNombre).subscribe({
      next: (response) => {
        this.comunas = response.comunas;
        this.form.get('comuna')!.enable(); // Habilitar cuando termine de cargar
      },
      error: (error) => {
        console.error('Error cargando comunas:', error);
        this.errorMessage = 'Error cargando comunas';
        this.form.get('comuna')!.enable(); // Habilitar aunque haya error
      }
    });
  }

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
    this.successMessage = '';
    
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      this.errorMessage = 'Revisa los campos marcados.';
      return;
    }

    this.isLoading = true;
    const formData = this.form.value;

    // Validar que se haya seleccionado región y comuna
    if (!formData.region || !formData.comuna) {
      this.isLoading = false;
      this.errorMessage = 'Debes seleccionar región y comuna.';
      return;
    }

    // Preparar los datos para enviar al backend usando los IDs directamente
    const juntaRequest: JuntaCreateRequest = {
      nombre: formData.nombre.trim(),
      rut: formData.rut_personeria ? this.formatRut(formData.rut_personeria) : '',
      email: formData.email_contacto.trim(),
      telefono: formData.telefono_contacto.trim(),
      direccion: formData.direccion_sede.trim(),
      id_comuna: parseInt(formData.comuna), // Ya es el ID de la comuna
      fecha_constitucion: formData.fecha_constitucion || undefined,
      descripcion: formData.descripcion?.trim() || undefined,
      activa: !!formData.activa,
      logo: formData.logo || undefined
    };

    // Enviar al backend
    this.juntaService.createJunta(juntaRequest).subscribe({
      next: (response) => {
        this.isLoading = false;
        this.successMessage = `¡Junta "${response.nombre}" creada exitosamente!`;
        
        // Obtener nombres para el evento
        const regionNombre = this.regiones.find(r => r.id_region == formData.region)?.nombre || '';
        const comunaNombre = this.comunas.find(c => c.id_comuna == formData.comuna)?.nombre || '';
        
        // Emitir evento de éxito con los datos originales del formulario
        const juntaForm: JuntaForm = {
          nombre: formData.nombre.trim(),
          rut_personeria: formData.rut_personeria,
          email_contacto: formData.email_contacto.trim(),
          telefono_contacto: formData.telefono_contacto.trim(),
          direccion_sede: formData.direccion_sede.trim(),
          region: regionNombre,
          comuna: comunaNombre,
          fecha_constitucion: formData.fecha_constitucion,
          activa: !!formData.activa,
          descripcion: formData.descripcion?.trim(),
          logo: formData.logo
        };
        
        this.save.emit(juntaForm);
        
        // Limpiar formulario después de 3 segundos
        setTimeout(() => {
          this.form.reset();
          this.logoPreview = null;
          this.successMessage = '';
          this.form.patchValue({ activa: true });
          // Resetear selecciones
          this.regionSeleccionada = '';
          this.comunaSeleccionada = '';
          this.comunas = [];
        }, 3000);
      },
      error: (error) => {
        this.isLoading = false;
        console.error('Error creando junta:', error);
        this.errorMessage = error.message || 'Error al crear la junta. Inténtalo nuevamente.';
      }
    });
  }

  /**
   * Formatea el RUT agregando puntos y guión
   */
  private formatRut(rut: string): string {
    const cleaned = rut.replace(/[.\-\s]/g, '').toUpperCase();
    if (cleaned.length < 8) return cleaned;
    
    const body = cleaned.slice(0, -1);
    const dv = cleaned.slice(-1);
    
    // Agregar puntos cada 3 dígitos desde la derecha
    const formatted = body.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    return `${formatted}-${dv}`;
  }

  cancelUI(): void {
    this.cancel.emit();
  }
}
