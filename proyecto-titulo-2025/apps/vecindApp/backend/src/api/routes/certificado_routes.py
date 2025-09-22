"""
Rutas para certificados de residencia.
"""

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database.session import get_db_session
from src.services.certificado_service import CertificadoService
from src.database.models.certificado import Certificado
from src.database.models.certificado_pedido import CertificadoPedido
from src.database.models.vecino import Vecino
from src.schemas.certificado_schemas import (
    CertificadoPedidoCreate,
    CertificadoPedidoResponse,
    CertificadoConfirmacionData,
    CertificadoGenerateRequest,
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
    "/solicitar",
    response_model=CertificadoPedidoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Solicitar certificado de residencia",
    description="Crea una nueva solicitud de certificado de residencia",
    responses={
        201: {"description": "Solicitud creada exitosamente"},
        400: {"model": ErrorResponse, "description": "Ya existe solicitud pendiente"},
        401: {"model": ErrorResponse, "description": "Token inválido o expirado"},
        404: {"model": ErrorResponse, "description": "Vecino no encontrado"},
    }
)
async def solicitar_certificado(
    request: CertificadoPedidoCreate,
    user_id: int = Depends(verify_user_token),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Crea una nueva solicitud de certificado de residencia.
    """
    try:
        service = CertificadoService(db)
        pedido = await service.crear_pedido_certificado(user_id)
        
        logger.info(f"📝 Solicitud de certificado creada: ID {pedido.id_pedido}")
        return pedido
        
    except ValueError as e:
        logger.warning(f"❌ Error creando solicitud: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Error en la solicitud", "detalle": str(e)}
        )
    except Exception as e:
        logger.error(f"💥 Error inesperado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error interno del servidor", "detalle": str(e)}
        )


@router.post(
    "/generar",
    response_model=CertificadoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generar certificado de residencia",
    description="Genera el certificado PDF después de confirmar los datos",
    responses={
        201: {"description": "Certificado generado exitosamente"},
        400: {"model": ErrorResponse, "description": "No hay solicitud pendiente o datos inválidos"},
        401: {"model": ErrorResponse, "description": "Token inválido o expirado"},
        409: {"model": ErrorResponse, "description": "Certificado ya existe"},
    }
)
async def generar_certificado(
    request: CertificadoGenerateRequest,
    user_id: int = Depends(verify_user_token),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Genera el certificado de residencia en PDF después de confirmar los datos.
    """
    try:
        if not request.confirmar_datos:
            raise ValueError("Debe confirmar los datos para generar el certificado")
        
        service = CertificadoService(db)
        certificado = await service.generar_certificado(
            user_id, 
            request.direccion_actualizada
        )
        
        logger.info(f"📄 Certificado generado: {certificado.numero}")
        return certificado
        
    except ValueError as e:
        logger.warning(f"❌ Error generando certificado: {str(e)}")
        status_code = status.HTTP_409_CONFLICT if "ya existe" in str(e).lower() else status.HTTP_400_BAD_REQUEST
        raise HTTPException(
            status_code=status_code,
            detail={"error": "Error generando certificado", "detalle": str(e)}
        )
    except Exception as e:
        logger.error(f"💥 Error inesperado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error interno del servidor", "detalle": str(e)}
        )


@router.get(
    "/mis-certificados",
    response_model=List[CertificadoResponse],
    summary="Obtener mis certificados",
    description="Obtiene todos los certificados emitidos para el usuario autenticado",
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
    Obtiene todos los certificados emitidos para el usuario autenticado.
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
        403: {"model": ErrorResponse, "description": "No autorizado para descargar este certificado"},
    }
)
async def descargar_certificado_pdf(
    certificado_id: int,
    user_id: int = Depends(verify_user_token),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Descarga el certificado en formato PDF.
    """
    try:
        # Verificar que el certificado existe y pertenece al usuario
        result = await db.execute(
            select(Certificado)
            .join(CertificadoPedido)
            .join(Vecino)
            .where(
                Certificado.id_certificado == certificado_id,
                Vecino.id_usuario == user_id
            )
        )
        certificado = result.scalar_one_or_none()
        
        if not certificado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Certificado no encontrado", "detalle": "El certificado no existe o no tienes permisos para acceder a él"}
            )
        
        if not certificado.pdf_url:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "PDF no disponible", "detalle": "El PDF del certificado no está disponible"}
            )
        
        # Extraer el contenido base64 del data URL
        if certificado.pdf_url.startswith("data:application/pdf;base64,"):
            pdf_base64 = certificado.pdf_url.replace("data:application/pdf;base64,", "")
            
            # Decodificar base64
            import base64
            pdf_bytes = base64.b64decode(pdf_base64)
            
            # Crear nombre del archivo
            filename = f"certificado_residencia_{certificado.numero}.pdf"
            
            # Retornar PDF como respuesta
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}",
                    "Content-Length": str(len(pdf_bytes))
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"error": "Formato de PDF inválido", "detalle": "El formato del PDF almacenado no es válido"}
            )
        
    except HTTPException:
        # Re-lanzar HTTPExceptions
        raise
    except Exception as e:
        logger.error(f"💥 Error descargando certificado PDF: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error interno del servidor", "detalle": str(e)}
        )
