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
  imports: [CommonModule,HttpClientModule, FormsModule], 
  templateUrl: './register.component.html',
  styleUrl: './register.component.css',
})
export class RegisterComponent implements OnInit {

  // Datos para regiones y comunas (JSON)
  regiones: string[] = [];
  comunas: string[] = [];
  regionesComunas: Record<string, string[]> = {};
  regionSeleccionada = '';
  comunaSeleccionada = '';

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
    id_region: 1, // Por defecto Región Metropolitana (ajustar según tu BD)
    id_comuna: 1, // Ajustar según tu BD
    id_junta: 1   // Ajustar según tu BD
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
    // Carga el JSON con regiones y comunas
    this.http
      .get<Record<string, string[]>>('/data/regiones-comunas.json')
      .subscribe((data) => {
        this.regionesComunas = data;
        this.regiones = Object.keys(data).sort(); // opcional: orden alfabético
      });}

/**
   * Maneja el cambio de archivo de foto de perfil
   */
  onFileChange(evt: Event): void {
    const input = evt.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;

    // Validar tipo de archivo
    if (!file.type.startsWith('image/')) {
      this.errorMessage = 'Por favor selecciona un archivo de imagen válido';
      return;
    }

    // Validar tamaño (máximo 2MB)
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

  /**
   * Maneja el cambio de región (para el JSON)
   */
  onRegionChange(event: Event): void {
    const target = event.target as HTMLSelectElement;
    const region = target.value;
    this.regionSeleccionada = region;
    this.comunas = this.regionesComunas[region] ?? [];
    this.comunaSeleccionada = '';
  }

  /**
   * Maneja el envío del formulario de registro
   */
  onRegister(): void {
    // Limpiar mensajes previos
    this.errorMessage = '';
    this.successMessage = '';

    // Validaciones básicas
    if (!this.isFormValid()) {
      return;
    }

    this.isLoading = true;

    // Preparar datos para envío
    const registerData = { ...this.registerData };
    
    // Limpiar y formatear datos según las expectativas del backend
    registerData.rut = registerData.rut.replace(/[.\-\s]/g, '').toUpperCase();
    
    // Limpiar foto_perfil si está vacía
    if (!registerData.foto_perfil || registerData.foto_perfil.trim() === '') {
      registerData.foto_perfil = undefined;
    }
    
    // Validar que la contraseña no sea muy larga (backend limita a 12 caracteres)
    if (registerData.password.length > 12) {
      this.errorMessage = 'La contraseña no puede tener más de 12 caracteres';
      this.isLoading = false;
      return;
    }

    this.authService.register(registerData).subscribe({
      next: (response) => {
        this.isLoading = false;
        this.successMessage = '¡Registro exitoso! Redirigiendo al login...';
        
        // Redirigir al login después de 2 segundos
        setTimeout(() => {
          this.router.navigate(['/login']);
        }, 2000);
      },
      error: (error) => {
        console.error('Error en registro:', error);
        this.isLoading = false;
        this.errorMessage = error.message || 'Error al registrar usuario. Verifica los datos e intenta nuevamente.';
      }
    });
  }

  /**
   * Valida que el formulario esté completo
   */
  private isFormValid(): boolean {
    const data = this.registerData;

    if (!data.email || !data.password || !data.rut || !data.nombres || 
        !data.apellido_paterno || !data.apellido_materno || !data.fecha_nacimiento ||
        !data.telefono || !data.direccion) {
      this.errorMessage = 'Por favor, completa todos los campos obligatorios';
      return false;
    }

    if (!this.isValidEmail(data.email)) {
      this.errorMessage = 'Por favor, ingresa un email válido';
      return false;
    }

    if (data.password.length < 8 || data.password.length > 12) {
      this.errorMessage = 'La contraseña debe tener entre 8 y 12 caracteres';
      return false;
    }

    if (!this.isValidRut(data.rut)) {
      this.errorMessage = 'Por favor, ingresa un RUT válido';
      return false;
    }

    if (!this.isValidPhone(data.telefono)) {
      this.errorMessage = 'El teléfono debe tener formato +56XXXXXXXXX';
      return false;
    }

    if (data.nombres.length < 2 || data.apellido_paterno.length < 2 || data.apellido_materno.length < 2) {
      this.errorMessage = 'Los nombres y apellidos deben tener al menos 2 caracteres';
      return false;
    }

    if (data.direccion.length < 5) {
      this.errorMessage = 'La dirección debe tener al menos 5 caracteres';
      return false;
    }

    return true;
  }

  /**
   * Validación simple de email
   */
  private isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  /**
   * Validación básica de RUT chileno
   */
  private isValidRut(rut: string): boolean {
    // Remover puntos y guiones
    const cleanRut = rut.replace(/[.-]/g, '');
    
    // Verificar que tenga al menos 8 caracteres
    if (cleanRut.length < 8) {
      return false;
    }

    // Verificar que tenga formato correcto (números + dígito verificador)
    const rutRegex = /^\d{7,8}[0-9Kk]$/;
    return rutRegex.test(cleanRut);
  }

  /**
   * Validación de teléfono chileno
   */
  private isValidPhone(phone: string): boolean {
    // Formato esperado: +56XXXXXXXXX (9 dígitos después de +56)
    const phoneRegex = /^\+56[0-9]{9}$/;
    return phoneRegex.test(phone);
  }

  /**
   * Navegar de vuelta al home
   */
  goBack(): void {
    this.router.navigate(['/']);
  }

  /**
   * Navegar al login
   */
  goToLogin(): void {
    this.router.navigate(['/login']);
  }
}
  
  

