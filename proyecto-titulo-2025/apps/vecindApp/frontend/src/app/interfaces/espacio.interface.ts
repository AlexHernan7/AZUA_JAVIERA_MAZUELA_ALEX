// Interfaces para espacios comunitarios

export interface EspacioCreateRequest {
  nombre: string;
  id_tipo: number;
  capacidad: number;
  valor: number;
  foto?: string;
  permitido?: string[];
  no_permitido?: string[];
  max_horas: number;
  activo: boolean;
  id_junta: number;
}

export interface EspacioResponse {
  id_espacio: number;
  id_junta: number;
  nombre: string;
  tipo: string;
  capacidad: number;
  valor: number;
  foto?: string;
  permitido?: string[];
  no_permitido?: string[];
  max_horas: number;
  activo: boolean;
}

export interface EspacioListResponse {
  espacios: EspacioResponse[];
  total: number;
  pagina: number;
  por_pagina: number;
}

export interface ApiError {
  detail: string;
}
