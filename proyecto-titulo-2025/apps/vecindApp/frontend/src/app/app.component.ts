import { Component } from '@angular/core';
import { RouterModule, RouterOutlet } from '@angular/router';
import { NxWelcomeComponent } from './nx-welcome.component';
import { LoginComponent } from './components/login/login.component'
import { MenuComponent } from './components/menu/menu.component'
import { HomeComponent } from './components/home/home.component';
import { RegisterComponent } from './components/register/register.component';
import { ProfileComponent } from './components/profile/profile.component';
import { AsyncPipe, NgIf } from '@angular/common';
import { MenuAuthComponent } from './components/menu-auth/menu-auth.component';
import { AuthService } from './services/auth.service';

@Component({
  standalone: true,
  imports: [ RouterModule,RouterOutlet, NgIf, AsyncPipe,MenuComponent,LoginComponent, HomeComponent, RegisterComponent, ProfileComponent, MenuAuthComponent],
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss',
})
export class AppComponent {
  title = 'frontend';

  
  constructor(public auth: AuthService) {}


  
}