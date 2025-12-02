// Interfaces para juntas de vecinos basadas en los schemas del backend

export interface JuntaCreateRequest {
  nombre: string;
  rut: string;
  email: string;
  telefono: string;
  direccion: string;
  id_comuna: number;
  fecha_constitucion?: string; // ISO date string
  descripcion?: string;
  activa: boolean;
  logo?: string; // base64 string
}

export interface JuntaCreateResponse {
  id_junta: number;
  nombre: string;
  rut: string;
  email: string;
  telefono: string;
  direccion: string;
  id_comuna: number;
  comuna_nombre: string;
  region_nombre: string;
  fecha_constitucion?: string;
  descripcion?: string;
  activa: boolean;
  logo?: string;
  created_at: string;
  mensaje: string;
}

export interface JuntaResponse {
  id_junta: number;
  nombre: string;
  rut: string;
  email?: string;
  telefono?: string;
  direccion?: string;
  id_comuna: number;
  comuna_nombre: string;
  region_nombre: string;
  fecha_constitucion?: string;
  descripcion?: string;
  activa: boolean;
  logo?: string;
  firma_presidente?: string; // Firma en base64 si existe
  timbre?: string; // Timbre en base64 si existe
  created_at: string;
}

export interface JuntaListResponse {
  id_junta: number;
  nombre: string;
  rut: string;
  email?: string;
  direccion?: string;
  comuna_nombre: string;
  region_nombre: string;
  activa: boolean;
  created_at: string;
}

export interface JuntasList {
  juntas: JuntaListResponse[];
  total: number;
  activas: number;
  inactivas: number;
}

export interface RegionResponse {
  id_region: number;
  nombre: string;
  codigo?: string;
}

export interface ComunaResponse {
  id_comuna: number;
  nombre: string;
  id_region: number;
}

export interface RegionsList {
  regiones: RegionResponse[];
  total: number;
}

export interface ComunasList {
  comunas: ComunaResponse[];
  total: number;
}

export interface JuntaUpdateRequest {
  telefono?: string;
  email?: string;
  descripcion?: string;
  logo?: string; // base64 string
}

export interface JuntaUpdateResponse {
  id_junta: number;
  telefono?: string;
  email?: string;
  descripcion?: string;
  logo?: string;
  mensaje: string;
}

export interface JuntaFirmaTimbreUpdateRequest {
  firma_presidente?: string; // base64 string
  timbre?: string; // base64 string
}

export interface JuntaFirmaTimbreUpdateResponse {
  id_junta: number;
  firma_presidente?: string;
  timbre?: string;
  mensaje: string;
}

export interface ApiError {
  error: string;
  detalle?: string;
  codigo?: string;
}
