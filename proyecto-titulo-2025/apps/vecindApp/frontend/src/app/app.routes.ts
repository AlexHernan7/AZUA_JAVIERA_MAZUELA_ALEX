// src/app/app.routes.ts
import { Routes } from '@angular/router';
import { HomeComponent } from './components/home/home.component';
import { LoginComponent } from './components/login/login.component';
import { AppComponent } from './app.component';
import { RegisterComponent } from './components/register/register.component';
import { ProfileComponent } from './components/profile/profile.component';
import { NewsComponent } from './components/news/news.component';
import { authGuard } from './services/auth.service';
import { DirectivaRegisterComponent } from './components/directiva-register/directiva-register.component';
import { JuntaCreateComponent } from './components/junta-create/junta-create.component';
import { CertificadoCreateComponent} from './components/certificado-create/certificado-create.component';
import { JuntaProfileComponent } from './components/junta-profile/junta-profile.component';
import { PaymentSuccessComponent } from './components/payment-success/payment-success.component';
import { PaymentFailureComponent } from './components/payment-failure/payment-failure.component';
import { PaymentPendingComponent } from './components/payment-pending/payment-pending.component';
import { ReservasComponent } from './components/reservas/reservas.component';


export const appRoutes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  { path: 'directiva/nuevo', component: DirectivaRegisterComponent },//falta agregar can active, para que solo el admin pueda ingresar a este 
  { path: 'juntas/nueva', component: JuntaCreateComponent },//falta agregar can active, para que solo el admin pueda ingresar a este 
  { path: 'certificados/residencia/crear', component: CertificadoCreateComponent },
  { path: 'juntas/:id', loadComponent: () => import('./components/junta-profile/junta-profile.component').then(m => m.JuntaProfileComponent)},
  { path: 'profile', component: ProfileComponent, canActivate: [authGuard]},
  { path: 'news', component: NewsComponent },
  { path: 'reservas', component: ReservasComponent },


  // Rutas de pago
  { path: 'payment/success', component: PaymentSuccessComponent },
  { path: 'payment/failure', component: PaymentFailureComponent },
  { path: 'payment/pending', component: PaymentPendingComponent },
  { path: '**', redirectTo: '' }, // opcional
];
