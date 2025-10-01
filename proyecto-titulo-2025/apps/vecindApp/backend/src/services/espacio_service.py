"""
Servicio para manejo de espacios comunitarios.

Maneja la creación, actualización y consulta de espacios comunitarios.
"""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from typing import Optional, List, Dict, Any
from decimal import Decimal

from src.database.models.espacio import Espacio
from src.database.models.junta import Junta
from src.schemas.espacio_schemas import (
    EspacioCreateRequest,
    EspacioUpdateRequest,
    EspacioResponse,
    EspacioListResponse
)

logger = logging.getLogger(__name__)


class EspacioService:
    """
    Servicio para manejar espacios comunitarios.
    """

    def __init__(self, db: AsyncSession):
        """Inicializa el servicio con la sesión de base de datos."""
        self.db = db

    async def create_espacio(
        self, 
        espacio_data: EspacioCreateRequest,
        user_id: int
    ) -> EspacioResponse:
        """
        Crea un nuevo espacio comunitario.
        
        Args:
            espacio_data: Datos del espacio a crear
            user_id: ID del usuario que crea el espacio
            
        Returns:
            EspacioResponse: Datos del espacio creado
            
        Raises:
            ValueError: Si la junta no existe o el usuario no tiene permisos
            IntegrityError: Si hay conflicto de datos
        """
        try:
            # 1. Verificar que la junta existe
            junta = await self._get_junta_by_id(espacio_data.id_junta)
            if not junta:
                raise ValueError(f"Junta con ID {espacio_data.id_junta} no encontrada")

            # 2. Verificar que el usuario tiene permisos para crear espacios en esta junta
            # TODO: Implementar verificación de permisos basada en roles
            # Por ahora, asumimos que cualquier usuario autenticado puede crear espacios

            # 3. Crear el espacio
            nuevo_espacio = Espacio(
                id_junta=espacio_data.id_junta,
                nombre=espacio_data.nombre,
                tipo=espacio_data.tipo,
                capacidad=espacio_data.capacidad,
                valor=espacio_data.valor,
                foto=espacio_data.foto,
                permitido=espacio_data.permitido,
                no_permitido=espacio_data.no_permitido,
                max_horas=espacio_data.max_horas,
                activo=espacio_data.activo
            )

            self.db.add(nuevo_espacio)
            await self.db.commit()
            await self.db.refresh(nuevo_espacio)

            logger.info(f"Espacio '{nuevo_espacio.nombre}' creado exitosamente con ID {nuevo_espacio.id_espacio}")

            return EspacioResponse.from_orm(nuevo_espacio)

        except IntegrityError as e:
            await self.db.rollback()
            logger.error(f"Error de integridad al crear espacio: {e}")
            raise ValueError("Error al crear el espacio. Verifique que los datos sean válidos.")
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error inesperado al crear espacio: {e}")
            raise

    async def get_espacio_by_id(self, espacio_id: int) -> Optional[EspacioResponse]:
        """
        Obtiene un espacio por su ID.
        
        Args:
            espacio_id: ID del espacio
            
        Returns:
            EspacioResponse o None si no existe
        """
        result = await self.db.execute(
            select(Espacio).where(Espacio.id_espacio == espacio_id)
        )
        espacio = result.scalar_one_or_none()
        
        if espacio:
            return EspacioResponse.from_orm(espacio)
        return None

    async def get_espacios_by_junta(
        self, 
        id_junta: int, 
        activo_only: bool = True,
        pagina: int = 1,
        por_pagina: int = 10
    ) -> EspacioListResponse:
        """
        Obtiene todos los espacios de una junta.
        
        Args:
            id_junta: ID de la junta
            activo_only: Si solo mostrar espacios activos
            pagina: Número de página (1-indexed)
            por_pagina: Elementos por página
            
        Returns:
            EspacioListResponse: Lista paginada de espacios
        """
        # Construir query base
        query = select(Espacio).where(Espacio.id_junta == id_junta)
        
        if activo_only:
            query = query.where(Espacio.activo == True)
        
        # Contar total
        count_query = select(Espacio).where(Espacio.id_junta == id_junta)
        if activo_only:
            count_query = count_query.where(Espacio.activo == True)
        
        total_result = await self.db.execute(count_query)
        total = len(total_result.scalars().all())
        
        # Aplicar paginación
        offset = (pagina - 1) * por_pagina
        query = query.offset(offset).limit(por_pagina)
        
        # Ejecutar query
        result = await self.db.execute(query)
        espacios = result.scalars().all()
        
        # Convertir a response
        espacios_response = [EspacioResponse.from_orm(espacio) for espacio in espacios]
        
        return EspacioListResponse(
            espacios=espacios_response,
            total=total,
            pagina=pagina,
            por_pagina=por_pagina
        )

    async def update_espacio(
        self, 
        espacio_id: int, 
        espacio_data: EspacioUpdateRequest,
        user_id: int
    ) -> Optional[EspacioResponse]:
        """
        Actualiza un espacio existente.
        
        Args:
            espacio_id: ID del espacio a actualizar
            espacio_data: Datos a actualizar
            user_id: ID del usuario que actualiza
            
        Returns:
            EspacioResponse: Datos del espacio actualizado o None si no existe
            
        Raises:
            ValueError: Si el usuario no tiene permisos
        """
        try:
            # 1. Verificar que el espacio existe
            espacio = await self._get_espacio_by_id(espacio_id)
            if not espacio:
                return None

            # 2. Verificar permisos (TODO: implementar verificación de roles)
            
            # 3. Preparar datos para actualización
            update_data = {}
            for field, value in espacio_data.dict(exclude_unset=True).items():
                if value is not None:
                    update_data[field] = value

            if not update_data:
                # No hay nada que actualizar
                return EspacioResponse.from_orm(espacio)

            # 4. Actualizar
            await self.db.execute(
                update(Espacio)
                .where(Espacio.id_espacio == espacio_id)
                .values(**update_data)
            )
            await self.db.commit()

            # 5. Obtener el espacio actualizado
            updated_espacio = await self._get_espacio_by_id(espacio_id)
            logger.info(f"Espacio {espacio_id} actualizado exitosamente")

            return EspacioResponse.from_orm(updated_espacio)

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error al actualizar espacio {espacio_id}: {e}")
            raise

    async def delete_espacio(self, espacio_id: int, user_id: int) -> bool:
        """
        Elimina un espacio (soft delete - lo marca como inactivo).
        
        Args:
            espacio_id: ID del espacio a eliminar
            user_id: ID del usuario que elimina
            
        Returns:
            bool: True si se eliminó exitosamente
            
        Raises:
            ValueError: Si el usuario no tiene permisos
        """
        try:
            # 1. Verificar que el espacio existe
            espacio = await self._get_espacio_by_id(espacio_id)
            if not espacio:
                return False

            # 2. Verificar permisos (TODO: implementar verificación de roles)
            
            # 3. Soft delete - marcar como inactivo
            await self.db.execute(
                update(Espacio)
                .where(Espacio.id_espacio == espacio_id)
                .values(activo=False)
            )
            await self.db.commit()

            logger.info(f"Espacio {espacio_id} eliminado (marcado como inactivo)")
            return True

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error al eliminar espacio {espacio_id}: {e}")
            raise

    async def _get_espacio_by_id(self, espacio_id: int) -> Optional[Espacio]:
        """Obtiene un espacio por ID (método privado)."""
        result = await self.db.execute(
            select(Espacio).where(Espacio.id_espacio == espacio_id)
        )
        return result.scalar_one_or_none()

    async def _get_junta_by_id(self, junta_id: int) -> Optional[Junta]:
        """Obtiene una junta por ID (método privado)."""
        result = await self.db.execute(
            select(Junta).where(Junta.id_junta == junta_id)
        )
        return result.scalar_one_or_none()
