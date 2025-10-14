import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth.service';
import { RegisterRequest } from '../../interfaces/auth.interface';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, HttpClientModule, FormsModule],
  templateUrl: './register.component.html',
  styleUrl: './register.component.css',
})
export class RegisterComponent implements OnInit {
  // Datos para regiones, comunas y juntas (desde BD)
  regiones: any[] = [];
  comunas: any[] = [];
  juntas: any[] = [];
  regionSeleccionada = '';
  comunaSeleccionada = '';
  juntaSeleccionada = '';

  // Modelo para el formulario de registro
  registerData: RegisterRequest = {
    email: '',
    password: '',
    rut: '',
    nombres: '',
    apellido_paterno: '',
    apellido_materno: '',
    fecha_nacimiento: '',
    telefono: '',
    direccion: '',
    foto_perfil: '',
    id_region: 1,
    id_comuna: 1,
    id_junta: 1
  };

  // Estados del componente
  isLoading = false;
  errorMessage = '';
  successMessage = '';
  photoPreview: string | null = null;

  constructor(
    private router: Router,
    private http: HttpClient,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.loadRegiones();
  }

  /** ===================== Cargas de datos ===================== */
  private loadRegiones(): void {
    this.authService.getRegiones().subscribe({
      next: (response) => {
        this.regiones = response.regiones;
      },
      error: (error) => {
        console.error('Error cargando regiones:', error);
        this.errorMessage = 'Error cargando regiones';
      }
    });
  }

  private loadComunasByRegion(regionId: number): void {
    this.authService.getComunasByRegion(regionId).subscribe({
      next: (response) => {
        this.comunas = response.comunas;
      },
      error: (error) => {
        console.error('Error cargando comunas:', error);
        this.errorMessage = 'Error cargando comunas';
      }
    });
  }

  private loadJuntasByComuna(comunaId: number): void {
    this.authService.getJuntasByComuna(comunaId).subscribe({
      next: (response) => {
        this.juntas = response.juntas;
      },
      error: (error) => {
        console.error('Error cargando juntas:', error);
        this.errorMessage = 'Error cargando juntas';
      }
    });
  }

  /** ===================== Handlers UI ===================== */
  onRegionChange(event: Event): void {
    const target = event.target as HTMLSelectElement;
    const regionId = parseInt(target.value);
    this.regionSeleccionada = target.value;

    this.comunaSeleccionada = '';
    this.juntaSeleccionada = '';
    this.comunas = [];
    this.juntas = [];

    if (regionId) this.loadComunasByRegion(regionId);
  }

  onComunaChange(event: Event): void {
    const target = event.target as HTMLSelectElement;
    const comunaId = parseInt(target.value);
    this.comunaSeleccionada = target.value;

    this.juntaSeleccionada = '';
    this.juntas = [];

    if (comunaId) this.loadJuntasByComuna(comunaId);
  }

  onJuntaChange(event: Event): void {
    const target = event.target as HTMLSelectElement;
    this.juntaSeleccionada = target.value;

    const regionId = parseInt(this.regionSeleccionada);
    const comunaId = parseInt(this.comunaSeleccionada);
    const juntaId = parseInt(this.juntaSeleccionada);

    this.registerData.id_region = regionId;
    this.registerData.id_comuna = comunaId;
    this.registerData.id_junta = juntaId;
  }

  onFileChange(evt: Event): void {
    const input = evt.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      this.errorMessage = 'Por favor selecciona un archivo de imagen válido';
      return;
    }

    if (file.size > 2 * 1024 * 1024) {
      this.errorMessage = 'La imagen no puede ser mayor a 2MB';
      return;
    }

