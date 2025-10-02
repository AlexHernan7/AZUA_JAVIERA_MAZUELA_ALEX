// Interfaces para reservas de espacios comunitarios

export interface ReservaCreateRequest {
  id_espacio: number;
  id_junta: number;
  id_vecino: number;
  fecha: string; // formato YYYY-MM-DD
  hora_inicio: string; // formato HH:MM
  hora_termino: string; // formato HH:MM
  motivo: string;
  asistentes?: number;
  observaciones?: string;
  acepta_reglamento: boolean;
}

export interface ReservaUpdateRequest {
  fecha?: string;
  hora_inicio?: string;
  hora_termino?: string;
  motivo?: string;
  asistentes?: number;
  estado?: 'pendiente' | 'confirmada' | 'cancelada';
}

export interface ReservaResponse {
  id_reserva: number;
  id_espacio: number;
  id_vecino: number;
  id_junta: number;
  fecha: string;
  hora_inicio: string;
  hora_termino: string;
  motivo: string;
  asistentes?: number;
  estado: 'pendiente' | 'confirmada' | 'cancelada';
  valor_total: number;
  created_at: string;
  updated_at: string;
  // Información adicional del espacio
  espacio?: {
    id_espacio: number;
    nombre: string;
    tipo: string;
    capacidad: number;
    valor: number;
  };
  // Información adicional del vecino
  vecino?: {
    id_vecino: number;
    nombres: string;
    apellido_paterno: string;
    apellido_materno: string;
    rut: string;
  };
}

export interface ReservaListResponse {
  reservas: ReservaResponse[];
  total: number;
  pagina: number;
  por_pagina: number;
}

export interface DisponibilidadRequest {
  id_espacio: number;
  fecha: string; // formato YYYY-MM-DD
  hora_inicio: string; // formato HH:MM
  hora_termino: string; // formato HH:MM
}

export interface DisponibilidadResponse {
  disponible: boolean;
  conflicto_con?: {
    id_reserva: number;
    hora_inicio: string;
    hora_termino: string;
    motivo: string;
  };
  mensaje: string;
}

export interface ApiError {
  detail: string;
}
