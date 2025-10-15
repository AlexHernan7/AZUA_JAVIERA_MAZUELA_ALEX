"""
Servicio para manejo de usuarios y vecinos.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
from typing import Optional, List

from src.database.models.usuario import Usuario
from src.database.models.vecino import Vecino
from src.database.models.junta import Junta
from src.database.models.rol import Rol
from src.database.models.usuario_rol import UsuarioRol
from src.utils.image_utils import base64_to_binary


class UserService:
    """
    Servicio para operaciones relacionadas con usuarios y vecinos.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_id(self, user_id: int) -> Optional[Usuario]:
        """
        Obtiene un usuario por su ID.
        """
        result = await self.db.execute(
            select(Usuario).where(Usuario.id_usuario == user_id)
        )
        return result.scalar_one_or_none()

    async def get_vecino_by_user_id(self, user_id: int) -> Optional[Vecino]:
        """
        Obtiene el perfil de vecino asociado a un usuario.
        """
        result = await self.db.execute(
            select(Vecino).where(Vecino.id_usuario == user_id)
        )
        return result.scalar_one_or_none()

    async def get_vecino_by_id(self, vecino_id: int) -> Optional[Vecino]:
        """
        Obtiene un vecino por su ID.
        """
        result = await self.db.execute(
            select(Vecino).where(Vecino.id_vecino == vecino_id)
        )
        return result.scalar_one_or_none()

    async def get_all_users_with_details(self) -> List[tuple[Usuario, Vecino, Junta]]:
        """
        Obtiene todos los usuarios con sus datos de vecino y junta.
        """
        result = await self.db.execute(
            select(Usuario, Vecino, Junta)
            .join(Vecino, Usuario.id_usuario == Vecino.id_usuario)
            .join(Junta, Usuario.id_junta == Junta.id_junta)
            .order_by(Vecino.apellido_paterno, Vecino.nombres)
        )
        return list(result.all())

    async def is_user_admin(self, user_id: int) -> bool:
        """
        Verifica si un usuario tiene rol de administrador.
        """
        result = await self.db.execute(
            select(UsuarioRol)
            .join(Rol, UsuarioRol.id_rol == Rol.id_rol)
            .where(UsuarioRol.id_usuario == user_id, Rol.codigo == "admin")
        )
        return result.scalar_one_or_none() is not None

    async def get_vecinos_by_junta(self, junta_id: int, activos_only: bool = False) -> List[Vecino]:
        """
        Obtiene todos los vecinos de una junta específica.
        
        Args:
            junta_id: ID de la junta
            activos_only: Si True, solo devuelve vecinos activos
            
        Returns:
            Lista de vecinos de la junta
        """
        from src.database.models.comuna import Comuna
        from src.database.models.region import Region
        from sqlalchemy.orm import selectinload
        
        query = (
            select(Vecino)
            .options(
                selectinload(Vecino.usuario),
                selectinload(Vecino.junta),
                selectinload(Vecino.comuna).selectinload(Comuna.region)
            )
            .where(Vecino.id_junta == junta_id)
        )
        
        if activos_only:
            query = query.join(Usuario, Vecino.id_usuario == Usuario.id_usuario).where(Usuario.activo == True)
        
        query = query.order_by(Vecino.apellido_paterno, Vecino.nombres)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_vecinos_by_user_junta(self, user_id: int, activos_only: bool = False) -> List[Vecino]:
        """
        Obtiene los vecinos de la junta del usuario logueado.
        
        Args:
            user_id: ID del usuario logueado
            activos_only: Si True, solo devuelve vecinos activos
            
        Returns:
            Lista de vecinos de la junta del usuario
            
        Raises:
            ValueError: Si el usuario no tiene perfil de vecino o no pertenece a una junta
        """
        # Primero intentar obtener el perfil de directivo del usuario
        from src.database.models.directiva import Directiva
        from sqlalchemy.orm import selectinload
        
        directiva_result = await self.db.execute(
            select(Directiva)
            .options(selectinload(Directiva.junta))
            .where(Directiva.id_usuario == user_id)
        )
        directiva = directiva_result.scalar_one_or_none()
        
        if directiva:
            # El usuario es un directivo, obtener vecinos de su junta
            return await self.get_vecinos_by_junta(directiva.id_junta, activos_only)
        
        # Si no es directivo, intentar obtener el perfil de vecino
        vecino = await self.get_vecino_by_user_id(user_id)
        if not vecino:
            raise ValueError("Usuario no tiene perfil de vecino ni de directivo")

        if not vecino.id_junta:
            raise ValueError("Usuario no pertenece a ninguna junta")

        # Obtener los vecinos de la junta del vecino
        return await self.get_vecinos_by_junta(vecino.id_junta, activos_only)

    async def update_vecino_profile(
        self,
        vecino_id: int,
        apellido_paterno: Optional[str] = None,
        apellido_materno: Optional[str] = None,
        email: Optional[str] = None,
        telefono: Optional[str] = None,
        direccion: Optional[str] = None,
        id_comuna: Optional[int] = None,
        comuna_nombre: Optional[str] = None,
        foto_perfil: Optional[str] = None,
    ) -> Optional[Vecino]:
        """
        Actualiza los datos del perfil del vecino.
        
        Campos NO editables: nombres, rut, fecha_nacimiento (datos de identificación inmutables)
        Campos editables: apellidos, email, telefono, direccion, id_comuna/comuna_nombre, foto_perfil

        Args:
            vecino_id: ID del vecino
            apellido_paterno: Nuevo apellido paterno (opcional)
            apellido_materno: Nuevo apellido materno (opcional)
            email: Nuevo email (opcional)
            telefono: Nuevo teléfono (opcional)
            direccion: Nueva dirección (opcional)
            id_comuna: Nuevo ID de comuna (opcional)
            comuna_nombre: Nombre de la comuna (alternativa a id_comuna)
            foto_perfil: Nueva foto de perfil en base64 (opcional)

        Returns:
            Vecino actualizado o None si no existe
        """
        # Verificar que el vecino existe
        vecino = await self.get_vecino_by_id(vecino_id)
        if not vecino:
            return None

        update_data = {}

        if apellido_paterno is not None:
            update_data["apellido_paterno"] = apellido_paterno

        if apellido_materno is not None:
            update_data["apellido_materno"] = apellido_materno

        if direccion is not None:
            update_data["direccion"] = direccion

        if email is not None:
            # Verificar email único en la junta
            existing_vecino = await self.db.execute(
                select(Vecino).where(
                    Vecino.email == email,
                    Vecino.id_junta == vecino.id_junta,
                    Vecino.id_vecino != vecino_id,
                )
            )
            if existing_vecino.scalar_one_or_none():
                raise ValueError(
                    "El email ya está en uso por otro vecino en esta junta"
                )

            update_data["email"] = email

            # Sincronizar con tabla usuario
            if vecino.id_usuario:
                await self.db.execute(
                    update(Usuario)
                    .where(Usuario.id_usuario == vecino.id_usuario)
                    .values(email=email)
                )

        if telefono is not None:
            update_data["telefono"] = telefono

        # Manejar actualización de comuna (por ID o por nombre)
        comuna_id_to_update = None
        
        if id_comuna is not None:
            comuna_id_to_update = id_comuna
        elif comuna_nombre is not None:
            # Buscar el ID de la comuna por su nombre (búsqueda flexible, case-insensitive)
            from src.database.models.comuna import Comuna
            from sqlalchemy import func
            
            result = await self.db.execute(
                select(Comuna).where(
                    func.lower(func.trim(Comuna.nombre)) == func.lower(func.trim(comuna_nombre))
                )
            )
            comuna = result.scalar_one_or_none()
            if not comuna:
                raise ValueError(f"No se encontró la comuna: {comuna_nombre}")
            comuna_id_to_update = comuna.id_comuna
        
        if comuna_id_to_update is not None:
            # Validar que la comuna existe
            from src.database.models.comuna import Comuna
            result = await self.db.execute(
                select(Comuna).where(Comuna.id_comuna == comuna_id_to_update)
            )
            comuna = result.scalar_one_or_none()
            if not comuna:
                raise ValueError("La comuna especificada no existe")
            
            update_data["id_comuna"] = comuna_id_to_update

        if foto_perfil is not None:
            try:
                # Convertir base64 a binario
                foto_binaria = base64_to_binary(foto_perfil)
                update_data["foto_perfil"] = foto_binaria
            except ValueError as e:
                raise ValueError(f"Error al procesar la foto de perfil: {str(e)}")

        if not update_data:
            return vecino

        try:
            # Actualizar vecino
            await self.db.execute(
                update(Vecino)
                .where(Vecino.id_vecino == vecino_id)
                .values(**update_data)
            )

            await self.db.commit()
            return await self.get_vecino_by_id(vecino_id)

        except IntegrityError as e:
            await self.db.rollback()
            if "email" in str(e).lower():
                raise ValueError("Error: El email ya está en uso")
            raise ValueError(f"Error de integridad: {str(e)}")

        except Exception as e:
            await self.db.rollback()
            raise ValueError(f"Error al actualizar vecino: {str(e)}")

    async def change_password(
        self, user_id: int, current_password: str, new_password: str
    ) -> bool:
        """
        Cambia la contraseña de un usuario.

        Args:
            user_id: ID del usuario
            current_password: Contraseña actual
            new_password: Nueva contraseña

        Returns:
            True si se actualizó correctamente

        Raises:
            ValueError: Si la contraseña actual es incorrecta o hay errores de validación
        """
        from src.core.security import verify_password, hash_password, validate_password_strength

        # Obtener usuario
        usuario = await self.get_user_by_id(user_id)
        if not usuario:
            raise ValueError("Usuario no encontrado")

        # Verificar contraseña actual
        if not verify_password(current_password, usuario.pass_hash):
            raise ValueError("La contraseña actual es incorrecta")

        # Validar nueva contraseña
        is_valid, error_msg = validate_password_strength(new_password)
        if not is_valid:
            raise ValueError(f"Contraseña inválida: {error_msg}")

        # Verificar que la nueva contraseña sea diferente
        if verify_password(new_password, usuario.pass_hash):
            raise ValueError("La nueva contraseña debe ser diferente a la actual")

        try:
            # Actualizar contraseña
            new_hash = hash_password(new_password)
            await self.db.execute(
                update(Usuario)
                .where(Usuario.id_usuario == user_id)
                .values(pass_hash=new_hash)
            )
            await self.db.commit()
            return True

        except Exception as e:
            await self.db.rollback()
            raise ValueError(f"Error al cambiar contraseña: {str(e)}")
