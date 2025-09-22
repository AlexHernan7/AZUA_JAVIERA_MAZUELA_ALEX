import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { Subscription } from 'rxjs';
import { AuthService } from '../../services/auth.service';
import { UserLoginData, UpdateProfileRequest } from '../../interfaces/auth.interface';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule],
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.css'],
})
export class ProfileComponent implements OnInit, OnDestroy {
  currentUser: UserLoginData | null = null;
  isLoading: boolean = true;
  error: string | null = null;
  
  // Variables para el modal de edición
  showEditModal: boolean = false;
  editForm: FormGroup;
  isUpdating: boolean = false;
  updateError: string | null = null;
  updateSuccess: string | null = null;
  
  private subscription: Subscription = new Subscription();

  // Propiedades calculadas para el template
  get nombreCompleto(): string {
    if (!this.currentUser) return '';
    return `${this.currentUser.nombres} ${this.currentUser.apellido_paterno} ${this.currentUser.apellido_materno || ''}`.trim();
  }

  get isDirectivo(): boolean {
    return this.currentUser?.roles?.includes('directiva') || false;
  }

  get isVecino(): boolean {
    return this.currentUser?.roles?.includes('vecino') || false;
  }

  get isAdmin(): boolean {
    return this.currentUser?.roles?.includes('admin') || false;
  }

  get avatarUrl(): string {
    const foto = this.currentUser?.vecino?.foto_perfil;
    if (foto && foto.trim() !== '') {
      // Verificar que sea una imagen base64 válida
      if (foto.startsWith('data:image/')) {
        return foto;
      }
      // Si no tiene el prefijo data:image/, agregarlo (por compatibilidad)
      return `data:image/jpeg;base64,${foto}`;
    }
    return 'images/avatar-placeholder2.svg';
  }

  get telefono(): string {
    return this.currentUser?.vecino?.telefono || 'No especificado';
  }

  get direccion(): string {
    return this.currentUser?.vecino?.direccion || 'No especificada';
  }

  get rutFormateado(): string {
    const rut = this.currentUser?.vecino?.rut;
    if (!rut) return 'No especificado';
    
    // Limpiar el RUT de cualquier formato previo
    const cleanRut = rut.replace(/[^0-9Kk]/g, '');
    
    if (cleanRut.length < 8) return rut;
    
    // Separar número y dígito verificador
    const numero = cleanRut.slice(0, -1);
    const dv = cleanRut.slice(-1);
    
    // Formatear con puntos
    const numeroFormateado = numero.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    
    return `${numeroFormateado}-${dv}`;
  }

