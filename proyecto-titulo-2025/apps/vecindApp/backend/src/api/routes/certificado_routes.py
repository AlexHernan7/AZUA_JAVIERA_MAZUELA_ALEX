"""
Rutas para certificados de residencia - VERSIÓN LIMPIA.
"""

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_db_session
from src.services.certificado_service import CertificadoService
from src.schemas.certificado_schemas import (
    CertificadoPedidoCreate,
    CertificadoPedidoResponse,
    CertificadoConfirmacionData,
    CertificadoResponse,
    ErrorResponse
)
from src.api.routes.user_routes import verify_user_token

# Crear router para certificados
router = APIRouter(prefix="/certificados", tags=["Certificados"])

logger = logging.getLogger(__name__)


@router.get(
    "/confirmacion-datos",
    response_model=CertificadoConfirmacionData,
    summary="Obtener datos para confirmación",
    description="Obtiene los datos del vecino para confirmar antes de solicitar certificado",
    responses={
        200: {"description": "Datos del vecino obtenidos exitosamente"},
        401: {"model": ErrorResponse, "description": "Token inválido o expirado"},
        404: {"model": ErrorResponse, "description": "Vecino no encontrado"},
    }
)
async def get_datos_confirmacion(
    user_id: int = Depends(verify_user_token),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Obtiene los datos del vecino autenticado para mostrar en la confirmación.
    """
    try:
        service = CertificadoService(db)
        datos = await service.get_datos_confirmacion(user_id)
        
        logger.info(f"📋 Datos de confirmación obtenidos para usuario {user_id}")
        return datos
        
    except ValueError as e:
        logger.warning(f"❌ Error obteniendo datos de confirmación: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Datos no encontrados", "detalle": str(e)}
        )
    except Exception as e:
        logger.error(f"💥 Error inesperado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error interno del servidor", "detalle": str(e)}
        )


@router.post(
    "/webpay-payment",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Crear certificado con Webpay Plus",
    description="Crea una solicitud de certificado con pago Webpay Plus y retorna token para redirección"
)
async def crear_certificado_webpay_payment(
    request: CertificadoPedidoCreate,
    user_id: int = Depends(verify_user_token),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Crea un certificado pendiente de pago con Webpay Plus.
    
    Returns:
        Dict con pedido, payment_intent, payment_url y webpay_token
    """
    try:
        service = CertificadoService(db)
        
        # Crear certificado con pago Webpay
        pedido, payment_intent, webpay_url, webpay_token = await service.crear_certificado_con_webpay(
            user_id=user_id,
            motivo_solicitud=request.motivo_solicitud
        )
        
        logger.info(f"📝💳 Certificado con Webpay creado: pedido={pedido.id_pedido}, payment={payment_intent.id_payment_intent}")
        
        return {
            "pedido": pedido,
            "payment_intent": payment_intent,
            "message": "Solicitud creada. Complete el pago para generar el certificado.",
            "payment_url": webpay_url,
            "webpay_token": webpay_token,
            "provider": "webpay"
        }
        
    except ValueError as e:
        logger.warning(f"❌ Error creando certificado con Webpay: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Error en la solicitud", "detalle": str(e)}
        )
    except Exception as e:
        logger.error(f"💥 Error inesperado en webpay-payment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error interno del servidor", "detalle": str(e)}
        )


@router.get(
    "/mis-certificados",
    response_model=List[CertificadoResponse],
    summary="Obtener mis certificados",
    description="Obtiene todos los certificados del usuario autenticado",
    responses={
        200: {"description": "Lista de certificados obtenida exitosamente"},
        401: {"model": ErrorResponse, "description": "Token inválido o expirado"},
    }
)
async def get_mis_certificados(
    user_id: int = Depends(verify_user_token),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Obtiene todos los certificados del usuario autenticado.
    """
    try:
        service = CertificadoService(db)
        certificados = await service.obtener_certificados_usuario(user_id)
        
        logger.info(f"📋 {len(certificados)} certificados obtenidos para usuario {user_id}")
        return certificados
        
    except Exception as e:
        logger.error(f"💥 Error obteniendo certificados: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error interno del servidor", "detalle": str(e)}
        )


@router.get(
    "/{certificado_id}/descargar",
    summary="Descargar certificado PDF",
    description="Descarga el certificado en formato PDF",
    responses={
        200: {"description": "PDF del certificado", "content": {"application/pdf": {}}},
        401: {"model": ErrorResponse, "description": "Token inválido o expirado"},
        404: {"model": ErrorResponse, "description": "Certificado no encontrado"},
        403: {"model": ErrorResponse, "description": "Sin permisos para descargar este certificado"},
    }
)
async def descargar_certificado(
    certificado_id: int,
    user_id: int = Depends(verify_user_token),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Descarga un certificado en formato PDF.
    Solo el propietario puede descargar su certificado.
    """
    try:
        service = CertificadoService(db)
        pdf_data, filename = await service.descargar_certificado(certificado_id, user_id)
        
        logger.info(f"📄 Certificado {certificado_id} descargado por usuario {user_id}")
        
        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": "application/pdf"
            }
        )
        
    except ValueError as e:
        logger.warning(f"❌ Error descargando certificado: {str(e)}")
        if "no encontrado" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Certificado no encontrado", "detalle": str(e)}
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"error": "Sin permisos", "detalle": str(e)}
            )
    except Exception as e:
        logger.error(f"💥 Error inesperado descargando certificado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error interno del servidor", "detalle": str(e)}
        )
