import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';
import { NxWelcomeComponent } from './nx-welcome.component';
import { LoginComponent } from './components/login/login.component'
import { MenuComponent } from './components/menu/menu.component'
import { HomeComponent } from './components/home/home.component';
import { RegisterComponent } from './components/register/register.component';

@Component({
  standalone: true,
  imports: [ RouterModule,MenuComponent,LoginComponent, HomeComponent, RegisterComponent],
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss',
})
export class AppComponent {
  title = 'frontend';




  
}