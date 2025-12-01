import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth.service';
import { VecinoListItem, DirectivaListItem } from '../../interfaces/auth.interface';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-user-management',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './user-management.component.html',
  styleUrl: './user-management.component.css',
})
export class UserManagementComponent implements OnInit, OnDestroy {
  vecinos: VecinoListItem[] = [];
  directivos: DirectivaListItem[] = [];
  
  vecinosFiltrados: VecinoListItem[] = [];
  directivosFiltrados: DirectivaListItem[] = [];
  
  filtroEstado: 'todos' | 'activos' | 'inactivos' = 'todos';
  vistaActual: 'vecinos' | 'directivos' = 'vecinos';
  
  isLoading = false;
  error: string | null = null;
  isAdmin = false;
  
  private subscription: Subscription = new Subscription();

  constructor(private authService: AuthService) {
    // Detectar si el usuario es admin
    const currentUser = this.authService.getCurrentUser();
    this.isAdmin = currentUser?.roles?.includes('admin') || false;
  }

  ngOnInit(): void {
    this.cargarDatos();
  }

  ngOnDestroy(): void {
    this.subscription.unsubscribe();
  }

  /**
   * Carga tanto vecinos como directivos
   */
  cargarDatos(): void {
    this.isLoading = true;
    this.error = null;

    let vecinosCargados = false;
    let directivosCargados = false;

    const finalizarCarga = () => {
      if (vecinosCargados && directivosCargados) {
        this.isLoading = false;
      }
    };

    // Si es admin, obtener todos los usuarios del sistema
    // Si no es admin (es directivo), obtener solo de su junta
    if (this.isAdmin) {
      // Cargar TODOS los vecinos (admin)
      this.subscription.add(
        this.authService.getAllVecinosAdmin().subscribe({
          next: (data) => {
            this.vecinos = data;
            vecinosCargados = true;
            this.aplicarFiltros();
            finalizarCarga();
          },
          error: (err) => {
            this.error = 'Error al cargar la lista de vecinos';
            vecinosCargados = true;
            finalizarCarga();
          }
        })
      );

      // Cargar TODOS los directivos (admin)
      this.subscription.add(
        this.authService.getAllDirectivosAdmin().subscribe({
          next: (data) => {
            this.directivos = data;
            directivosCargados = true;
            this.aplicarFiltros();
            finalizarCarga();
          },
          error: (err) => {
            this.error = 'Error al cargar la lista de directivos';
            directivosCargados = true;
            finalizarCarga();
          }
        })
      );
    } else {
      // Cargar vecinos de mi junta (directivo)
      this.subscription.add(
        this.authService.getVecinosMyJunta(false).subscribe({
          next: (data) => {
            this.vecinos = data;
            vecinosCargados = true;
            this.aplicarFiltros();
            finalizarCarga();
          },
          error: (err) => {
            this.error = 'Error al cargar la lista de vecinos';
            vecinosCargados = true;
            finalizarCarga();
          }
        })
      );

      // Cargar directivos de mi junta (directivo)
      this.subscription.add(
        this.authService.getDirectivosMyJunta(false).subscribe({
          next: (data) => {
            this.directivos = data;
            directivosCargados = true;
            this.aplicarFiltros();
            finalizarCarga();
          },
          error: (err) => {
            this.error = 'Error al cargar la lista de directivos';
            directivosCargados = true;
            finalizarCarga();
          }
        })
      );
    }
  }

  /**
   * Aplica los filtros seleccionados
   */
  aplicarFiltros(): void {
    // Filtrar vecinos
    switch (this.filtroEstado) {
      case 'activos':
        this.vecinosFiltrados = this.vecinos.filter(v => v.activo);
        break;
      case 'inactivos':
        this.vecinosFiltrados = this.vecinos.filter(v => !v.activo);
        break;
      default:
        this.vecinosFiltrados = [...this.vecinos];
    }

    // Los directivos no tienen estado activo/inactivo en el schema actual
    // pero podemos filtrarlos si es necesario
    this.directivosFiltrados = [...this.directivos];
  }

  /**
   * Cambia el filtro de estado
   */
  cambiarFiltroEstado(estado: 'todos' | 'activos' | 'inactivos'): void {
    this.filtroEstado = estado;
    this.aplicarFiltros();
  }

  /**
   * Cambia la vista entre vecinos y directivos
   */
  cambiarVista(vista: 'vecinos' | 'directivos'): void {
    this.vistaActual = vista;
  }

  /**
   * Obtiene el avatar o usa placeholder
   */
  getAvatarUrl(fotoBase64: string | undefined): string {
    if (fotoBase64) {
      return fotoBase64;
    }
    return 'assets/images/avatar-placeholder.svg';
  }

  /**
   * Obtiene el nombre completo
   */
  getNombreCompleto(item: VecinoListItem | DirectivaListItem): string {
    const apellidoMaterno = item.apellido_materno ? ` ${item.apellido_materno}` : '';
    return `${item.nombres} ${item.apellido_paterno}${apellidoMaterno}`;
  }

  /**
   * Formatea el RUT para mejor visualización
   */
  formatearRut(rut: string): string {
    if (!rut) return '';
    
    // Eliminar puntos y guiones existentes
    const rutLimpio = rut.replace(/\./g, '').replace(/-/g, '');
    
    // Separar el dígito verificador
    const dv = rutLimpio.slice(-1);
    let rutNumero = rutLimpio.slice(0, -1);
    
    // Agregar puntos cada 3 dígitos
    rutNumero = rutNumero.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    
    return `${rutNumero}-${dv}`;
  }

  /**
   * Obtiene la clase CSS para el badge de estado
   */
  getEstadoClass(activo: boolean): string {
    return activo ? 'badge-success' : 'badge-danger';
  }

  /**
   * Obtiene el texto del estado
   */
  getEstadoTexto(activo: boolean): string {
    return activo ? 'Activo' : 'Inactivo';
  }
}
