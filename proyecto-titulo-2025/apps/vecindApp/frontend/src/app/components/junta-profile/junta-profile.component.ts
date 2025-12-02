// src/app/components/junta-profile/junta-profile.component.ts
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { DirectivaService } from '../../services/directiva.service';
import { AuthService } from '../../services/auth.service';
import { JuntaService } from '../../services/junta.service';
import { EspacioService } from '../../services/espacio.service';
import { DirectivaResponse } from '../../interfaces/directiva.interface';
import { JuntaResponse, JuntaUpdateRequest, JuntaFirmaTimbreUpdateRequest } from '../../interfaces/junta.interface';
import { EspacioResponse, EspacioDirectivaUpdateRequest } from '../../interfaces/espacio.interface';
import { SignaturePadComponent } from '../signature-pad/signature-pad.component';

export interface Junta {
  id_junta: number;
  id_comuna: number;
  nombre: string;
  direccion: string;
  telefono: string;
  email: string;
  descripcion?: string;
  created_at?: string;
  comuna_nombre?: string;
  region_nombre?: string;
  logo_url?: string;
}

// Usamos DirectivaResponse del servicio, pero mantenemos esta interfaz para compatibilidad
export interface Directivo {
  id_usuario?: number;
  nombres: string;
  apellido_paterno: string;
  apellido_materno?: string;
  cargo: 'Presidente' | 'Vicepresidente' | 'Secretario' | 'Tesorero' | 'Vocal' | string;
  email?: string;
  telefono?: string;
  foto_perfil?: string;
}

@Component({
  selector: 'app-junta-profile',
  standalone: true,
  imports: [CommonModule, FormsModule, SignaturePadComponent],
  templateUrl: './junta-profile.component.html',
  styleUrls: ['./junta-profile.component.css'],
})
export class JuntaProfileComponent implements OnInit {
  // estados locales
  isLoading = true;
  error: string | null = null;

  // datos a mostrar
  junta: Junta | null = null;
  directiva: Directivo[] = [];

  // Estado de edición
  isEditMode = false;
  isSaving = false;
  editSuccess: string | null = null;
  editError: string | null = null;

  // Datos del formulario de edición
  editForm = {
    telefono: '',
    email: '',
    descripcion: '',
    logo: ''
  };

  // Control de archivo
  selectedFile: File | null = null;
  previewLogo: string | null = null;

  // Espacios de la junta
  espacios: EspacioResponse[] = [];
  isLoadingEspacios = false;
  espaciosError: string | null = null;

  // Estado de edición de espacio
  espacioEditando: EspacioResponse | null = null;
  isEditingEspacio = false;
  isSavingEspacio = false;
  espacioEditSuccess: string | null = null;
  espacioEditError: string | null = null;

  // Formulario de edición de espacio
  espacioEditForm = {
    capacidad: 0,
    valor: 0,
    foto: '',
    permitido: [] as string[],
    no_permitido: [] as string[],
    max_horas: 0
  };

  // Control de archivo de espacio
  selectedEspacioFile: File | null = null;
  previewEspacioFoto: string | null = null;

  // Inputs para actividades
  nuevaActividadPermitida = '';
  nuevaActividadNoPermitida = '';

  // Firma y timbre
  firmaActual: string | null = null;
  timbreActual: string | null = null;
  nuevaFirma: string | null = null;
  nuevoTimbre: string | null = null;
  selectedTimbreFile: File | null = null;
  previewTimbre: string | null = null;
  isSavingFirmaTimbre = false;
  firmaTimbreSuccess: string | null = null;
  firmaTimbreError: string | null = null;

  constructor(
    private route: ActivatedRoute,
    private directivaService: DirectivaService,
    private authService: AuthService,
    private juntaService: JuntaService,
    private espacioService: EspacioService
  ) {}

  ngOnInit(): void {
    // Verificar si el usuario está autenticado
    if (!this.authService.isLoggedIn()) {
      this.error = 'Debes estar logueado para ver esta información.';
      this.isLoading = false;
      return;
    }

    // Cargar datos de la junta y directivos
    this.loadJuntaProfile();
  }

