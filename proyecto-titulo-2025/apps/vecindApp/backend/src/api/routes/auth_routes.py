"""
Rutas de autenticación para VecindApp.

Contiene endpoints para registro, login, etc.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from src.database.session import get_db_session
from src.services.auth_service import AuthService
from src.schemas.auth_schemas import (
    UsuarioRegistroRequest, 
    UsuarioRegistroResponse, 
    VecinoResponse,
    ErrorResponse
)
from src.schemas.user_schemas import JuntasList, ComunasList

# Crear router para rutas de autenticación
router = APIRouter(prefix="/auth", tags=["Autenticación"])

logger = logging.getLogger(__name__)


@router.post(
    "/register",
    response_model=UsuarioRegistroResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo usuario",
    description="Registra un nuevo usuario y crea su perfil de vecino",
    responses={
        201: {"description": "Usuario registrado exitosamente"},
        400: {"model": ErrorResponse, "description": "Error de validación"},
        409: {"model": ErrorResponse, "description": "Email ya registrado"}
    }
)
async def register_user(
    user_data: UsuarioRegistroRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Registra un nuevo usuario en el sistema.
    
    Este endpoint:
    1. Valida los datos del usuario
    2. Verifica que la junta y comuna existan y coincidan
    3. Crea el usuario con contraseña hasheada
    4. Crea el perfil de vecino asociado
    5. Asigna el rol de 'vecino' por defecto
    
    Args:
        user_data: Datos del usuario a registrar
        db: Sesión de base de datos
        
    Returns:
        Datos del usuario y vecino creados
        
    Raises:
        HTTPException: Si hay errores de validación o el email ya existe
    """
    try:
        logger.info(f"🔄 Iniciando registro de usuario: {user_data.email}")
        
        # Crear servicio de autenticación
        auth_service = AuthService(db)
        logger.info("✅ Servicio de autenticación creado")
        
        # Registrar usuario
        logger.info(f"🔄 Registrando usuario en junta {user_data.id_junta}, comuna {user_data.id_comuna}")
        usuario, vecino = await auth_service.register_user(user_data)
        logger.info(f"✅ Usuario registrado exitosamente: ID {usuario.id_usuario}, Vecino ID {vecino.id_vecino}")
        
        # Preparar respuesta
        vecino_response = VecinoResponse(
            id_vecino=vecino.id_vecino,
            nombres=vecino.nombres,
            apellidos=vecino.apellidos,
            email=usuario.email,
            telefono=vecino.telefono,
            direccion=vecino.direccion,
            fecha_nacimiento=vecino.fecha_nacimiento
        )
        
        return UsuarioRegistroResponse(
            id_usuario=usuario.id_usuario,
            vecino=vecino_response
        )
        
    except ValueError as e:
        # Errores de validación de negocio
        logger.error(f"❌ Error de validación: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Error de validación",
                "detalle": str(e),
                "codigo": "VALIDATION_ERROR"
            }
        )
    
    except Exception as e:
        # Errores inesperados - MOSTRAR EL ERROR REAL
        logger.error(f"❌ Error interno del servidor: {str(e)}")
        logger.error(f"❌ Tipo de error: {type(e).__name__}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Error interno del servidor",
                "detalle": str(e),  # ← CAMBIO PRINCIPAL: mostrar error real
                "codigo": "INTERNAL_ERROR"
            }
        )


@router.get(
    "/comunas",
    response_model=ComunasList,
    summary="Listar comunas",
    description="Obtiene la lista de todas las comunas disponibles"
)
async def get_comunas(db: AsyncSession = Depends(get_db_session)):
    """
    Obtiene la lista de todas las comunas disponibles.
    
    Returns:
        Lista de comunas con sus IDs y nombres
    """
    try:
        auth_service = AuthService(db)
        comunas = await auth_service.get_all_comunas()
        
        return ComunasList(
            comunas=[
                {"id_comuna": c.id_comuna, "nombre": c.nombre}
                for c in comunas
            ],
            total=len(comunas)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Error al obtener comunas",
                "detalle": str(e)
            }
        )


@router.get(
    "/juntas/{comuna_id}",
    response_model=JuntasList,
    summary="Listar juntas por comuna",
    description="Obtiene la lista de juntas de vecinos de una comuna específica"
)
async def get_juntas_by_comuna(
    comuna_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Obtiene las juntas de vecinos de una comuna específica.
    
    Args:
        comuna_id: ID de la comuna
        
    Returns:
        Lista de juntas en la comuna especificada
    """
    try:
        auth_service = AuthService(db)
        juntas = await auth_service.get_juntas_by_comuna(comuna_id)
        
        return JuntasList(
            juntas=[
                {
                    "id_junta": j.id_junta,
                    "nombre": j.nombre,
                    "direccion": j.direccion,
                    "telefono": j.telefono,
                    "email": j.email
                }
                for j in juntas
            ],
            total=len(juntas)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Error al obtener juntas",
                "detalle": str(e)
            }
        )
