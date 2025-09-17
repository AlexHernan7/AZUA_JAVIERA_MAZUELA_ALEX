import { Component } from '@angular/core';
import { CommonModule } from '@angular/common'; 
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule],    
  templateUrl: './home.component.html',
  styleUrl: './home.component.css',
})
export class HomeComponent {
constructor(private router: Router, public authService: AuthService) {}


  goToRegister() {
    this.router.navigate(['/register']);}
}
