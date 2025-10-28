"""
Rutas de autenticación para VecindApp.

Contiene endpoints para registro, login, etc.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import logging

from src.database.session import get_db_session
from src.database.models.usuario import Usuario
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
    PasswordResetRequest,
    PasswordResetResponse,
    VerifyResetCodeRequest,
    ResetPasswordRequest,
    ResetPasswordResponse,
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
    "/regiones",
    summary="Listar regiones",
    description="Obtiene la lista de todas las regiones disponibles desde la base de datos",
)
async def get_regiones(db: AsyncSession = Depends(get_db_session)):
    """
    Obtiene la lista de todas las regiones disponibles desde la base de datos.
    """
    try:
        from src.database.models.region import Region
        from sqlalchemy import select
        
        result = await db.execute(
            select(Region).order_by(Region.nombre)
        )
        regiones = result.scalars().all()
        
        return {
            "regiones": [
                {
                    "id_region": region.id_region,
                    "nombre": region.nombre
                } 
                for region in regiones
            ],
            "total": len(regiones)
        }

    except Exception as e:
        logger.error(f"Error al obtener regiones: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error al obtener regiones", "detalle": str(e)},
        )


@router.get(
    "/comunas",
    summary="Listar todas las comunas (desde JSON)",
    description="Obtiene la lista de todas las comunas disponibles desde el JSON estático",
)
async def get_comunas():
    """
    Obtiene la lista de todas las comunas disponibles desde el JSON.
    """
    try:
        from src.utils.regiones_comunas_data import get_all_comunas
        
        comunas = get_all_comunas()
        
        return {
            "comunas": [{"nombre": comuna} for comuna in comunas],
            "total": len(comunas)
        }

    except Exception as e:
        logger.error(f"Error al obtener comunas desde JSON: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error al obtener comunas", "detalle": str(e)},
        )


@router.get(
    "/comunas/region/{region_id}",
    summary="Listar comunas por región",
    description="Obtiene la lista de comunas de una región específica desde la base de datos",
)
async def get_comunas_by_region(region_id: int, db: AsyncSession = Depends(get_db_session)):
    """
    Obtiene las comunas de una región específica desde la base de datos.
    
    Args:
        region_id: ID de la región
        db: Sesión de base de datos
    """
    try:
        from src.database.models.region import Region
        from src.database.models.comuna import Comuna
        from sqlalchemy import select
        
        # Verificar que la región existe
        result = await db.execute(
            select(Region).where(Region.id_region == region_id)
        )
        region = result.scalar_one_or_none()
        
        if not region:
            logger.warning(f"Región no encontrada: ID {region_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Región no encontrada", "detalle": f"No existe la región con ID {region_id}"},
            )
        
        # Obtener comunas de la región
        result = await db.execute(
            select(Comuna)
            .where(Comuna.id_region == region_id)
            .order_by(Comuna.nombre)
        )
        comunas = result.scalars().all()
        
        return {
            "region_id": region_id,
            "region_nombre": region.nombre,
            "comunas": [
                {
                    "id_comuna": comuna.id_comuna,
                    "nombre": comuna.nombre
                } 
                for comuna in comunas
            ],
            "total": len(comunas)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener comunas por región: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error al obtener comunas", "detalle": str(e)},
        )


@router.get(
    "/regiones-comunas/estructura",
    summary="Obtener estructura completa de regiones y comunas",
    description="Obtiene la estructura completa de regiones con sus comunas desde el JSON estático",
)
async def get_regiones_comunas_estructura():
    """
    Obtiene la estructura completa de regiones y comunas.
    Útil para formularios que necesitan mostrar ambos selectores.
    """
    try:
        from src.utils.regiones_comunas_data import get_regiones_comunas_structure
        
        estructura = get_regiones_comunas_structure()
        
        return {
            "data": estructura,
            "total_regiones": len(estructura)
        }

    except Exception as e:
        logger.error(f"Error al obtener estructura de regiones-comunas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error al obtener estructura", "detalle": str(e)},
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
        usuario, vecino, directiva, roles = await auth_service.login_user(
            credentials.email, credentials.password
        )
        logger.info(f"✅ Usuario autenticado con roles: {roles}")

        # 3. Determinar datos personales (vecino o directiva)
        if vecino:
            nombres = vecino.nombres
            apellido_paterno = vecino.apellido_paterno
            apellido_materno = vecino.apellido_materno
        elif directiva:
            nombres = directiva.nombres
            apellido_paterno = directiva.apellido_paterno
            apellido_materno = directiva.apellido_materno
        else:
            # Usuario administrativo sin perfil
            nombres = ""
            apellido_paterno = ""
            apellido_materno = ""

        # 4. Crear JWT token
        token_data = {
            "sub": str(usuario.id_usuario),  # subject = user id
            "email": usuario.email,
            "nombres": nombres,
            "apellido_paterno": apellido_paterno,
            "apellido_materno": apellido_materno,
            "roles": roles,  # Incluir roles en el token
        }

        access_token = create_access_token(token_data)
        logger.info(f"✅ Token JWT creado para usuario ID: {usuario.id_usuario}")

        # 5. Convertir foto de perfil binaria a base64 para respuesta
        foto_perfil_base64 = None
        foto_perfil_source = None
        
        if vecino and vecino.foto_perfil:
            foto_perfil_source = vecino.foto_perfil
        elif directiva and directiva.foto_perfil:
            foto_perfil_source = directiva.foto_perfil
            
        if foto_perfil_source:
            # Detectar si es SVG o imagen rasterizada
            if (
                foto_perfil_source.startswith(b"<svg")
                or b"<svg" in foto_perfil_source[:100]
            ):
                foto_perfil_base64 = binary_to_base64(
                    foto_perfil_source, "image/svg+xml"
                )
            else:
                foto_perfil_base64 = binary_to_base64(foto_perfil_source, "image/jpeg")

        # 6. Preparar respuesta
        user_data = UserLoginData(
            id_usuario=usuario.id_usuario,
            email=usuario.email,
            nombres=nombres,
            apellido_paterno=apellido_paterno,
            apellido_materno=apellido_materno,
            activo=usuario.activo,
            roles=roles,  # Incluir roles en la respuesta
            vecino=(
                VecinoLoginData(
                    id_vecino=vecino.id_vecino,
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
                    id_junta=vecino.junta.id_junta if vecino.junta else None,
                )
                if vecino
                else (
                    # Para directivos, crear un VecinoLoginData con datos de directiva
                    VecinoLoginData(
                        id_vecino=directiva.id_directiva,  # Usar ID de directiva como identificador
                        nombres=directiva.nombres,
                        apellido_paterno=directiva.apellido_paterno,
                        apellido_materno=directiva.apellido_materno,
                        rut=directiva.rut,
                        fecha_nacimiento=None,  # Los directivos no tienen fecha de nacimiento
                        telefono=directiva.telefono,
                        direccion=None,  # Los directivos no tienen dirección personal
                        foto_perfil=foto_perfil_base64,
                        comuna=None,  # Los directivos no tienen comuna personal
                        region=None,
                        junta=directiva.junta.nombre if directiva.junta else None,
                        id_junta=directiva.junta.id_junta if directiva.junta else None,
                        cargo=directiva.cargo,  # Agregar el cargo del directivo
                        fecha_inicio_cargo=directiva.fecha_inicio_cargo.isoformat() if directiva.fecha_inicio_cargo else None,
                        fecha_termino_cargo=directiva.fecha_termino_cargo.isoformat() if directiva.fecha_termino_cargo else None,
                    )
                    if directiva
                    else None
                )
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


# ==================== ENDPOINTS DE RECUPERACIÓN DE CONTRASEÑA ====================


@router.post(
    "/password-reset/request",
    response_model=PasswordResetResponse,
    status_code=status.HTTP_200_OK,
    summary="Solicitar código de recuperación",
    description="Envía un código de 6 dígitos al email del usuario para recuperar su contraseña"
)
async def request_password_reset(
    request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Solicita un código de recuperación de contraseña.
    
    - Verifica que el email exista
    - Genera código de 6 dígitos
    - Envía email con el código
    - El código expira en 15 minutos
    """
    try:
        logger.info(f"🔐 Solicitud de recuperación de contraseña para: {request.email}")
        
        # Crear servicio de autenticación
        auth_service = AuthService(db)
        
        # Solicitar código de recuperación
        success, code = await auth_service.request_password_reset(request.email)
        
        if not success:
            raise ValueError("No se pudo generar el código")
        
        # Obtener nombre del usuario para personalizar email
        result = await db.execute(
            select(Usuario).options(
                selectinload(Usuario.vecino),
                selectinload(Usuario.directiva)
            ).where(Usuario.email == request.email.lower())
        )
        usuario = result.scalar_one_or_none()
        
        user_name = "Usuario"
        if usuario:
            if usuario.vecino:
                user_name = usuario.vecino.nombres
            elif usuario.directiva:
                user_name = usuario.directiva.nombres
        
        # Enviar email con código usando Brevo
        from src.core.config import settings
        from src.services.email_service import EmailService
        
        # Verificar si estamos en modo desarrollo
        is_development = settings.ENVIRONMENT != "PRODUCTION"
        
        if not settings.BREVO_API_KEY:
            logger.warning("⚠️  BREVO_API_KEY no configurada")
            if is_development:
                logger.warning(f"🔑 CÓDIGO DE DESARROLLO: {code} para {request.email}")
                return PasswordResetResponse(
                    message=f"Modo desarrollo - Tu código es: {code}",
                    email=request.email
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"error": "Servicio de email no configurado", "detalle": "Contacta al administrador"}
            )
        
        # Intentar enviar email con Brevo
        email_service = EmailService(
            api_key=settings.BREVO_API_KEY,
            from_email=settings.BREVO_FROM_EMAIL,
            from_name=settings.BREVO_FROM_NAME
        )
        
        email_sent = email_service.send_password_reset_code(
            to_email=request.email,
            code=code,
            user_name=user_name
        )
        
        if not email_sent:
            # Si falla el envío (ej: error en la API de Brevo)
            if is_development:
                logger.warning(f"⚠️  No se pudo enviar email - Devolviendo código: {code}")
                return PasswordResetResponse(
                    message=f"[DEV] Email no disponible - Tu código es: {code}",
                    email=request.email
                )
            logger.error(f"❌ No se pudo enviar email a {request.email}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"error": "No se pudo enviar el email", "detalle": "Error en el servicio de correo Brevo"}
            )
        
        logger.info(f"✅ Código de recuperación enviado a {request.email}")
        
        return PasswordResetResponse(
            message="Código de recuperación enviado a tu email",
            email=request.email
        )
        
    except ValueError as e:
        logger.warning(f"⚠️ Error en solicitud de recuperación: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Usuario no encontrado", "detalle": str(e)}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Error inesperado en recuperación de contraseña: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error interno del servidor", "detalle": str(e)}
        )


