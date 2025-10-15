import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpClientModule, HttpHeaders } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

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
  // Ajusta la base URL a tu backend
  private readonly BASE_URL = '/api/admin';

  loading = false;
  error = '';
  q = ''; // búsqueda

  allUsers: SystemUser[] = [];
  // estados de carga por fila
  rowBusy = new Set<number>();

  constructor(private http: HttpClient) {}

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
    
    const headers = this.getAuthHeaders();
    
    this.http
      .get<{ usuarios: SystemUser[] }>(`${this.BASE_URL}/usuarios?limit=1000`, { headers })
      .subscribe({
        next: (res) => {
          // excluir admins
          this.allUsers = (res.usuarios || []).filter(
            u => !(u.roles || []).includes('admin')
          );
          // orden alfabético por apellido/nombre
          this.allUsers.sort((a, b) =>
            (this.displayName(a)).localeCompare(this.displayName(b), 'es')
          );
          this.loading = false;
        },
        error: (err) => {
          console.error(err);
          this.error = 'No se pudieron cargar los usuarios.';
          this.loading = false;
        },
      });
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
    if (this.rowBusy.has(u.id_usuario)) return;
    const nuevo = !u.activo;

    const headers = this.getAuthHeaders();

    this.rowBusy.add(u.id_usuario);
    this.http
      .patch(`${this.BASE_URL}/usuarios/${u.id_usuario}/estado`, { activo: nuevo }, { headers })
      .subscribe({
        next: () => {
          u.activo = nuevo; // éxito optimista
          this.rowBusy.delete(u.id_usuario);
        },
        error: (err) => {
          console.error(err);
          this.rowBusy.delete(u.id_usuario);
          alert('No se pudo actualizar el estado del usuario.');
        },
      });
  }
}
