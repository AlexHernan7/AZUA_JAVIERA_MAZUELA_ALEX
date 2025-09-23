// Interfaces para el sistema de pagos
export interface PaymentIntentResponse {
  id_payment_intent: number;
  entity_type: string;
  entity_id: number;
  amount: number;
  currency: string;
  description: string;
  status: string;
  created_at: string;
  updated_at: string;
  expires_at: string;
  
  // URLs de MercadoPago
  mp_preference_id?: string;
  mp_init_point?: string;
  mp_sandbox_init_point?: string;
  
  // Estado calculado
  is_expired: boolean;
  is_active: boolean;
  can_retry: boolean;
  
  extra_data?: any;
}

export interface PaymentTransactionResponse {
  id_payment_transaction: number;
  id_payment_intent: number;
  provider: string;
  external_id?: string;
  amount: number;
  currency: string;
  status: string;
  payment_method_id?: string;
  payment_type_id?: string;
  installments?: number;
  created_at: string;
  updated_at: string;
  processed_at?: string;
  payer_email?: string;
}

export interface PaymentStatusResponse {
  payment_intent: PaymentIntentResponse;
  transactions: PaymentTransactionResponse[];
  latest_transaction?: PaymentTransactionResponse;
}

export interface CertificadoConPagoResponse {
  pedido: any; // CertificadoPedidoResponse
  payment_intent: PaymentIntentResponse;
  message: string;
  payment_url: string;
  webpay_token?: string; // Token para Webpay Plus
  provider?: string; // 'mercadopago' o 'webpay'
}

export interface PaymentErrorResponse {
  error: string;
  detail: string;
  payment_intent_id?: number;
  provider_error?: any;
}

export type PaymentStatus = 'pending' | 'processing' | 'completed' | 'failed' | 'expired' | 'cancelled';
export type TransactionStatus = 'created' | 'pending' | 'in_process' | 'approved' | 'rejected' | 'cancelled' | 'refunded' | 'charged_back';
