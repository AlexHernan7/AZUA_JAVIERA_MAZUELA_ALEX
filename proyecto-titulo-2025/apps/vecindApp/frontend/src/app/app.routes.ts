// src/app/app.routes.ts
import { Routes } from '@angular/router';
import { HomeComponent } from './components/home/home.component';
import { LoginComponent } from './components/login/login.component';
import { AppComponent } from './app.component';
import { RegisterComponent } from './components/register/register.component';
import { ProfileComponent } from './components/profile/profile.component';
import { NewsComponent } from './components/news/news.component';
import { authGuard, directivaGuard, adminGuard, guestGuard } from './services/auth.service';
import { DirectivaRegisterComponent } from './components/directiva-register/directiva-register.component';
import { JuntaCreateComponent } from './components/junta-create/junta-create.component';
import { CertificadoCreateComponent} from './components/certificado-create/certificado-create.component';
import { PaymentSuccessComponent } from './components/payment-success/payment-success.component';
import { PaymentFailureComponent } from './components/payment-failure/payment-failure.component';
import { PaymentPendingComponent } from './components/payment-pending/payment-pending.component';
import { ReservasComponent } from './components/reservas/reservas.component';
import { QuienesSomosComponent } from './components/quienes-somos/quienes-somos.component';
import { CreateEspaciosComponent } from './components/create-espacios/create-espacios.component';
import { ReportesComponent } from './components/reportes/reportes.component';
import { TramitesComponent } from './components/tramites/tramites.component';
import { ForgotPasswordComponent } from './components/forgot-password/forgot-password.component';
import { UserManagementComponent } from './components/users-management/user-management.component';



export const appRoutes: Routes = [
  // Rutas públicas
  { path: '', component: HomeComponent },
  { path: 'quienes-somos', component: QuienesSomosComponent },
  { path: 'news', component: NewsComponent },
  { path: 'juntas/:id', loadComponent: () => import('./components/junta-profile/junta-profile.component').then(m => m.JuntaProfileComponent)},
  
  // Rutas de autenticación (solo para usuarios no autenticados)
  { path: 'login', component: LoginComponent, canActivate: [guestGuard] },
  { path: 'register', component: RegisterComponent, canActivate: [guestGuard] },
  { path: 'forgot-password', component: ForgotPasswordComponent, canActivate: [guestGuard] },
  
  // Rutas que requieren autenticación
  { path: 'profile', component: ProfileComponent, canActivate: [authGuard]},
  { path: 'certificados/residencia/crear', component: CertificadoCreateComponent, canActivate: [authGuard] },
  { path: 'reservas', component: ReservasComponent, canActivate: [authGuard] },
  { path: 'espacios/crear', component: CreateEspaciosComponent, canActivate: [authGuard] },
  { path: 'reportes', component: ReportesComponent, canActivate: [authGuard] },
  { path: 'tramites', component: TramitesComponent, canActivate: [authGuard] },
  
  // Rutas que requieren rol de directiva o admin
  { path: 'list_user', loadComponent: () => import('./components/list_user/list_user.component').then(m => m.ListUserComponent), canActivate: [directivaGuard]},
  { path: 'users-management', component: UserManagementComponent, canActivate: [directivaGuard] },
  
  // Rutas que requieren rol de admin exclusivamente
  { path: 'directiva/nuevo', component: DirectivaRegisterComponent, canActivate: [adminGuard] },
  { path: 'juntas/nueva', component: JuntaCreateComponent, canActivate: [adminGuard] },
  
  // Rutas de pago (requieren autenticación)
  { path: 'payment/success', component: PaymentSuccessComponent, canActivate: [authGuard] },
  { path: 'payment/failure', component: PaymentFailureComponent, canActivate: [authGuard] },
  { path: 'payment/pending', component: PaymentPendingComponent, canActivate: [authGuard] },
  
  // Ruta catch-all (debe ir al final)
  { path: '**', redirectTo: '' },
];
