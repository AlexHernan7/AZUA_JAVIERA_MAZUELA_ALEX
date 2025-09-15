import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.css'],
})
export class ProfileComponent {
  // demo data (conecta esto a tu servicio cuando tengas backend)
  user = {
    nombreCompleto: 'Javiera Azúa',
    subtitulo: 'Vecina registrada',
    rut: '18.582.719-4',
    fechaNac: '10/02/1985',
    email: 'javiera.azua@example.com',
    telefono: '+56 9 1234 5678',
    direccion: 'Calle Falsa 123, Dpto 2B',
    comuna: 'Maipú',
    region: 'Región Metropolitana',
    avatarUrl: 'images/avatar-placeholder2.svg',        // 400×400 sugerido
    coverUrl: 'images/hero_vecindapp.png',              // fondo ancho
  };

  editarPerfil() {
    // TODO: navega a tu formulario de edición o abre modal
    console.log('Editar perfil');
  }
}