  /**
   * Carga el perfil de la junta del usuario autenticado
   */
  loadJuntaProfile(): void {
    this.isLoading = true;
    this.error = null;

    // Obtener datos del usuario logueado (funciona tanto para vecinos como directivos)
    const currentUser = this.authService.getCurrentUser();
    if (!currentUser || !currentUser.vecino || !currentUser.vecino.id_junta) {
      this.error = 'Usuario no tiene una junta asociada.';
      this.isLoading = false;
      return;
    }

    // Cargar información detallada de la junta del usuario
    this.juntaService.getJuntaById(currentUser.vecino.id_junta).subscribe({
      next: (juntaData: JuntaResponse) => {
        // Convertir JuntaResponse a Junta para compatibilidad con el template
        this.junta = {
          id_junta: juntaData.id_junta,
          id_comuna: juntaData.id_comuna,
          nombre: juntaData.nombre,
          direccion: juntaData.direccion || 'Dirección no disponible',
          telefono: juntaData.telefono || 'Teléfono no disponible',
          email: juntaData.email || 'Email no disponible',
          descripcion: juntaData.descripcion || 'Descripción no disponible',
          comuna_nombre: juntaData.comuna_nombre,
          region_nombre: juntaData.region_nombre,
          logo_url: juntaData.logo || '',
          created_at: juntaData.created_at
        };

        // Cargar firma y timbre si existen
        this.firmaActual = juntaData.firma_presidente || null;
        this.timbreActual = juntaData.timbre || null;

        // Cargar directivos de la junta
        this.loadDirectivos();
      },
      error: (error: any) => {
        this.error = error.message || 'Error al cargar la información de la junta.';
        this.isLoading = false;
      }
    });
  }

  /**
   * Carga los directivos de la junta del usuario autenticado
   */
  private loadDirectivos(): void {
    this.directivaService.getMyJuntaDirectivos(false).subscribe({
      next: (directivos: DirectivaResponse[]) => {
        // Convertir DirectivaResponse a Directivo para compatibilidad con el template
        this.directiva = directivos.map(d => ({
          nombres: d.nombres,
          apellido_paterno: d.apellido_paterno,
          apellido_materno: d.apellido_materno,
          cargo: this.formatCargo(d.cargo),
          email: d.email,
          telefono: d.telefono,
          foto_perfil: d.foto_perfil
        }));

        this.isLoading = false;
        
        // Si el usuario es directiva, cargar espacios
        if (this.isDirectiva) {
          this.loadEspacios();
        }
      },
      error: (error: any) => {
        this.error = error.message || 'Error al cargar los directivos de la junta.';
        this.isLoading = false;
      }
    });
  }

  /**
   * Formatea el cargo para mostrar con la primera letra en mayúscula
   */
  private formatCargo(cargo: string): string {
    if (!cargo) return '';
    return cargo.charAt(0).toUpperCase() + cargo.slice(1).toLowerCase();
  }

  get tieneDirectiva(): boolean {
    return this.directiva.length > 0;
  }

  nombreCompleto(d: Directivo): string {
    return `${d.nombres} ${d.apellido_paterno} ${d.apellido_materno ?? ''}`.trim();
  }

  avatar(d: Directivo): string {
    if (!d.foto_perfil) return 'images/avatar-placeholder2.svg';
    return d.foto_perfil.startsWith('data:image')
      ? d.foto_perfil
      : `data:image/jpeg;base64,${d.foto_perfil}`;
  }

  cargoBadgeClass(cargo: string): string {
    const map: Record<string, string> = {
      Presidente: 'bg-primary-soft',
      Vicepresidente: 'bg-info-soft',
      Secretario: 'bg-success-soft',
      Tesorero: 'bg-warning-soft',
      Vocal: 'bg-secondary-soft',
    };
    return map[cargo] ?? 'bg-secondary-soft';
  }

  /**
   * Verifica si el usuario actual es directiva de esta junta
   */
  get isDirectiva(): boolean {
    const currentUser = this.authService.getCurrentUser();
    if (!currentUser || !currentUser.roles) {
      return false;
    }
    return currentUser.roles.includes('directiva');
  }