@router.post(
    "/password-reset/verify",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Verificar código de recuperación",
    description="Verifica si un código de 6 dígitos es válido"
)
async def verify_reset_code(request: VerifyResetCodeRequest):
    """
    Verifica si un código de recuperación es válido.
    
    - Valida que el código sea correcto
    - Verifica que no haya expirado
    """
    try:
        logger.info(f"🔍 Verificando código para: {request.email}")
        
        is_valid = AuthService.verify_reset_code(request.email, request.code)
        
        if not is_valid:
            logger.warning(f"⚠️ Código inválido o expirado para {request.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "Código inválido", "detalle": "El código es incorrecto o ha expirado"}
            )
        
        logger.info(f"✅ Código válido para {request.email}")
        
        return {
            "message": "Código válido",
            "valid": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Error verificando código: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error interno del servidor", "detalle": str(e)}
        )


@router.post(
    "/password-reset/confirm",
    response_model=ResetPasswordResponse,
    status_code=status.HTTP_200_OK,
    summary="Resetear contraseña",
    description="Resetea la contraseña del usuario usando el código de verificación"
)
async def reset_password(
    request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Resetea la contraseña del usuario.
    
    - Verifica el código
    - Valida la nueva contraseña
    - Actualiza la contraseña
    - Invalida el código
    """
    try:
        logger.info(f"🔒 Reseteando contraseña para: {request.email}")
        
        # Crear servicio de autenticación
        auth_service = AuthService(db)
        
        # Resetear contraseña
        success = await auth_service.reset_password(
            email=request.email,
            code=request.code,
            new_password=request.new_password
        )
        
        if not success:
            raise ValueError("No se pudo actualizar la contraseña")
        
        logger.info(f"✅ Contraseña actualizada exitosamente para {request.email}")
        
        return ResetPasswordResponse(
            message="Contraseña actualizada exitosamente",
            success=True
        )
        
    except ValueError as e:
        logger.warning(f"⚠️ Error reseteando contraseña: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Error al resetear contraseña", "detalle": str(e)}
        )
    except Exception as e:
        logger.error(f"💥 Error inesperado reseteando contraseña: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error interno del servidor", "detalle": str(e)}
        )