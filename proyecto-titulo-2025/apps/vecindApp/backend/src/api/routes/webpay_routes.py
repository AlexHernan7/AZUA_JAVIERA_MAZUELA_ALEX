"""
Rutas para Webpay Plus.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_db_session
from src.services.payment_service import PaymentService
from src.services.webpay_service import WebpayService
from src.services.certificado_service import CertificadoService
from src.database.models.payment_intent import PaymentIntentStatus

router = APIRouter(prefix="/payments/webpay", tags=["Webpay"])
logger = logging.getLogger(__name__)


@router.get(
    "/return",
    summary="Endpoint de retorno de Webpay (GET)",
    description="Endpoint donde Webpay redirige después del pago"
)
async def webpay_return_get(
    token_ws: str,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Maneja el retorno desde Webpay después del pago (GET).
    """
    return await _process_webpay_return(token_ws, db)


@router.post(
    "/return",
    summary="Endpoint de retorno de Webpay (POST)",
    description="Endpoint donde Webpay redirige después del pago"
)
async def webpay_return_post(
    request: Request,
    token_ws: str = Form(...),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Maneja el retorno desde Webpay después del pago (POST).
    """
    return await _process_webpay_return(token_ws, db)


async def _process_webpay_return(
    token_ws: str,
    db: AsyncSession
):
    """
    Maneja el retorno desde Webpay después del pago.
    
    Args:
        token_ws: Token de la transacción de Webpay
        db: Sesión de base de datos
    """
    try:
        logger.info(f"🔄 Procesando retorno de Webpay con token: {token_ws[:20]}...")
        
        webpay_service = WebpayService()
        payment_service = PaymentService(db)
        
        # 1. Confirmar la transacción en Webpay
        transaction_data = webpay_service.confirm_transaction(token_ws)
        
        logger.info(f"📊 Datos de transacción: {webpay_service.format_transaction_for_log(transaction_data)}")
        
        # 2. Obtener el buy_order para encontrar el PaymentIntent
        buy_order = webpay_service.get_buy_order(transaction_data)
        
        # Extraer payment_intent_id del buy_order
        # Formato: pi{payment_intent_id}_{timestamp}
        try:
            parts = buy_order.split("_")
            pi_part = parts[0]  # "pi123"
            payment_intent_id = int(pi_part[2:])  # Remover "pi" y convertir a int
        except (IndexError, ValueError):
            logger.error(f"❌ Buy order inválido: {buy_order}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Buy order inválido"
            )
        
        # 3. Obtener la intención de pago
        payment_intent_response = await payment_service.get_payment_intent(payment_intent_id)
        if not payment_intent_response:
            logger.error(f"❌ PaymentIntent no encontrado: {payment_intent_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Intención de pago no encontrada"
            )
        
        # 4. Determinar el estado según la respuesta de Webpay
        if webpay_service.is_transaction_approved(transaction_data):
            new_status = PaymentIntentStatus.COMPLETED
            logger.info(f"✅ Transacción aprobada para PaymentIntent {payment_intent_id}")
        else:
            new_status = PaymentIntentStatus.FAILED
            logger.warning(f"❌ Transacción rechazada para PaymentIntent {payment_intent_id}")
        
        # 5. Actualizar el estado del PaymentIntent
        await payment_service.update_payment_intent_status(
            payment_intent_id=payment_intent_id,
            new_status=new_status,
            external_id=webpay_service.get_authorization_code(transaction_data),
            response_payload=transaction_data
        )
        
        # 6. Procesar lógica de negocio si el pago fue exitoso
        if new_status == PaymentIntentStatus.COMPLETED:
            # Liberar certificado
            certificado_service = CertificadoService(db)
            certificado_pedido_id = payment_intent_response.entity_id
            await certificado_service.liberar_certificado_por_pago(certificado_pedido_id)
            
            logger.info(f"✅ Transacción aprobada para PaymentIntent {payment_intent_id}. Certificado liberado.")
            return RedirectResponse(url=webpay_service.webpay_settings.final_url, status_code=status.HTTP_302_FOUND)
        else:
            # Pago rechazado o pendiente
            logger.warning(f"❌ Transacción rechazada para PaymentIntent {payment_intent_id}")
            return RedirectResponse(url=webpay_service.webpay_settings.final_url, status_code=status.HTTP_302_FOUND)
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"💥 Error procesando retorno de Webpay: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Error en el retorno de Webpay", "detalle": str(e)}
        )
    except Exception as e:
        logger.error(f"💥 Error inesperado procesando retorno de Webpay: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error interno del servidor", "detalle": str(e)}
        )


@router.get(
    "/status/{token}",
    summary="Consultar estado de transacción Webpay",
    description="Consulta el estado de una transacción usando el token"
)
async def get_webpay_status(
    token: str,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Consulta el estado de una transacción de Webpay.
    
    Args:
        token: Token de la transacción
        db: Sesión de base de datos
    """
    try:
        webpay_service = WebpayService()
        
        transaction_data = webpay_service.get_transaction_status(token)
        
        return {
            "status": "success",
            "transaction_data": transaction_data,
            "is_approved": webpay_service.is_transaction_approved(transaction_data),
            "formatted_info": webpay_service.format_transaction_for_log(transaction_data)
        }
        
    except Exception as e:
        logger.error(f"💥 Error consultando estado Webpay: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error consultando estado: {str(e)}"
        )