  /**
   * Verifica si el usuario actual es presidente activo de esta junta
   */
  get isPresidente(): boolean {
    if (!this.isDirectiva) {
      return false;
    }
    
    const currentUser = this.authService.getCurrentUser();
    if (!currentUser || !currentUser.email) {
      return false;
    }

    // Buscar presidente activo en la lista de directivos
    const presidente = this.directiva.find(d => 
      d.cargo.toLowerCase() === 'presidente'
    );

    // Verificar si el usuario actual es el presidente comparando emails
    // Nota: El backend validará correctamente los permisos
    return presidente !== undefined && presidente.email === currentUser.email;
  }

  /**
   * Activa el modo de edición
   */
  enableEditMode(): void {
    if (!this.junta) return;
    
    this.isEditMode = true;
    this.editSuccess = null;
    this.editError = null;
    
    // Cargar datos actuales en el formulario
    this.editForm = {
      telefono: this.junta.telefono || '',
      email: this.junta.email || '',
      descripcion: this.junta.descripcion || '',
      logo: ''
    };
    
    this.previewLogo = this.junta.logo_url || null;
  }

  /**
   * Cancela el modo de edición
   */
  cancelEdit(): void {
    this.isEditMode = false;
    this.editSuccess = null;
    this.editError = null;
    this.selectedFile = null;
    this.previewLogo = null;
  }

  /**
   * Maneja la selección de archivo de logo
   */
  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (!input.files || input.files.length === 0) {
      return;
    }

    const file = input.files[0];
    
    // Validar tipo de archivo
    if (!file.type.match(/image\/(jpeg|jpg|png|svg\+xml)/)) {
      this.editError = 'Solo se permiten imágenes JPEG, PNG o SVG';
      return;
    }

    // Validar tamaño (máximo 5MB)
    if (file.size > 5 * 1024 * 1024) {
      this.editError = 'La imagen es muy grande. Máximo 5MB permitido';
      return;
    }

    this.selectedFile = file;
    this.editError = null;

