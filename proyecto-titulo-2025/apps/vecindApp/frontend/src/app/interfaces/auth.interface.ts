// Interfaces para autenticación basadas en los schemas del backend

export interface LoginRequest {
  email: string;
  password: string;
}

export interface VecinoLoginData {
  nombres: string;
  apellido_paterno: string;
  apellido_materno: string;
  rut: string;
  fecha_nacimiento?: string;
  telefono?: string;
  direccion?: string;
  foto_perfil?: string;
  comuna?: string;
  region?: string;
  junta?: string;
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

// Interfaces para registro de usuario
export interface RegisterRequest {
  email: string;
  password: string;
  rut: string;
  nombres: string;
  apellido_paterno: string;
  apellido_materno: string;
  fecha_nacimiento: string; // formato YYYY-MM-DD
  telefono: string;
  direccion: string;
  foto_perfil?: string; // base64 opcional
  id_region: number;
  id_comuna: number;
  id_junta: number;
}

export interface VecinoResponse {
  id_vecino: number;
  rut: string;
  nombres: string;
  apellido_paterno: string;
  apellido_materno: string;
  email: string;
  telefono?: string;
  direccion?: string;
  fecha_nacimiento: string;
  foto_perfil?: string;
}

export interface RegisterResponse {
  id_usuario: number;
  vecino: VecinoResponse;
}