  get fechaNacimientoFormateada(): string {
    const fecha = this.currentUser?.vecino?.fecha_nacimiento;
    if (!fecha) return 'No especificada';
    
    try {
      const date = new Date(fecha);
      return date.toLocaleDateString('es-CL', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      });
    } catch {
      return fecha;
    }
  }

  get comuna(): string {
    return this.currentUser?.vecino?.comuna || 'No especificada';
  }

  get region(): string {
    return this.currentUser?.vecino?.region || 'No especificada';
  }

  get junta(): string {
    return this.currentUser?.vecino?.junta || 'No especificada';
  }

  get cargo(): string {
    return this.currentUser?.vecino?.cargo || 'No especificado';
  }

  get fechaInicioCargo(): string {
    const fecha = this.currentUser?.vecino?.fecha_inicio_cargo;
    if (!fecha) return 'No especificada';
    
    try {
      const date = new Date(fecha);
      return date.toLocaleDateString('es-CL', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      });
    } catch {
      return fecha;
    }
  }

  get fechaTerminoCargo(): string {
    const fecha = this.currentUser?.vecino?.fecha_termino_cargo;
    if (!fecha) return 'Cargo activo';
    
    try {
      const date = new Date(fecha);
      return date.toLocaleDateString('es-CL', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      });
    } catch {
      return fecha;
    }
  }

  constructor(
    private authService: AuthService,
    private router: Router,
    private formBuilder: FormBuilder
  ) {
    // Inicializar el formulario de edición
    this.editForm = this.formBuilder.group({
      email: ['', [Validators.required, Validators.email]],
      telefono: ['', [Validators.pattern(/^\+56\d{8,9}$/)]],
      foto_perfil: ['']
    });
  }

  ngOnInit(): void {
    this.loadUserData();
  }

  ngOnDestroy(): void {
    this.subscription.unsubscribe();
  }

  loadUserData(): void {
    // Verificar si el usuario está autenticado
    if (!this.authService.isAuthenticated()) {
      this.router.navigate(['/login']);
      return;
    }

    // Suscribirse a los cambios del usuario actual
    this.subscription.add(
      this.authService.currentUser$.subscribe({
        next: (user) => {
          this.currentUser = user;
          this.isLoading = false;
          
          if (!user) {
            // Si no hay usuario logueado, redirigir al login
            this.router.navigate(['/login']);
          }
        },
        error: (error) => {
          console.error('Error al cargar datos del usuario:', error);
          this.error = 'Error al cargar los datos del usuario';
          this.isLoading = false;
        }
      })
    );
  }

  editarPerfil(): void {
    if (!this.currentUser) return;
    
    // Rellenar el formulario con los datos actuales
    this.editForm.patchValue({
      email: this.currentUser.email,
      telefono: this.currentUser.vecino?.telefono || '',
      foto_perfil: ''
    });
    
    // Limpiar mensajes
    this.updateError = null;
    this.updateSuccess = null;
    
    // Mostrar modal
    this.showEditModal = true;
  }

  closeEditModal(): void {
    this.showEditModal = false;
    this.updateError = null;
    this.updateSuccess = null;
  }

  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (!file) return;

    // Validar tipo de archivo
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png'];
    if (!allowedTypes.includes(file.type)) {
      this.updateError = 'Tipo de archivo no permitido. Use JPEG o PNG.';
      return;
    }

    // Validar tamaño (máximo 2MB)
    const maxSize = 2 * 1024 * 1024; // 2MB
    if (file.size > maxSize) {
      this.updateError = 'La imagen es demasiado grande. Máximo 2MB permitido.';
      return;
    }

    // Convertir a base64
    const reader = new FileReader();
    reader.onload = (e: any) => {
      const base64String = e.target.result;
      this.editForm.patchValue({
        foto_perfil: base64String
      });
      this.updateError = null;
    };
    reader.readAsDataURL(file);
  }

  updateProfile(): void {
    if (this.editForm.invalid || this.isUpdating) return;

    this.isUpdating = true;
    this.updateError = null;
    this.updateSuccess = null;

    const formData = this.editForm.value;
    const updateData: UpdateProfileRequest = {};

    // Solo incluir campos que han cambiado
    if (formData.email !== this.currentUser?.email) {
      updateData.email = formData.email;
    }

    if (formData.telefono !== this.currentUser?.vecino?.telefono) {
      updateData.telefono = formData.telefono || undefined;
    }

    if (formData.foto_perfil) {
      updateData.foto_perfil = formData.foto_perfil;
    }

    // Si no hay cambios, cerrar modal
    if (Object.keys(updateData).length === 0) {
      this.updateSuccess = 'No hay cambios para actualizar';
      setTimeout(() => this.closeEditModal(), 1500);
      this.isUpdating = false;
      return;
    }

    this.subscription.add(
      this.authService.updateProfile(updateData).subscribe({
        next: (response) => {
          this.updateSuccess = response.mensaje || 'Perfil actualizado correctamente';
          this.isUpdating = false;
          
          // Cerrar modal después de un momento
          setTimeout(() => {
            this.closeEditModal();
          }, 1500);
        },
        error: (error) => {
          this.updateError = error.message || 'Error al actualizar el perfil';
          this.isUpdating = false;
        }
      })
    );
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }

  onImageError(event: any): void {
    // Si la imagen falla al cargar, usar la imagen por defecto
    console.warn('Error al cargar la imagen de perfil, usando imagen por defecto');
    event.target.src = 'images/avatar-placeholder2.svg';
  }
}