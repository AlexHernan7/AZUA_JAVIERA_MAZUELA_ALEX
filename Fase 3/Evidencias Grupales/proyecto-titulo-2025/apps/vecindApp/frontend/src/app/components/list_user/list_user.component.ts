import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpClientModule, HttpHeaders } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth.service';
import { VecinoListItem, DirectivaListItem } from '../../interfaces/auth.interface';
import { forkJoin } from 'rxjs';
import { environment } from '../../../environments/environment';

type RoleCode = 'admin' | 'vecino' | 'directiva';

interface SystemUser {
  id_usuario: number;
  email: string;
  activo: boolean;
  roles: RoleCode[];          // p.ej.: ["vecino"] | ["directiva"] | ["admin","directiva"]
  nombres?: string;
  apellido_paterno?: string;
  apellido_materno?: string | null;
  junta_nombre?: string;      // opcional, si tu API lo entrega
  created_at?: string;        // ISO
}

@Component({
  selector: 'app-list-user',
  standalone: true,
  imports: [CommonModule, HttpClientModule, FormsModule],
  templateUrl: './list_user.component.html',
  styleUrls: ['./list_user.component.css'],
})
export class ListUserComponent implements OnInit {
  // Usa la URL base del environment para apuntar a Railway
  // La ruta del backend es: /api/admin/usuarios/{id}/estado
  private readonly BASE_URL = `${environment.apiUrl}/admin`;

  loading = false;
  error = '';
  q = ''; // búsqueda

  allUsers: SystemUser[] = [];
  // estados de carga por fila
  rowBusy = new Set<number>();
  // estados de colapsado por sección
  showDirectiva = false;
  showVecinos = false;

  constructor(private http: HttpClient, private auth: AuthService) {}

  ngOnInit(): void {
    this.fetchUsers();
  }

  /**
   * Obtiene los headers de autenticación con el token
   */
  private getAuthHeaders(): HttpHeaders {
    const token = localStorage.getItem('vecindapp_token');
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
  }

  fetchUsers(): void {
    this.loading = true;
    this.error = '';
    
    if (this.isAdmin) {
      // Admin: cargar TODOS los vecinos y TODOS los directivos del sistema
      forkJoin({
        vecinos: this.auth.getAllVecinosAdmin(),
        directivos: this.auth.getAllDirectivosAdmin()
      }).subscribe({
        next: ({ vecinos, directivos }) => {
          const vecinosArr = vecinos as VecinoListItem[];
          const mappedVecinos: SystemUser[] = vecinosArr.map(v => ({
            id_usuario: v.id_usuario,
            email: v.email,
            activo: v.activo,
            roles: ['vecino'],
            nombres: v.nombres,
            apellido_paterno: v.apellido_paterno,
            apellido_materno: v.apellido_materno ?? null,
            junta_nombre: v.junta_nombre
          }));
          
          const mappedDirectivos: SystemUser[] = (directivos as DirectivaListItem[]).map((d) => ({
            id_usuario: d.id_usuario,
            email: d.email,
            activo: true,
            roles: ['directiva'],
            nombres: d.nombres,
            apellido_paterno: d.apellido_paterno,
            apellido_materno: d.apellido_materno ?? null,
            junta_nombre: d.junta_nombre
          }));

          this.allUsers = [...mappedDirectivos, ...mappedVecinos];
          this.allUsers.sort((a, b) =>
            (this.displayName(a)).localeCompare(this.displayName(b), 'es')
          );
          
          this.loading = false;
        },
        error: (err) => {
          this.error = 'No se pudieron cargar los usuarios.';
          this.loading = false;
        }
      });
    } else {
      // Directiva/vecino: cargar solo usuarios de mi junta
      forkJoin({
        vecinos: this.auth.getVecinosMyJunta(false),
        directivos: this.auth.getDirectivosMyJunta(false)
      }).subscribe({
        next: ({ vecinos, directivos }) => {
          const vecinosArr = vecinos as VecinoListItem[];
          const mappedVecinos: SystemUser[] = vecinosArr.map(v => ({
            id_usuario: v.id_usuario,
            email: v.email,
            activo: v.activo,
            roles: ['vecino'],
            nombres: v.nombres,
            apellido_paterno: v.apellido_paterno,
            apellido_materno: v.apellido_materno ?? null,
            junta_nombre: v.junta_nombre
          }));
          const juntaNombre = vecinosArr.find(v => !!v.junta_nombre)?.junta_nombre
            || this.auth.getCurrentUser()?.vecino?.junta
            || undefined;
          const mappedDirectivos: SystemUser[] = (directivos as DirectivaListItem[]).map((d) => ({
            id_usuario: d.id_usuario,
            email: d.email,
            activo: true,
            roles: ['directiva'],
            nombres: d.nombres,
            apellido_paterno: d.apellido_paterno,
            apellido_materno: d.apellido_materno ?? null,
            junta_nombre: juntaNombre
          }));

          this.allUsers = [...mappedDirectivos, ...mappedVecinos];
          this.allUsers.sort((a, b) =>
            (this.displayName(a)).localeCompare(this.displayName(b), 'es')
          );
          
          this.loading = false;
        },
        error: (err) => {
          this.error = 'No se pudieron cargar los usuarios de tu junta.';
          this.loading = false;
        }
      });
    }
  }

  // Helpers de UI
  displayName(u: SystemUser): string {
    const ap = u.apellido_paterno ?? '';
    const am = u.apellido_materno ?? '';
    const nom = u.nombres ?? '';
    const n = `${nom} ${ap} ${am}`.trim();
    return n || u.email;
  }

  matchesQuery(u: SystemUser): boolean {
    if (!this.q) return true;
    const q = this.q.toLowerCase();
    return (
      this.displayName(u).toLowerCase().includes(q) ||
      (u.email || '').toLowerCase().includes(q) ||
      (u.junta_nombre || '').toLowerCase().includes(q)
    );
  }

  // Agrupación por rol (si un usuario tiene ambos, lo mostramos en Directiva por prioridad)
  get directiva(): SystemUser[] {
    return this.allUsers
      .filter(u => (u.roles || []).includes('directiva'))
      .filter(u => this.matchesQuery(u));
  }
  get vecinos(): SystemUser[] {
    return this.allUsers
      .filter(u => !(u.roles || []).includes('directiva') && (u.roles || []).includes('vecino'))
      .filter(u => this.matchesQuery(u));
  }

  // Toggle estado
  toggleActive(u: SystemUser): void {
    // Admin usa endpoint de admin; directiva usa endpoint de directiva para su junta
    if (this.rowBusy.has(u.id_usuario)) return;
    const nuevo = !u.activo;

    const headers = this.getAuthHeaders();

    this.rowBusy.add(u.id_usuario);
    const req$ = this.isAdmin
      ? this.http.patch(`${this.BASE_URL}/usuarios/${u.id_usuario}/estado`, { activo: nuevo }, { headers })
      : this.http.patch(`${environment.apiUrl}/users/directiva/usuarios/${u.id_usuario}/estado`, { activo: nuevo }, { headers });

    req$
      .subscribe({
        next: () => {
          u.activo = nuevo; // éxito optimista
          this.rowBusy.delete(u.id_usuario);
        },
        error: (err) => {
          this.rowBusy.delete(u.id_usuario);
          alert('No se pudo actualizar el estado del usuario.');
        },
      });
  }

  // Roles helpers
  private currentRoles(): string[] {
    return this.auth.getCurrentUser()?.roles || [];
  }
  get isAdmin(): boolean {
    return this.currentRoles().includes('admin');
  }
}