    // Generar preview
    const reader = new FileReader();
    reader.onload = (e: ProgressEvent<FileReader>) => {
      this.previewLogo = e.target?.result as string;
    };
    reader.readAsDataURL(file);
  }

  /**
   * Guarda los cambios de la junta
   */
  saveChanges(): void {
    if (!this.junta) return;

    this.isSaving = true;
    this.editSuccess = null;
    this.editError = null;

    // Preparar datos para enviar (solo los campos modificados)
    const updateData: JuntaUpdateRequest = {};
    
    // Comparar teléfono (trimear espacios para comparación correcta)
    const telefonoActual = (this.junta.telefono || '').trim();
    const telefonoNuevo = (this.editForm.telefono || '').trim();
    if (telefonoNuevo && telefonoNuevo !== telefonoActual) {
      updateData.telefono = telefonoNuevo;
    }
    
    // Comparar email
    const emailActual = (this.junta.email || '').trim();
    const emailNuevo = (this.editForm.email || '').trim();
    if (emailNuevo && emailNuevo !== emailActual) {
      updateData.email = emailNuevo;
    }
    
    // Comparar descripción
    const descripcionActual = (this.junta.descripcion || '').trim();
    const descripcionNueva = (this.editForm.descripcion || '').trim();
    if (descripcionNueva !== descripcionActual) {
      updateData.descripcion = descripcionNueva;
    }
    
    // Comparar logo (solo si se seleccionó uno nuevo)
    if (this.previewLogo && this.previewLogo !== this.junta.logo_url) {
      updateData.logo = this.previewLogo;
    }

    // Validar que al menos un campo fue modificado
    if (Object.keys(updateData).length === 0) {
      this.editError = 'No se detectaron cambios para guardar';
      this.isSaving = false;
      return;
    }

    // Llamar al servicio
    this.juntaService.updateJunta(this.junta.id_junta, updateData).subscribe({
      next: (response) => {
        // Actualizar datos locales con los valores del servidor
        if (this.junta) {
          // Solo actualizar si el servidor devuelve el campo
          if (response.telefono !== undefined && response.telefono !== null) {
            this.junta.telefono = response.telefono;
          }
          if (response.email !== undefined && response.email !== null) {
            this.junta.email = response.email;
          }
          if (response.descripcion !== undefined && response.descripcion !== null) {
            this.junta.descripcion = response.descripcion;
          }
          if (response.logo !== undefined && response.logo !== null) {
            this.junta.logo_url = response.logo;
          }
        }
        
        this.editSuccess = response.mensaje || 'Junta actualizada exitosamente';
        this.isSaving = false;
        
        // Cerrar modo de edición después de 2 segundos
        setTimeout(() => {
          this.isEditMode = false;
          this.editSuccess = null;
          this.selectedFile = null;
          this.previewLogo = null;
        }, 2000);
      },
      error: (error: any) => {
        this.editError = error.message || 'Error al actualizar la junta';
        this.isSaving = false;
      }
    });
  }

  /**
   * Carga los espacios de la junta
   */
  loadEspacios(): void {
    if (!this.junta) return;

    this.isLoadingEspacios = true;
    this.espaciosError = null;

    this.espacioService.getEspaciosByJunta(this.junta.id_junta, true, 1, 50).subscribe({
      next: (response) => {
        this.espacios = response.espacios;
        this.isLoadingEspacios = false;
      },
      error: (error) => {
        this.espaciosError = 'Error al cargar espacios';
        this.isLoadingEspacios = false;
      }
    });
  }

  /**
   * Habilita el modo de edición para un espacio
   */
  editarEspacio(espacio: EspacioResponse): void {
    this.espacioEditando = espacio;
    this.isEditingEspacio = true;
    this.espacioEditSuccess = null;
    this.espacioEditError = null;
    this.selectedEspacioFile = null;
    this.previewEspacioFoto = null;

    // Inicializar formulario con datos actuales
    // Asegurar que los arrays siempre sean arrays, nunca null o undefined
    const permitidoInicial = Array.isArray(espacio.permitido) ? [...espacio.permitido] : [];
    const noPermitidoInicial = Array.isArray(espacio.no_permitido) ? [...espacio.no_permitido] : [];
    
    this.espacioEditForm = {
      capacidad: espacio.capacidad,
      valor: Number(espacio.valor),
      foto: '',
      permitido: permitidoInicial,
      no_permitido: noPermitidoInicial,
      max_horas: espacio.max_horas
    };
  }

  /**
   * Elimina un espacio (solo directiva). Pide confirmación y refresca la lista.
   */
  eliminarEspacio(espacio: EspacioResponse): void {
    if (!espacio || !this.isDirectiva) return;
    const confirmado = confirm(`¿Seguro que deseas eliminar el espacio "${espacio.nombre}"?`);
    if (!confirmado) return;

    this.isLoadingEspacios = true;
    this.espaciosError = null;

    this.espacioService.deleteEspacioDirectiva(espacio.id_espacio).subscribe({
      next: () => {
        // Quitar de la lista local
        this.espacios = this.espacios.filter(e => e.id_espacio !== espacio.id_espacio);
        this.isLoadingEspacios = false;
      },
      error: (error) => {
        this.espaciosError = error.message || 'Error al eliminar el espacio';
        this.isLoadingEspacios = false;
      }
    });
  }

  /**
   * Cancela la edición de un espacio
   */
  cancelarEditarEspacio(): void {
    this.espacioEditando = null;
    this.isEditingEspacio = false;
    this.espacioEditSuccess = null;
    this.espacioEditError = null;
    this.selectedEspacioFile = null;
    this.previewEspacioFoto = null;
    this.nuevaActividadPermitida = '';
    this.nuevaActividadNoPermitida = '';
  }

  /**
   * Maneja la selección de archivo de foto del espacio
   */
  onEspacioFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];

    if (!file) return;

    // Validar tipo de archivo
    if (!file.type.startsWith('image/')) {
      this.espacioEditError = 'Por favor selecciona una imagen válida';
      return;
    }

    // Validar tamaño (máximo 5MB)
    if (file.size > 5 * 1024 * 1024) {
      this.espacioEditError = 'La imagen no puede ser mayor a 5MB';
      return;
    }

    this.selectedEspacioFile = file;
    this.espacioEditError = null;

    // Generar preview
    const reader = new FileReader();
    reader.onload = () => {
      this.previewEspacioFoto = reader.result as string;
      this.espacioEditForm.foto = reader.result as string;
    };
    reader.readAsDataURL(file);
  }

  /**
   * Agrega una actividad permitida
   */
  agregarActividadPermitida(): void {
    const actividad = this.nuevaActividadPermitida.trim();
    
    if (!actividad) {
      return;
    }
    
    if (this.espacioEditForm.permitido.includes(actividad)) {
      return;
    }
    
    this.espacioEditForm.permitido = [...this.espacioEditForm.permitido, actividad];
    this.nuevaActividadPermitida = '';
  }

  /**
   * Elimina una actividad permitida
   */
  eliminarActividadPermitida(index: number): void {
    this.espacioEditForm.permitido = this.espacioEditForm.permitido.filter((_, i) => i !== index);
  }

  /**
   * Agrega una actividad no permitida
   */
  agregarActividadNoPermitida(): void {
    const actividad = this.nuevaActividadNoPermitida.trim();
    if (actividad && !this.espacioEditForm.no_permitido.includes(actividad)) {
      this.espacioEditForm.no_permitido = [...this.espacioEditForm.no_permitido, actividad];
      this.nuevaActividadNoPermitida = '';
    }
  }

  /**
   * Elimina una actividad no permitida
   */
  eliminarActividadNoPermitida(index: number): void {
    this.espacioEditForm.no_permitido = this.espacioEditForm.no_permitido.filter((_, i) => i !== index);
  }

  /**
   * Guarda los cambios del espacio
   */
  guardarCambiosEspacio(): void {
    if (!this.espacioEditando) return;

    // Antes de guardar, agregar cualquier actividad que esté escrita pero no agregada
    if (this.nuevaActividadPermitida.trim()) {
      this.agregarActividadPermitida();
    }
    if (this.nuevaActividadNoPermitida.trim()) {
      this.agregarActividadNoPermitida();
    }

    this.isSavingEspacio = true;
    this.espacioEditSuccess = null;
    this.espacioEditError = null;

    // Preparar datos para enviar (solo los campos modificados)
    const updateData: EspacioDirectivaUpdateRequest = {};
    
    // Comparar capacidad
    if (this.espacioEditForm.capacidad !== this.espacioEditando.capacidad) {
      updateData.capacidad = this.espacioEditForm.capacidad;
    }
    
    // Comparar valor
    if (this.espacioEditForm.valor !== Number(this.espacioEditando.valor)) {
      updateData.valor = this.espacioEditForm.valor;
    }
    
    // Comparar max_horas
    if (this.espacioEditForm.max_horas !== this.espacioEditando.max_horas) {
      updateData.max_horas = this.espacioEditForm.max_horas;
    }
    
    // Comparar foto (solo si se seleccionó una nueva)
    if (this.previewEspacioFoto && this.previewEspacioFoto !== this.espacioEditando.foto) {
      updateData.foto = this.previewEspacioFoto;
    }
    
    // Siempre incluir actividades permitidas y no permitidas
    // Esto evita problemas de comparación con arrays vacíos o null de PostgreSQL
    updateData.permitido = this.espacioEditForm.permitido || [];
    updateData.no_permitido = this.espacioEditForm.no_permitido || [];

    // Validar que al menos un campo fue modificado
    // Como siempre enviamos permitido y no_permitido, verificamos que haya al menos un cambio real
    const hasOtherChanges = updateData.capacidad !== undefined || 
                           updateData.valor !== undefined || 
                           updateData.max_horas !== undefined || 
                           updateData.foto !== undefined;
    
    const hasActivityChanges = 
      JSON.stringify([...(this.espacioEditando.permitido || [])].sort()) !== 
      JSON.stringify([...(this.espacioEditForm.permitido || [])].sort()) ||
      JSON.stringify([...(this.espacioEditando.no_permitido || [])].sort()) !== 
      JSON.stringify([...(this.espacioEditForm.no_permitido || [])].sort());

    if (!hasOtherChanges && !hasActivityChanges) {
      this.espacioEditError = 'No se detectaron cambios para guardar';
      this.isSavingEspacio = false;
      return;
    }

    // Llamar al servicio
    this.espacioService.updateEspacioDirectiva(this.espacioEditando.id_espacio, updateData).subscribe({
      next: (response) => {
        // Actualizar el espacio en la lista local
        const index = this.espacios.findIndex(e => e.id_espacio === this.espacioEditando!.id_espacio);
        if (index !== -1) {
          this.espacios[index] = {
            ...this.espacios[index],
            capacidad: response.capacidad,
            valor: response.valor,
            foto: response.foto,
            permitido: response.permitido,
            no_permitido: response.no_permitido,
            max_horas: response.max_horas
          };
        }
        
        this.espacioEditSuccess = response.mensaje || 'Espacio actualizado exitosamente';
        this.isSavingEspacio = false;
        
        // Cerrar modo de edición después de 2 segundos
        setTimeout(() => {
          this.cancelarEditarEspacio();
        }, 2000);
      },
      error: (error: any) => {
        this.espacioEditError = error.message || 'Error al actualizar el espacio';
        this.isSavingEspacio = false;
      }
    });
  }

  /**
   * Maneja cambios en la firma
   */
  onFirmaChange(firmaBase64: string | null): void {
    this.nuevaFirma = firmaBase64;
  }

  /**
   * Maneja la selección de archivo de timbre
   */
  onTimbreFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (!input.files || input.files.length === 0) {
      return;
    }

    const file = input.files[0];
    
    // Validar tipo de archivo
    if (!file.type.match(/image\/(jpeg|jpg|png|svg\+xml)/)) {
      this.firmaTimbreError = 'Solo se permiten imágenes JPEG, PNG o SVG';
      return;
    }

    // Validar tamaño (máximo 5MB)
    if (file.size > 5 * 1024 * 1024) {
      this.firmaTimbreError = 'La imagen es muy grande. Máximo 5MB permitido';
      return;
    }

    this.selectedTimbreFile = file;
    this.firmaTimbreError = null;

    // Generar preview y convertir a base64
    const reader = new FileReader();
    reader.onload = (e: ProgressEvent<FileReader>) => {
      this.previewTimbre = e.target?.result as string;
      this.nuevoTimbre = e.target?.result as string;
    };
    reader.readAsDataURL(file);
  }

  /**
   * Guarda la firma y/o timbre
   */
  saveFirmaTimbre(): void {
    if (!this.junta) return;

    // Validar que hay algo para guardar
    if (!this.nuevaFirma && !this.nuevoTimbre) {
      this.firmaTimbreError = 'Debes proporcionar al menos una firma o un timbre';
      return;
    }

    this.isSavingFirmaTimbre = true;
    this.firmaTimbreSuccess = null;
    this.firmaTimbreError = null;

    const updateData: JuntaFirmaTimbreUpdateRequest = {};
    
    if (this.nuevaFirma) {
      updateData.firma_presidente = this.nuevaFirma;
    }
    
    if (this.nuevoTimbre) {
      updateData.timbre = this.nuevoTimbre;
    }

    this.juntaService.updateFirmaTimbre(this.junta.id_junta, updateData).subscribe({
      next: (response) => {
        // Actualizar datos locales
        if (this.junta) {
          if (response.firma_presidente !== undefined) {
            this.firmaActual = response.firma_presidente;
            this.nuevaFirma = null;
          }
          if (response.timbre !== undefined) {
            this.timbreActual = response.timbre;
            this.nuevoTimbre = null;
            this.previewTimbre = null;
            this.selectedTimbreFile = null;
          }
        }
        
        this.firmaTimbreSuccess = response.mensaje || 'Firma y timbre actualizados exitosamente';
        this.isSavingFirmaTimbre = false;
        
        // Limpiar mensaje después de 3 segundos
        setTimeout(() => {
          this.firmaTimbreSuccess = null;
        }, 3000);
      },
      error: (error: any) => {
        this.firmaTimbreError = error.message || 'Error al actualizar firma y timbre';
        this.isSavingFirmaTimbre = false;
      }
    });
  }
}
