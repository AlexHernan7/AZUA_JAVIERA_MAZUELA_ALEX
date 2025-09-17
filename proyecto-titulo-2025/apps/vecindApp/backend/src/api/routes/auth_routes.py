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
    ErrorResponse,
    LoginRequest,
    LoginResponse,
    UserLoginData,
    VecinoLoginData,
)
from src.schemas.user_schemas import JuntasList, ComunasList
from src.core.security import create_access_token
from src.core.config import settings
from src.utils import binary_to_base64

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
        409: {"model": ErrorResponse, "description": "Email ya registrado"},
    },
)
async def register_user(
    user_data: UsuarioRegistroRequest, db: AsyncSession = Depends(get_db_session)
):
    """
    Registra un nuevo usuario y crea su perfil de vecino.
    
    Args:
        user_data: Datos del usuario a registrar
        db: Sesión de base de datos
    
    Returns:
        Datos del usuario y vecino creados
    """
    try:
        logger.info(f"🔄 Iniciando registro de usuario: {user_data.email}")

        # Crear servicio de autenticación
        auth_service = AuthService(db)
        logger.info("✅ Servicio de autenticación creado")

        # Registrar usuario
        logger.info(
            f"🔄 Registrando usuario en junta {user_data.id_junta}, comuna {user_data.id_comuna}"
        )
        usuario, vecino = await auth_service.register_user(user_data)
        logger.info(
            f"✅ Usuario registrado exitosamente: ID {usuario.id_usuario}, Vecino ID {vecino.id_vecino}"
        )

        # Convertir foto de perfil binaria a base64 para respuesta
        foto_perfil_base64 = None
        if vecino.foto_perfil:
            # Detectar si es SVG o imagen rasterizada
            if (
                vecino.foto_perfil.startswith(b"<svg")
                or b"<svg" in vecino.foto_perfil[:100]
            ):
                foto_perfil_base64 = binary_to_base64(
                    vecino.foto_perfil, "image/svg+xml"
                )
            else:
                foto_perfil_base64 = binary_to_base64(vecino.foto_perfil, "image/jpeg")

        # Preparar respuesta
        vecino_response = VecinoResponse(
            id_vecino=vecino.id_vecino,
            rut=vecino.rut,
            nombres=vecino.nombres,
            apellido_paterno=vecino.apellido_paterno,
            apellido_materno=vecino.apellido_materno,
            email=usuario.email,
            telefono=vecino.telefono,
            direccion=vecino.direccion,
            fecha_nacimiento=vecino.fecha_nacimiento,
            foto_perfil=foto_perfil_base64,
        )

        return UsuarioRegistroResponse(
            id_usuario=usuario.id_usuario, vecino=vecino_response
        )

    except ValueError as e:
        # Errores de validación de negocio
        logger.error(f"❌ Error de validación: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Error de validación",
                "detalle": str(e),
                "codigo": "VALIDATION_ERROR",
            },
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
                "codigo": "INTERNAL_ERROR",
            },
        )


@router.get(
    "/comunas",
    response_model=ComunasList,
    summary="Listar comunas",
    description="Obtiene la lista de todas las comunas disponibles",
)
async def get_comunas(db: AsyncSession = Depends(get_db_session)):
    """
    Obtiene la lista de todas las comunas disponibles.
    """
    try:
        auth_service = AuthService(db)
        comunas = await auth_service.get_all_comunas()

        return ComunasList(
            comunas=[{"id_comuna": c.id_comuna, "nombre": c.nombre} for c in comunas],
            total=len(comunas),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error al obtener comunas", "detalle": str(e)},
        )


@router.get(
    "/juntas/{comuna_id}",
    response_model=JuntasList,
    summary="Listar juntas por comuna",
    description="Obtiene la lista de juntas de vecinos de una comuna específica",
)
async def get_juntas_by_comuna(
    comuna_id: int, db: AsyncSession = Depends(get_db_session)
):
    """
    Obtiene las juntas de vecinos de una comuna específica.
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
                    "email": j.email,
                }
                for j in juntas
            ],
            total=len(juntas),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error al obtener juntas", "detalle": str(e)},
        )


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login_user(
    credentials: LoginRequest, db: AsyncSession = Depends(get_db_session)
):
    """
    Autentica usuario y genera JWT token.
    
    Args:
        credentials: Email y contraseña del usuario
        db: Sesión de base de datos
    
    Returns:
        LoginResponse con token JWT y datos del usuario
    """
    logger.info(f"🔐 Intento de login para: {credentials.email}")

    try:
        # 1. Crear servicio de autenticación
        auth_service = AuthService(db)
        logger.info("✅ Servicio de autenticación creado")

        # 2. Autenticar usuario
        logger.info(f"🔄 Autenticando usuario: {credentials.email}")
        usuario, vecino = await auth_service.login_user(
            credentials.email, credentials.password
        )

        # 3. Crear JWT token
        token_data = {
            "sub": str(usuario.id_usuario),  # subject = user id
            "email": usuario.email,
            "nombres": vecino.nombres if vecino else "",
            "apellido_paterno": vecino.apellido_paterno if vecino else "",
            "apellido_materno": vecino.apellido_materno if vecino else "",
        }

        access_token = create_access_token(token_data)
        logger.info(f"✅ Token JWT creado para usuario ID: {usuario.id_usuario}")

        # Convertir foto de perfil binaria a base64 para respuesta
        foto_perfil_base64 = None
        if vecino and vecino.foto_perfil:
            # Detectar si es SVG o imagen rasterizada
            if (
                vecino.foto_perfil.startswith(b"<svg")
                or b"<svg" in vecino.foto_perfil[:100]
            ):
                foto_perfil_base64 = binary_to_base64(
                    vecino.foto_perfil, "image/svg+xml"
                )
            else:
                foto_perfil_base64 = binary_to_base64(vecino.foto_perfil, "image/jpeg")

        # 4. Preparar respuesta
        user_data = UserLoginData(
            id_usuario=usuario.id_usuario,
            email=usuario.email,
            nombres=vecino.nombres if vecino else "",
            apellido_paterno=vecino.apellido_paterno if vecino else "",
            apellido_materno=vecino.apellido_materno if vecino else "",
            activo=usuario.activo,
            vecino=(
                VecinoLoginData(
                    nombres=vecino.nombres,
                    apellido_paterno=vecino.apellido_paterno,
                    apellido_materno=vecino.apellido_materno,
                    rut=vecino.rut,
                    fecha_nacimiento=vecino.fecha_nacimiento,
                    telefono=vecino.telefono,
                    direccion=vecino.direccion,
                    foto_perfil=foto_perfil_base64,
                    comuna=vecino.comuna.nombre if vecino.comuna else None,
                    region=(
                        vecino.comuna.region.nombre
                        if vecino.comuna and vecino.comuna.region
                        else None
                    ),
                    junta=vecino.junta.nombre if vecino.junta else None,
                )
                if vecino
                else None
            ),
        )

        response = LoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.api.access_token_expire_minutes,
            user=user_data,
        )

        logger.info(f"✅ Login exitoso para: {credentials.email}")
        return response

    except ValueError as e:
        # Error de credenciales inválidas
        logger.warning(f"❌ Login fallido para {credentials.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Credenciales inválidas", "detalle": str(e)},
        )

    except Exception as e:
        # Error interno del servidor
        logger.error(f"💥 Error interno en login para {credentials.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error interno del servidor", "detalle": str(e)},
        )
