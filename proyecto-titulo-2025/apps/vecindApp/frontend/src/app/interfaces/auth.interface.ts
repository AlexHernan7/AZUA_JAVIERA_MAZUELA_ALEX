// Interfaces para autenticación basadas en los schemas del backend

export interface LoginRequest {
  email: string;
  password: string;
}

export interface VecinoLoginData {
  id_vecino: number;
  nombres: string;
  apellido_paterno: string;
  apellido_materno: string;
  telefono?: string;
  direccion?: string;
  foto_perfil?: string;
}

export interface UserLoginData {
  id_usuario: number;
  email: string;
  nombres: string;
  apellido_paterno: string;
  apellido_materno: string;
  activo: boolean;
  vecino?: VecinoLoginData;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: UserLoginData;
}

export interface ApiError {
  error: string;
  detalle: string;
  codigo?: string;
}
