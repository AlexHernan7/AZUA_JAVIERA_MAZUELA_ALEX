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
  creado_por: number;
  id_estado: number;
  inicio: string; // Fecha y hora de inicio en formato ISO
  fin: string; // Fecha y hora de fin en formato ISO
  estado: string; // Nombre del estado
  observaciones?: string;
  created_at: string;
  valor_reserva: number;
  // Información adicional del espacio
  espacio_nombre?: string;
  espacio_tipo?: string;
  espacio_capacidad?: number;
  espacio_valor?: number;
  // Información adicional del vecino
  vecino_nombre?: string;
  vecino_email?: string;
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

export interface ReservaConPagoRequest {
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

export interface ReservaWebpayResponse {
  reserva: ReservaResponse;
  payment_intent: {
    id_payment_intent: number;
    amount: number;
    status: string;
    description: string;
  };
  message: string;
  payment_url: string;
  webpay_token: string;
  provider: string;
}

export interface ApiError {
  detail: string;
}