    const reader = new FileReader();
    reader.onload = () => {
      this.photoPreview = reader.result as string;
      this.registerData.foto_perfil = reader.result as string;
    };
    reader.readAsDataURL(file);
  }

  /** ===================== Submit ===================== */
  onRegister(): void {
    this.errorMessage = '';
    this.successMessage = '';

    if (!this.isFormValid()) return;

    this.isLoading = true;

    const payload: RegisterRequest = { ...this.registerData };

    // Normalizaciones mínimas
    payload.rut = payload.rut.replace(/[.\-\s]/g, '').toUpperCase();
    if (!payload.foto_perfil || payload.foto_perfil.trim() === '') {
      // enviar undefined si no hay imagen
      (payload as any).foto_perfil = undefined;
    }

    if (payload.password.length > 12) {
      this.errorMessage = 'La contraseña no puede tener más de 12 caracteres';
      this.isLoading = false;
      return;
    }

    this.authService.register(payload).subscribe({
      next: () => {
        this.isLoading = false;
        this.successMessage = '¡Registro exitoso! Redirigiendo al login...';
        setTimeout(() => this.router.navigate(['/login']), 2000);
      },
      error: (error) => {
        console.error('Error en registro:', error);
        this.isLoading = false;
        this.errorMessage =
          error?.error?.detalle ||
          error?.message ||
          'Error al registrar usuario. Verifica los datos e intenta nuevamente.';
      }
    });
  }

  /** ===================== Validaciones FRONT ===================== */
  private isFormValid(): boolean {
    const d = this.registerData;

    // 1) Requeridos
    if (
      !d.email || !d.password || !d.rut || !d.nombres ||
      !d.apellido_paterno || !d.apellido_materno ||
      !d.fecha_nacimiento || !d.telefono || !d.direccion
    ) {
      this.errorMessage = 'Por favor completa todos los campos obligatorios.';
      return false;
    }

    // 2) Email
    if (!this.isValidEmail(d.email)) {
      this.errorMessage = 'El correo ingresado no es válido.';
      return false;
    }

    // 3) Password 8–12
    if (d.password.length < 8 || d.password.length > 12) {
      this.errorMessage = 'La contraseña debe tener entre 8 y 12 caracteres.';
      return false;
    }

    // 4) RUT con dígito verificador
    if (!this.isValidRut(d.rut)) {
      this.errorMessage = 'El RUT ingresado no es válido.';
      return false;
    }

    // 5) Teléfono +56 + 9 dígitos
    if (!this.isValidPhone(d.telefono)) {
      this.errorMessage = 'El teléfono debe tener formato +56XXXXXXXXX (9 dígitos).';
      return false;
    }

    // 6) Mínimos de texto
    if (
      d.nombres.trim().length < 2 ||
      d.apellido_paterno.trim().length < 2 ||
      d.apellido_materno.trim().length < 2
    ) {
      this.errorMessage = 'Los nombres y apellidos deben tener al menos 2 caracteres.';
      return false;
    }

    if (d.direccion.trim().length < 5) {
      this.errorMessage = 'La dirección debe tener al menos 5 caracteres.';
      return false;
    }

    // 7) Selecciones
    if (!this.registerData.id_region || !this.registerData.id_comuna || !this.registerData.id_junta) {
      this.errorMessage = 'Selecciona región, comuna y junta de vecinos.';
      return false;
    }

    return true;
  }

  public isValidEmail(email: string): boolean {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test((email || '').trim());
  }

  public isValidPhone(phone: string): boolean {
    // +56 seguido de 9 dígitos
    return /^\+56\d{9}$/.test((phone || '').trim());
  }

  /** Valida RUT chileno con dígito verificador */
  public isValidRut(rut: string): boolean {
    if (!rut) return false;
    const clean = rut.replace(/[.\-]/g, '').toUpperCase();
    if (!/^[0-9]+[0-9K]$/.test(clean)) return false;

    const body = clean.slice(0, -1);
    const dv = clean.slice(-1);

    let suma = 0;
    let multiplo = 2;

    for (let i = body.length - 1; i >= 0; i--) {
      suma += parseInt(body[i], 10) * multiplo;
      multiplo = multiplo < 7 ? multiplo + 1 : 2;
    }

    const resto = 11 - (suma % 11);
    const dvEsperado = resto === 11 ? '0' : resto === 10 ? 'K' : resto.toString();

    return dv === dvEsperado;
  }

  public declaraVeracidad = false;

  /** ===================== Navegación ===================== */
  goBack(): void {
    this.router.navigate(['/']);
  }

  goToLogin(): void {
    this.router.navigate(['/login']);
  }
}
