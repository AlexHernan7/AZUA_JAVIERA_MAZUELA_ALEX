import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { Subscription } from 'rxjs';
import { AuthService } from '../../services/auth.service';
import { UserLoginData, UpdateProfileRequest, ChangePasswordRequest} from '../../interfaces/auth.interface';
import { TramitesComponent } from '../tramites/tramites.component';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule, RouterModule],
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

  // Variables para el modal de cambio de contraseña
  showPasswordModal: boolean = false;
  passwordForm: FormGroup;
  isChangingPassword: boolean = false;
  passwordError: string | null = null;
  passwordSuccess: string | null = null;
  
  // Variables para selección de región/comuna
  regiones: any[] = [];
  comunas: any[] = [];
  regionSeleccionada: string = '';
  
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

  go(path: string) { this.router.navigate([path]); }

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
      apellido_paterno: ['', [Validators.required, Validators.minLength(2)]],
      apellido_materno: ['', [Validators.minLength(2)]],
      email: ['', [Validators.required, Validators.email]],
      telefono: ['', [Validators.pattern(/^\+56\d{8,9}$/)]],
      direccion: ['', [Validators.minLength(5)]],
      region: [{value: '', disabled: false}],
      comuna: [{value: '', disabled: true}],
      foto_perfil: ['']
    });

    // Inicializar el formulario de cambio de contraseña
    this.passwordForm = this.formBuilder.group({
      current_password: ['', [Validators.required]],
      new_password: ['', [Validators.required, Validators.minLength(8), Validators.maxLength(12)]],
      confirm_password: ['', [Validators.required]]
    });
  }

  ngOnInit(): void {
    this.loadUserData();
    this.loadRegiones();
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

  loadRegiones(): void {
    this.authService.getRegiones().subscribe({
      next: (response) => {
        this.regiones = response.regiones || [];
      },
      error: (error) => {
        console.error('Error al cargar regiones:', error);
      }
    });
  }

  onRegionChange(event: any): void {
    const regionNombre = event.target.value;
    if (!regionNombre) {
      this.comunas = [];
      this.editForm.get('comuna')?.setValue('');
      this.editForm.get('comuna')?.disable();
      return;
    }

    this.regionSeleccionada = regionNombre;
    this.editForm.get('comuna')?.setValue('');
    this.editForm.get('comuna')?.disable();
    
    this.authService.getComunasByRegion(regionNombre).subscribe({
      next: (response: any) => {
        this.comunas = response.comunas || [];
        this.editForm.get('comuna')?.enable();
      },
      error: (error) => {
        console.error('Error al cargar comunas:', error);
        this.comunas = [];
        this.editForm.get('comuna')?.enable();
      }
    });
  }

  editarPerfil(): void {
    if (!this.currentUser) return;

    // Rellenar el formulario con los datos actuales
    this.editForm.patchValue({
      apellido_paterno: this.currentUser.apellido_paterno,
      apellido_materno: this.currentUser.apellido_materno || '',
      email: this.currentUser.email,
      telefono: this.currentUser.vecino?.telefono || '',
      direccion: this.currentUser.vecino?.direccion || '',
      region: this.currentUser.vecino?.region || '',
      comuna: this.currentUser.vecino?.comuna || '',
      foto_perfil: ''
    });
    
    // Si hay región seleccionada, cargar las comunas
    if (this.currentUser.vecino?.region) {
      this.regionSeleccionada = this.currentUser.vecino.region;
      this.editForm.get('comuna')?.disable();
      
      // Buscar el ID de la región por su nombre
      const regionEncontrada = this.regiones.find(r => r.nombre === this.regionSeleccionada);
      if (regionEncontrada) {
        this.authService.getComunasByRegion(regionEncontrada.id_region).subscribe({
          next: (response: any) => {
            this.comunas = response.comunas || [];
            this.editForm.get('comuna')?.enable();
          },
          error: (error) => {
            console.error('Error cargando comunas:', error);
            this.editForm.get('comuna')?.enable();
          }
        });
      } else {
        this.editForm.get('comuna')?.enable();
      }
    }
    
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

    // Obtener todos los valores del formulario (incluyendo disabled)
    const formData = this.editForm.getRawValue();
    const updateData: UpdateProfileRequest = {};

    // Incluir campos que han cambiado (verificar solo si son diferentes, no si están vacíos)
    if (formData.apellido_paterno !== this.currentUser?.apellido_paterno) {
      updateData.apellido_paterno = formData.apellido_paterno;
    }

    if (formData.apellido_materno !== (this.currentUser?.apellido_materno || '')) {
      updateData.apellido_materno = formData.apellido_materno || '';
    }

    if (formData.email !== this.currentUser?.email) {
      updateData.email = formData.email;
    }

    if (formData.telefono !== (this.currentUser?.vecino?.telefono || '')) {
      updateData.telefono = formData.telefono || '';
    }

    if (formData.direccion !== (this.currentUser?.vecino?.direccion || '')) {
      updateData.direccion = formData.direccion || '';
    }

    // Manejar cambio de comuna - enviar el nombre para que el backend busque el ID
    if (formData.comuna && formData.comuna !== (this.currentUser?.vecino?.comuna || '')) {
      updateData.comuna_nombre = formData.comuna;
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

  cambiarContrasena(): void {
    // Limpiar formulario y mensajes
    this.passwordForm.reset();
    this.passwordError = null;
    this.passwordSuccess = null;
    
    // Mostrar modal
    this.showPasswordModal = true;
  }

  closePasswordModal(): void {
    this.showPasswordModal = false;
    this.passwordForm.reset();
    this.passwordError = null;
    this.passwordSuccess = null;
  }

  changePassword(): void {
    if (this.passwordForm.invalid || this.isChangingPassword) return;

    // Verificar que las contraseñas coincidan
    const formData = this.passwordForm.value;
    if (formData.new_password !== formData.confirm_password) {
      this.passwordError = 'Las contraseñas nuevas no coinciden';
      return;
    }

    this.isChangingPassword = true;
    this.passwordError = null;
    this.passwordSuccess = null;

    const passwordData: ChangePasswordRequest = {
      current_password: formData.current_password,
      new_password: formData.new_password
    };

    this.subscription.add(
      this.authService.changePassword(passwordData).subscribe({
        next: (response) => {
          this.passwordSuccess = response.mensaje || 'Contraseña actualizada exitosamente';
          this.isChangingPassword = false;
          
          // Cerrar modal después de un momento
          setTimeout(() => {
            this.closePasswordModal();
          }, 1500);
        },
        error: (error) => {
          this.passwordError = error.message || 'Error al cambiar la contraseña';
          this.isChangingPassword = false;
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