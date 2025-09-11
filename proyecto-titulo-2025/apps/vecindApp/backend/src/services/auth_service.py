"""
Servicio de autenticación para VecindApp.

Maneja el registro, login y validaciones de usuarios.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from typing import Optional, Tuple

from src.database.models.usuario import Usuario
from src.database.models.vecino import Vecino
from src.database.models.junta import Junta
from src.database.models.comuna import Comuna
from src.database.models.rol import Rol
from src.database.models.usuario_rol import UsuarioRol
from src.core.security import hash_password, validate_password_strength, verify_password
from src.schemas.auth_schemas import UsuarioRegistroRequest
from src.schemas.user_schemas import VecinoCreate
from src.utils import base64_to_binary, load_default_profile_image


class AuthService:
    """
    Servicio para manejar autenticación y registro de usuarios.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def register_user(self, user_data: UsuarioRegistroRequest) -> Tuple[Usuario, Vecino]:
        """
        Registra un nuevo usuario y su perfil de vecino.
        
        Args:
            user_data: Datos del usuario a registrar
            
        Returns:
            Tupla (Usuario, Vecino) creados
            
        Raises:
            ValueError: Si hay errores de validación
            IntegrityError: Si el email ya existe
        """
        
        # 1. Validar contraseña
        is_valid, error_msg = validate_password_strength(user_data.password)
        if not is_valid:
            raise ValueError(f"Contraseña inválida: {error_msg}")
        
        # 2. Verificar que la junta existe y pertenece a la comuna
        junta = await self._get_junta_by_id(user_data.id_junta)
        if not junta:
            raise ValueError("La junta especificada no existe")
        
        if junta.id_comuna != user_data.id_comuna:
            raise ValueError("La junta no pertenece a la comuna seleccionada")
        
        # 3. Verificar que no existe otro usuario con el mismo email en la junta
        existing_user = await self._get_user_by_email_and_junta(
            user_data.email, user_data.id_junta
        )
        if existing_user:
            raise ValueError("Ya existe un usuario con este email en la junta")
        
        try:
            # 4. Crear usuario
            hashed_password = hash_password(user_data.password)
            usuario = Usuario(
                id_junta=user_data.id_junta,
                email=user_data.email,
                pass_hash=hashed_password,
                activo=True
            )
            self.db.add(usuario)
            await self.db.flush()  # Para obtener el ID sin hacer commit
            
            # 5. Crear perfil de vecino
            # Mantener teléfono con formato +56
            telefono_formateado = user_data.telefono
            if not telefono_formateado.startswith('+56'):
                # Si no tiene +56, agregarlo
                if telefono_formateado.startswith('56'):
                    telefono_formateado = f"+{telefono_formateado}"
                else:
                    telefono_formateado = f"+56{telefono_formateado}"
            
            # Manejar foto de perfil (usar por defecto si no se proporciona)
            foto_perfil_binaria = None
            if user_data.foto_perfil:
                # Convertir base64 a binario
                foto_perfil_binaria = base64_to_binary(user_data.foto_perfil)
            else:
                # Usar imagen por defecto
                foto_perfil_binaria = load_default_profile_image()
            
            vecino = Vecino(
                id_junta=user_data.id_junta,
                id_usuario=usuario.id_usuario,
                rut=user_data.rut,
                nombres=user_data.nombres,
                apellido_paterno=user_data.apellido_paterno,
                apellido_materno=user_data.apellido_materno,
                email=user_data.email,
                fecha_nacimiento=user_data.fecha_nacimiento,
                telefono=telefono_formateado,  # Almacenar con formato +56
                direccion=user_data.direccion,
                foto_perfil=foto_perfil_binaria,
                id_comuna=user_data.id_comuna
            )
            self.db.add(vecino)
            await self.db.flush()
            
            # 6. Asignar rol de vecino por defecto
            await self._assign_default_role(usuario.id_usuario)
            
            # 7. Hacer commit de toda la transacción
            await self.db.commit()
            
            # 8. Refrescar objetos para obtener datos actualizados
            await self.db.refresh(usuario)
            await self.db.refresh(vecino)
            
            return usuario, vecino
            
        except IntegrityError as e:
            await self.db.rollback()
            if "ux_usuario_email" in str(e):
                raise ValueError("Ya existe un usuario con este email en la junta")
            raise ValueError(f"Error de integridad en la base de datos: {str(e)}")
        
        except Exception as e:
            await self.db.rollback()
            raise ValueError(f"Error al registrar usuario: {str(e)}")
    
    async def _get_junta_by_id(self, junta_id: int) -> Optional[Junta]:
        """Obtiene una junta por su ID."""
        result = await self.db.execute(
            select(Junta).where(Junta.id_junta == junta_id)
        )
        return result.scalar_one_or_none()
    
    async def _get_user_by_email_and_junta(self, email: str, junta_id: int) -> Optional[Usuario]:
        """Verifica si ya existe un usuario con el email en la junta."""
        result = await self.db.execute(
            select(Usuario).where(
                Usuario.email == email,
                Usuario.id_junta == junta_id
            )
        )
        return result.scalar_one_or_none()
    
    async def _assign_default_role(self, user_id: int) -> None:
        """Asigna el rol de 'vecino' por defecto al usuario."""
        # Obtener el rol de vecino
        result = await self.db.execute(
            select(Rol).where(Rol.codigo == "vecino")
        )
        rol_vecino = result.scalar_one_or_none()
        
        if not rol_vecino:
            raise ValueError("No se encontró el rol de vecino en el sistema")
        
        # Crear la relación usuario-rol
        usuario_rol = UsuarioRol(
            id_usuario=user_id,
            id_rol=rol_vecino.id_rol
        )
        self.db.add(usuario_rol)
    
    async def get_juntas_by_comuna(self, comuna_id: int) -> list[Junta]:
        """
        Obtiene todas las juntas de una comuna.
        
        Args:
            comuna_id: ID de la comuna
            
        Returns:
            Lista de juntas en la comuna
        """
        result = await self.db.execute(
            select(Junta).where(Junta.id_comuna == comuna_id)
        )
        return list(result.scalars().all())
    
    async def get_all_comunas(self) -> list[Comuna]:
        """
        Obtiene todas las comunas disponibles.
        
        Returns:
            Lista de todas las comunas
        """
        result = await self.db.execute(select(Comuna))
        return list(result.scalars().all())
    
    async def login_user(self, email: str, password: str) -> tuple[Usuario, Vecino]:
        """
        Autentica un usuario con email y contraseña.
        
        Args:
            email: Email del usuario
            password: Contraseña en texto plano
            
        Returns:
            Tupla (Usuario, Vecino) si la autenticación es exitosa
            
        Raises:
            ValueError: Si las credenciales son inválidas o el usuario está inactivo
        """
        # 1. Buscar usuario por email
        result = await self.db.execute(
            select(Usuario).where(Usuario.email == email)
        )
        usuario = result.scalar_one_or_none()
        
        if not usuario:
            raise ValueError("Credenciales inválidas")
        
        # 2. Verificar contraseña
        if not verify_password(password, usuario.pass_hash):
            raise ValueError("Credenciales inválidas")
        
        # 3. Verificar que el usuario esté activo
        if not usuario.activo:
            raise ValueError("Usuario inactivo")
        
        # 4. Obtener datos del vecino asociado
        result = await self.db.execute(
            select(Vecino).where(Vecino.id_usuario == usuario.id_usuario)
        )
        vecino = result.scalar_one_or_none()
        
        if not vecino:
            raise ValueError("No se encontró perfil de vecino asociado")
        
        return usuario, vecino
