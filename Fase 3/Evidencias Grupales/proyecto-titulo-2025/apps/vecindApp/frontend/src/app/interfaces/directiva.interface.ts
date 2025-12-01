// Interfaces para directivos basadas en los schemas del backend

export interface DirectivaRegistroRequest {
  // Datos personales
  rut: string;
  nombres: string;
  apellido_paterno: string;
  apellido_materno?: string;
  telefono: string;
  email: string;
  
  // Datos del cargo
  cargo: string;
  fecha_inicio_cargo: string; // formato YYYY-MM-DD
  fecha_termino_cargo?: string; // formato YYYY-MM-DD
  
  // Datos de la junta
  id_junta: number;
  
  // Credenciales
  password: string;
  confirm_password: string;
  
  // Foto de perfil opcional (base64)
  foto_perfil?: string;
}

export interface DirectivaResponse {
  id_directiva: number;
  rut: string;
  nombres: string;
  apellido_paterno: string;
  apellido_materno?: string;
  telefono: string;
  email: string;
  cargo: string;
  fecha_inicio_cargo: string;
  fecha_termino_cargo?: string;
  foto_perfil?: string;
}

export interface DirectivaRegistroResponse {
  id_usuario: number;
  directiva: DirectivaResponse;
}

export interface DirectivaApiError {
  error: string;
  detalle: string;
  codigo?: string;
}

// Mapeo del tipo del componente al tipo de la API
export interface DirectivaFormData {
  foto_perfil?: string;
  apellido_paterno: string;
  apellido_materno?: string;
  rut: string;
  cargo: string;
  nombres: string;
  email: string;
  telefono: string;
  fecha_inicio?: string;
  fecha_termino?: string;
  password: string;
}

// Opciones de cargo disponibles
export const CARGOS_DIRECTIVA = [
  'presidente',
  'vicepresidente', 
  'secretario',
  'tesorero',
  'director',
  'vocal'
] as const;

export type CargoDirectiva = typeof CARGOS_DIRECTIVA[number];
