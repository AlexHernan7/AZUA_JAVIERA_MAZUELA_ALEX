// Interfaces para certificados basadas en los schemas del backend

export interface CertificadoPedidoCreate {
  motivo_solicitud: string;
}

export interface CertificadoPedidoResponse {
  id_pedido: number;
  estado: string;
  created_at: string;
  vecino_nombres: string;
  vecino_apellidos: string;
  vecino_rut: string;
  vecino_direccion?: string;
  comuna?: string;
  region?: string;
  junta?: string;
  motivo_solicitud?: string;
}

export interface CertificadoConfirmacionData {
  nombres: string;
  apellido_paterno: string;
  apellido_materno: string;
  rut: string;
  direccion?: string;
  comuna?: string;
  region?: string;
  junta?: string;
}

export interface CertificadoGenerateRequest {
  confirmar_datos: boolean;
  motivo_solicitud: string;
  direccion_actualizada?: string;
}

export interface CertificadoResponse {
  id_certificado: number;
  numero: string;
  fecha_emision: string;
  direccion?: string;
  comuna?: string;
  region?: string;
  pdf_url?: string;
}

export interface CertificadoApiError {
  error: string;
  detalle?: string;
}

// Estados del certificado
export type CertificadoEstado = 'iniciado' | 'pagado' | 'emitido' | 'rechazado';

// Catálogo de motivos para el frontend
export interface MotivoGrupo {
  grupo: string;
  items: string[];
}
