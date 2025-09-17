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

    async def update_vecino_profile(
        self,
        vecino_id: int,
        email: Optional[str] = None,
        telefono: Optional[str] = None,
        foto_perfil: Optional[str] = None,
    ) -> Optional[Vecino]:
        """
        Actualiza email, teléfono y/o foto de perfil del vecino.

        Args:
            vecino_id: ID del vecino
            email: Nuevo email (opcional)
            telefono: Nuevo teléfono (opcional)
            foto_perfil: Nueva foto de perfil en base64 (opcional)

        Returns:
            Vecino actualizado o None si no existe
        """
        # Verificar que el vecino existe
        vecino = await self.get_vecino_by_id(vecino_id)
        if not vecino:
            return None

        update_data = {}

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
