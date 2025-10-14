import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterModule} from '@angular/router';
import { EspacioService } from '../../services/espacio.service';
import { AuthService } from '../../services/auth.service';
import { JuntaService } from '../../services/junta.service';
import { MasterService, TipoEspacioResponse } from '../../services/master.service';
import { EspacioCreateRequest } from '../../interfaces/espacio.interface';
import { JuntaListResponse } from '../../interfaces/junta.interface';

@Component({
  selector: 'app-create-espacios',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule,RouterModule],
  templateUrl: './create-espacios.component.html',
  styleUrl: './create-espacios.component.css',
})
export class CreateEspaciosComponent implements OnInit {
  espacioForm!: FormGroup;
  loading = false;
  error: string | null = null;
  success = false;
  juntas: JuntaListResponse[] = [];
  tiposEspacio: TipoEspacioResponse[] = [];
  selectedFile: File | null = null;
  filePreview: string | null = null;

  constructor(
    private fb: FormBuilder,
    private espacioService: EspacioService,
    private authService: AuthService,
    private juntaService: JuntaService,
    private masterService: MasterService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.initForm();
    this.loadJuntas();
    this.loadTiposEspacio();
  }

  private initForm(): void {
    this.espacioForm = this.fb.group({
      nombre: ['', [Validators.required, Validators.minLength(2), Validators.maxLength(100)]],
      id_tipo: ['', Validators.required],
      capacidad: ['', [Validators.required, Validators.min(1)]],
      valor: ['', [Validators.required, Validators.min(0)]],
      foto: [''],
      permitido: [''],
      no_permitido: [''],
      max_horas: [4, [Validators.required, Validators.min(1), Validators.max(24)]],
      activo: [true],
      id_junta: ['', Validators.required] // Ahora es un selector
    });
  }

  onSubmit(): void {
    if (this.espacioForm.valid) {
      this.loading = true;
      this.error = null;
      this.success = false;

      const formData = this.espacioForm.value;
      
      // Procesar arrays de permitido y no permitido
      const espacioData: EspacioCreateRequest = {
        ...formData,
        id_tipo: parseInt(formData.id_tipo), // Convertir a número
        permitido: this.processArrayField(formData.permitido),
        no_permitido: this.processArrayField(formData.no_permitido),
        id_junta: parseInt(formData.id_junta) // Convertir a número
      };

      // Si hay archivo seleccionado, usar el servicio con archivo
      if (this.selectedFile) {
        this.espacioService.createEspacioWithFile(espacioData, this.selectedFile).subscribe({
          next: (response) => {
            this.loading = false;
            this.success = true;
            console.log('Espacio creado exitosamente:', response);
            
            // Redirigir después de 2 segundos
            setTimeout(() => {
              this.router.navigate(['/reservas']);
            }, 2000);
          },
          error: (error) => {
            this.loading = false;
            this.error = error.message || 'Error al crear el espacio';
            console.error('Error al crear espacio:', error);
          }
        });
      } else {
        // Sin archivo, usar el servicio normal
        this.espacioService.createEspacio(espacioData).subscribe({
          next: (response) => {
            this.loading = false;
            this.success = true;
            console.log('Espacio creado exitosamente:', response);
            
            // Redirigir después de 2 segundos
            setTimeout(() => {
              this.router.navigate(['/reservas']);
            }, 2000);
          },
          error: (error) => {
            this.loading = false;
            this.error = error.message || 'Error al crear el espacio';
            console.error('Error al crear espacio:', error);
          }
        });
      }
    } else {
      this.markFormGroupTouched();
    }
  }

  private processArrayField(field: string): string[] {
    if (!field || field.trim() === '') {
      return [];
    }
    
    return field
      .split(',')
      .map(item => item.trim())
      .filter(item => item.length > 0);
  }

  private markFormGroupTouched(): void {
    Object.keys(this.espacioForm.controls).forEach(key => {
      const control = this.espacioForm.get(key);
      control?.markAsTouched();
    });
  }

  getFieldError(fieldName: string): string {
    const field = this.espacioForm.get(fieldName);
    if (field?.errors && field.touched) {
      if (field.errors['required']) {
        return `${this.getFieldLabel(fieldName)} es requerido`;
      }
      if (field.errors['minlength']) {
        return `${this.getFieldLabel(fieldName)} debe tener al menos ${field.errors['minlength'].requiredLength} caracteres`;
      }
      if (field.errors['maxlength']) {
        return `${this.getFieldLabel(fieldName)} no puede tener más de ${field.errors['maxlength'].requiredLength} caracteres`;
      }
      if (field.errors['min']) {
        return `${this.getFieldLabel(fieldName)} debe ser mayor a ${field.errors['min'].min}`;
      }
      if (field.errors['max']) {
        return `${this.getFieldLabel(fieldName)} no puede ser mayor a ${field.errors['max'].max}`;
      }
    }
    return '';
  }

  private getFieldLabel(fieldName: string): string {
    const labels: { [key: string]: string } = {
      nombre: 'Nombre',
      id_tipo: 'Tipo de espacio',
      capacidad: 'Capacidad',
      valor: 'Valor',
      foto: 'Foto',
      permitido: 'Actividades permitidas',
      no_permitido: 'Actividades no permitidas',
      max_horas: 'Máximo de horas',
      id_junta: 'Junta de vecinos'
    };
    return labels[fieldName] || fieldName;
  }

  isFieldInvalid(fieldName: string): boolean {
    const field = this.espacioForm.get(fieldName);
    return !!(field?.invalid && field.touched);
  }

  goBack(): void {
    this.router.navigate(['/reservas']);
  }

  private loadJuntas(): void {
    this.juntaService.listJuntas({ limit: 100 }).subscribe({
      next: (response) => {
        this.juntas = response.juntas || [];
        console.log('Juntas cargadas:', this.juntas);
      },
      error: (error) => {
        console.error('Error al cargar juntas:', error);
        this.error = 'Error al cargar la lista de juntas';
      }
    });
  }

  private loadTiposEspacio(): void {
    this.masterService.getTiposEspacio(true).subscribe({
      next: (response) => {
        this.tiposEspacio = response;
        console.log('Tipos de espacio cargados:', this.tiposEspacio);
      },
      error: (error) => {
        console.error('Error al cargar tipos de espacio:', error);
        this.error = 'Error al cargar los tipos de espacio';
      }
    });
  }

  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file) {
      // Validar tipo de archivo
      const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
      if (!allowedTypes.includes(file.type)) {
        this.error = 'Solo se permiten archivos de imagen (JPEG, PNG, GIF, WebP)';
        return;
      }

      // Validar tamaño (máximo 5MB)
      const maxSize = 5 * 1024 * 1024; // 5MB
      if (file.size > maxSize) {
        this.error = 'El archivo no puede ser mayor a 5MB';
        return;
      }

      this.selectedFile = file;
      this.error = null;

      // Crear preview
      const reader = new FileReader();
      reader.onload = (e) => {
        this.filePreview = e.target?.result as string;
      };
      reader.readAsDataURL(file);

      // Actualizar el formulario con el nombre del archivo
      this.espacioForm.patchValue({
        foto: file.name
      });
    }
  }

  removeFile(): void {
    this.selectedFile = null;
    this.filePreview = null;
    this.espacioForm.patchValue({
      foto: ''
    });
  }

  triggerFileInput(): void {
    const fileInput = document.getElementById('foto') as HTMLInputElement;
    if (fileInput) {
      fileInput.click();
    }
  }
}
