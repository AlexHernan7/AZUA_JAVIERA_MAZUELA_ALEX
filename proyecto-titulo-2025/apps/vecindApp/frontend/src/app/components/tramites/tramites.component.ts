import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';

type Certificado = {
  titulo: string;
  fecha: string;   // texto formateado
  id?: number;
};

type Reserva = {
  espacio: string;
  fecha: string;   // texto formateado
  id?: number;
};

@Component({
  selector: 'app-tramites',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './tramites.component.html'
})
export class TramitesComponent {

  // Mock de datos (puedes mapearlos a lo que te devuelva tu API)
  certificados: Certificado[] = [
    { titulo: 'Certificado recursuada',  fecha: '10 de abril de 2024', id: 101 },
    { titulo: 'Certificados descargada', fecha: '28 de abril de 2024', id: 102 },
    { titulo: 'Solicitud certaiocaolaada', fecha: '2 de marzo de 2024', id: 103 },
  ];

  reservas: Reserva[] = [
    { espacio: 'Sancha 10 am', fecha: '20 de abril de 2024', id: 201 },
    { espacio: 'Sala 1 am',   fecha: '5 de abril de 2024',  id: 202 },
    { espacio: 'Sala 2',      fecha: '24 de abril de 2024', id: 203 },
  ];

  constructor(private router: Router) {}

  // Acciones
  solicitarCertificado() {
    // si está autenticado, navega al flujo de certificados; si no, al login
    this.router.navigate(['/certificados/residencia/crear']);
    // o: this.router.navigate(['/login']);
  }

  hacerReserva() {
    this.router.navigate(['/reservas']); // ajusta a tu ruta real
  }

  verDetalleCert(id?: number) {
    if (!id) return;
    this.router.navigate(['/certificados', id]); // ejemplo
  }

  verDetalleReserva(id?: number) {
    if (!id) return;
    this.router.navigate(['/reservas', id]); // ejemplo
  }
}
