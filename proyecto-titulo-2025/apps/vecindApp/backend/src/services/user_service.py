"""
Servicio para manejo de usuarios y vecinos.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from src.database.models.usuario import Usuario
from src.database.models.vecino import Vecino


class UserService:
    """
    Servicio para operaciones relacionadas con usuarios y vecinos.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_by_id(self, user_id: int) -> Optional[Usuario]:
        """
        Obtiene un usuario por su ID.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Usuario si existe, None si no
        """
        result = await self.db.execute(
            select(Usuario).where(Usuario.id_usuario == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_vecino_by_user_id(self, user_id: int) -> Optional[Vecino]:
        """
        Obtiene el perfil de vecino asociado a un usuario.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Vecino si existe, None si no
        """
        result = await self.db.execute(
            select(Vecino).where(Vecino.id_usuario == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_vecino_by_id(self, vecino_id: int) -> Optional[Vecino]:
        """
        Obtiene un vecino por su ID.
        
        Args:
            vecino_id: ID del vecino
            
        Returns:
            Vecino si existe, None si no
        """
        result = await self.db.execute(
            select(Vecino).where(Vecino.id_vecino == vecino_id)
        )
        return result.scalar_one_or_none()
