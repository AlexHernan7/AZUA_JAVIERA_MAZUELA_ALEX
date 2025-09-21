"""
Servicio para manejo de directivos de juntas de vecinos.

Maneja el registro, autenticación y gestión de directivos.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from typing import Optional, Tuple

from src.database.models.usuario import Usuario
from src.database.models.directiva import Directiva
from src.database.models.junta import Junta
from src.database.models.rol import Rol
from src.database.models.usuario_rol import UsuarioRol
from src.core.security import hash_password, validate_password_strength
from src.schemas.directiva_schemas import DirectivaRegistroRequest
from src.utils import base64_to_binary, load_default_profile_image


class DirectivaService:
    """
    Servicio para manejar directivos de juntas de vecinos.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_directivo(
        self, directivo_data: DirectivaRegistroRequest
    ) -> Tuple[Usuario, Directiva]:
        """
        Registra un nuevo directivo y su usuario asociado.
        
        Args:
            directivo_data: Datos del directivo a registrar
        
        Returns:
            Tupla (Usuario, Directiva) creados
        """

        # 1. Validar contraseña
        is_valid, error_msg = validate_password_strength(directivo_data.password)
        if not is_valid:
            raise ValueError(f"Contraseña inválida: {error_msg}")

        # 2. Verificar que la junta existe
        junta = await self._get_junta_by_id(directivo_data.id_junta)
        if not junta:
            raise ValueError("La junta especificada no existe")

        # 3. Verificar que no existe otro usuario con el mismo email en la junta
        existing_user = await self._get_user_by_email_and_junta(
            directivo_data.email, directivo_data.id_junta
        )
        if existing_user:
            raise ValueError("Ya existe un usuario con este email en la junta")

        # 4. Verificar que no existe otro directivo con el mismo RUT
        existing_directivo = await self._get_directivo_by_rut(directivo_data.rut)
        if existing_directivo:
            raise ValueError("Ya existe un directivo con este RUT")

        # 5. Verificar que no hay otro directivo activo con el mismo cargo en la junta
        existing_cargo = await self._get_directivo_by_cargo_and_junta(
            directivo_data.cargo, directivo_data.id_junta
        )
        if existing_cargo:
            raise ValueError(f"Ya existe un {directivo_data.cargo} activo en esta junta")

        try:
            # 6. Crear usuario
            hashed_password = hash_password(directivo_data.password)
            usuario = Usuario(
                id_junta=directivo_data.id_junta,
                email=directivo_data.email,
                pass_hash=hashed_password,
                activo=True,
            )
            self.db.add(usuario)
            await self.db.flush()  # Para obtener el ID sin hacer commit

            # 7. Crear perfil de directivo
            # Formatear teléfono con +56
            telefono_formateado = directivo_data.telefono
            if not telefono_formateado.startswith("+56"):
                if telefono_formateado.startswith("56"):
                    telefono_formateado = f"+{telefono_formateado}"
                else:
                    telefono_formateado = f"+56{telefono_formateado}"

            # Manejar foto de perfil (usar por defecto si no se proporciona)
            foto_perfil_binaria = None
            if directivo_data.foto_perfil:
                foto_perfil_binaria = base64_to_binary(directivo_data.foto_perfil)
            else:
                foto_perfil_binaria = load_default_profile_image()

            directiva = Directiva(
                id_junta=directivo_data.id_junta,
                id_usuario=usuario.id_usuario,
                rut=directivo_data.rut,
                nombres=directivo_data.nombres,
                apellido_paterno=directivo_data.apellido_paterno,
                apellido_materno=directivo_data.apellido_materno,
                telefono=telefono_formateado,
                email=directivo_data.email,
                cargo=directivo_data.cargo,
                fecha_inicio_cargo=directivo_data.fecha_inicio_cargo,
                fecha_termino_cargo=directivo_data.fecha_termino_cargo,
                foto_perfil=foto_perfil_binaria,
            )
            self.db.add(directiva)
            await self.db.flush()

            # 8. Asignar rol de directiva
            await self._assign_directiva_role(usuario.id_usuario)

            # 9. Hacer commit de toda la transacción
            await self.db.commit()

            # 10. Refrescar objetos para obtener datos actualizados
            await self.db.refresh(usuario)
            await self.db.refresh(directiva)

            return usuario, directiva

        except IntegrityError as e:
            await self.db.rollback()
            if "ux_usuario_email" in str(e):
                raise ValueError("Ya existe un usuario con este email en la junta")
            elif "directiva_rut_key" in str(e):
                raise ValueError("Ya existe un directivo con este RUT")
            raise ValueError(f"Error de integridad en la base de datos: {str(e)}")

        except Exception as e:
            await self.db.rollback()
            raise ValueError(f"Error al registrar directivo: {str(e)}")

    async def _get_junta_by_id(self, junta_id: int) -> Optional[Junta]:
        """Obtiene una junta por su ID."""
        result = await self.db.execute(select(Junta).where(Junta.id_junta == junta_id))
        return result.scalar_one_or_none()

    async def _get_user_by_email_and_junta(
        self, email: str, junta_id: int
    ) -> Optional[Usuario]:
        """Verifica si ya existe un usuario con el email en la junta."""
        result = await self.db.execute(
            select(Usuario).where(Usuario.email == email, Usuario.id_junta == junta_id)
        )
        return result.scalar_one_or_none()

    async def _get_directivo_by_rut(self, rut: str) -> Optional[Directiva]:
        """Verifica si ya existe un directivo con el RUT."""
        result = await self.db.execute(
            select(Directiva).where(Directiva.rut == rut)
        )
        return result.scalar_one_or_none()

    async def _get_directivo_by_cargo_and_junta(
        self, cargo: str, junta_id: int
    ) -> Optional[Directiva]:
        """Verifica si ya existe un directivo activo con el mismo cargo en la junta."""
        result = await self.db.execute(
            select(Directiva).where(
                Directiva.cargo == cargo,
                Directiva.id_junta == junta_id,
                Directiva.fecha_termino_cargo.is_(None)  # Solo directivos activos
            )
        )
        return result.scalar_one_or_none()

    async def _assign_directiva_role(self, user_id: int) -> None:
        """Asigna el rol de 'directiva' al usuario."""
        # Obtener el rol de directiva
        result = await self.db.execute(select(Rol).where(Rol.codigo == "directiva"))
        rol_directiva = result.scalar_one_or_none()

        if not rol_directiva:
            raise ValueError("No se encontró el rol de directiva en el sistema")

        # Crear la relación usuario-rol
        usuario_rol = UsuarioRol(id_usuario=user_id, id_rol=rol_directiva.id_rol)
        self.db.add(usuario_rol)

    async def get_directivos_by_junta(self, junta_id: int) -> list[Directiva]:
        """
        Obtiene todos los directivos de una junta.

        Args:
            junta_id: ID de la junta

        Returns:
            Lista de directivos en la junta
        """
        result = await self.db.execute(
            select(Directiva)
            .options(selectinload(Directiva.junta))
            .where(Directiva.id_junta == junta_id)
            .order_by(Directiva.fecha_inicio_cargo.desc())
        )
        return list(result.scalars().all())

    async def get_directivos_activos_by_junta(self, junta_id: int) -> list[Directiva]:
        """
        Obtiene todos los directivos activos de una junta.

        Args:
            junta_id: ID de la junta

        Returns:
            Lista de directivos activos en la junta
        """
        result = await self.db.execute(
            select(Directiva)
            .options(selectinload(Directiva.junta))
            .where(
                Directiva.id_junta == junta_id,
                Directiva.fecha_termino_cargo.is_(None)
            )
            .order_by(Directiva.fecha_inicio_cargo.desc())
        )
        return list(result.scalars().all())
