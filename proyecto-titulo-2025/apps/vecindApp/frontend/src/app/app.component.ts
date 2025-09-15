import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';
import { NxWelcomeComponent } from './nx-welcome.component';
import { LoginComponent } from './components/login/login.component'
import { MenuComponent } from './components/menu/menu.component'
import { HomeComponent } from './components/home/home.component';
import { RegisterComponent } from './components/register/register.component';
import { ProfileComponent } from './components/profile/profile.component';

@Component({
  standalone: true,
  imports: [ RouterModule,MenuComponent,LoginComponent, HomeComponent, RegisterComponent, ProfileComponent],
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss',
})
export class AppComponent {
  title = 'frontend';




  
}