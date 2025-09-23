"""
Servicio para gestión de juntas de vecinos.
"""

import logging
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
import base64

from src.database.models.junta import Junta
from src.database.models.comuna import Comuna
from src.database.models.region import Region
from src.schemas.junta_schemas import JuntaCreateRequest, JuntaCreateResponse, JuntaResponse, JuntaListResponse
from src.utils.image_utils import base64_to_binary

logger = logging.getLogger(__name__)


class JuntaService:
    """Servicio para operaciones con juntas de vecinos."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_junta(self, junta_data: JuntaCreateRequest) -> JuntaCreateResponse:
        """
        Crea una nueva junta de vecinos.
        
        Args:
            junta_data: Datos de la junta a crear
            
        Returns:
            Datos de la junta creada
            
        Raises:
            ValueError: Si hay errores de validación
            Exception: Si hay errores de base de datos
        """
        try:
            # Verificar que la comuna existe
            comuna_query = select(Comuna).options(selectinload(Comuna.region)).where(
                Comuna.id_comuna == junta_data.id_comuna
            )
            result = await self.db.execute(comuna_query)
            comuna = result.scalar_one_or_none()
            
            if not comuna:
                raise ValueError(f"Comuna con ID {junta_data.id_comuna} no encontrada")

            # Verificar que no existe otra junta con el mismo RUT
            existing_rut = await self.db.execute(
                select(Junta).where(Junta.rut == junta_data.rut)
            )
            if existing_rut.scalar_one_or_none():
                raise ValueError(f"Ya existe una junta con el RUT {junta_data.rut}")

            # Verificar que no existe otra junta con el mismo nombre en la misma comuna
            existing_name = await self.db.execute(
                select(Junta).where(
                    and_(
                        Junta.nombre == junta_data.nombre,
                        Junta.id_comuna == junta_data.id_comuna
                    )
                )
            )
            if existing_name.scalar_one_or_none():
                raise ValueError(f"Ya existe una junta con el nombre '{junta_data.nombre}' en esta comuna")

            # Procesar logo si existe
            logo_binary = None
            if junta_data.logo:
                try:
                    logo_binary = base64_to_binary(junta_data.logo)
                except Exception as e:
                    raise ValueError(f"Error procesando logo: {str(e)}")

            # Crear la nueva junta
            nueva_junta = Junta(
                nombre=junta_data.nombre,
                rut=junta_data.rut,
                email=junta_data.email,
                telefono=junta_data.telefono,
                direccion=junta_data.direccion,
                id_comuna=junta_data.id_comuna,
                fecha_constitucion=junta_data.fecha_constitucion,
                descripcion=junta_data.descripcion,
                activa=junta_data.activa,
                logo=logo_binary
            )

            self.db.add(nueva_junta)
            await self.db.commit()
            await self.db.refresh(nueva_junta)

            logger.info(f"✅ Junta creada exitosamente: {nueva_junta.nombre} (RUT: {nueva_junta.rut})")

            # Convertir logo a base64 si existe
            logo_base64 = None
            if nueva_junta.logo:
                try:
                    from src.utils.image_utils import binary_to_base64
                    logo_base64 = binary_to_base64(nueva_junta.logo, "image/png")
                except Exception as e:
                    logger.warning(f"Error convirtiendo logo a base64: {str(e)}")

            # Crear respuesta
            return JuntaCreateResponse(
                id_junta=nueva_junta.id_junta,
                nombre=nueva_junta.nombre,
                rut=nueva_junta.rut,
                email=nueva_junta.email,
                telefono=nueva_junta.telefono,
                direccion=nueva_junta.direccion,
                id_comuna=nueva_junta.id_comuna,
                comuna_nombre=comuna.nombre,
                region_nombre=comuna.region.nombre,
                fecha_constitucion=nueva_junta.fecha_constitucion,
                descripcion=nueva_junta.descripcion,
                activa=nueva_junta.activa,
                logo=logo_base64,
                created_at=nueva_junta.created_at
            )

        except ValueError:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"❌ Error creando junta: {str(e)}")
            raise Exception(f"Error interno al crear junta: {str(e)}")

    async def get_junta_by_id(self, junta_id: int) -> Optional[JuntaResponse]:
        """
        Obtiene una junta por su ID.
        
        Args:
            junta_id: ID de la junta
            
        Returns:
            Datos de la junta o None si no existe
        """
        try:
            query = select(Junta).options(
                selectinload(Junta.comuna).selectinload(Comuna.region)
            ).where(Junta.id_junta == junta_id)
            
            result = await self.db.execute(query)
            junta = result.scalar_one_or_none()
            
            if not junta:
                return None

            # Convertir logo a base64 si existe
            logo_base64 = None
            if junta.logo:
                try:
                    from src.utils.image_utils import binary_to_base64
                    logo_base64 = binary_to_base64(junta.logo, "image/png")
                except Exception as e:
                    logger.warning(f"Error convirtiendo logo a base64: {str(e)}")

            return JuntaResponse(
                id_junta=junta.id_junta,
                nombre=junta.nombre,
                rut=junta.rut,
                email=junta.email,
                telefono=junta.telefono,
                direccion=junta.direccion,
                id_comuna=junta.id_comuna,
                comuna_nombre=junta.comuna.nombre,
                region_nombre=junta.comuna.region.nombre,
                fecha_constitucion=junta.fecha_constitucion,
                descripcion=junta.descripcion,
                activa=junta.activa,
                logo=logo_base64,
                created_at=junta.created_at
            )

        except Exception as e:
            logger.error(f"❌ Error obteniendo junta {junta_id}: {str(e)}")
            raise Exception(f"Error interno al obtener junta: {str(e)}")

    async def list_juntas(
        self, 
        skip: int = 0, 
        limit: int = 50,
        activa_only: Optional[bool] = None,
        comuna_id: Optional[int] = None
    ) -> dict:
        """
        Lista las juntas con filtros opcionales.
        
        Args:
            skip: Número de registros a saltar
            limit: Número máximo de registros
            activa_only: Si True, solo juntas activas; si False, solo inactivas; si None, todas
            comuna_id: ID de comuna para filtrar
            
        Returns:
            Diccionario con lista de juntas y estadísticas
        """
        try:
            # Construir query base
            query = select(Junta).options(
                selectinload(Junta.comuna).selectinload(Comuna.region)
            )
            
            # Aplicar filtros
            conditions = []
            if activa_only is not None:
                conditions.append(Junta.activa == activa_only)
            if comuna_id is not None:
                conditions.append(Junta.id_comuna == comuna_id)
            
            if conditions:
                query = query.where(and_(*conditions))
            
            # Query para contar totales
            count_query = select(func.count(Junta.id_junta))
            if conditions:
                count_query = count_query.where(and_(*conditions))
            
            # Query para contar activas e inactivas
            activas_query = select(func.count(Junta.id_junta)).where(Junta.activa == True)
            inactivas_query = select(func.count(Junta.id_junta)).where(Junta.activa == False)
            
            if comuna_id is not None:
                activas_query = activas_query.where(Junta.id_comuna == comuna_id)
                inactivas_query = inactivas_query.where(Junta.id_comuna == comuna_id)
            
            # Ejecutar queries
            query = query.offset(skip).limit(limit).order_by(Junta.created_at.desc())
            
            result = await self.db.execute(query)
            juntas = result.scalars().all()
            
            total_result = await self.db.execute(count_query)
            total = total_result.scalar()
            
            activas_result = await self.db.execute(activas_query)
            activas = activas_result.scalar()
            
            inactivas_result = await self.db.execute(inactivas_query)
            inactivas = inactivas_result.scalar()

            # Convertir a response models
            juntas_response = []
            for junta in juntas:
                juntas_response.append(JuntaListResponse(
                    id_junta=junta.id_junta,
                    nombre=junta.nombre,
                    rut=junta.rut,
                    email=junta.email,
                    direccion=junta.direccion,
                    comuna_nombre=junta.comuna.nombre,
                    region_nombre=junta.comuna.region.nombre,
                    activa=junta.activa,
                    created_at=junta.created_at
                ))

            return {
                "juntas": juntas_response,
                "total": total,
                "activas": activas,
                "inactivas": inactivas
            }

        except Exception as e:
            logger.error(f"❌ Error listando juntas: {str(e)}")
            raise Exception(f"Error interno al listar juntas: {str(e)}")

    async def get_juntas_by_comuna(self, comuna_id: int) -> List[JuntaListResponse]:
        """
        Obtiene todas las juntas activas de una comuna específica.
        
        Args:
            comuna_id: ID de la comuna
            
        Returns:
            Lista de juntas de la comuna
        """
        try:
            query = select(Junta).options(
                selectinload(Junta.comuna).selectinload(Comuna.region)
            ).where(
                and_(
                    Junta.id_comuna == comuna_id,
                    Junta.activa == True
                )
            ).order_by(Junta.nombre)
            
            result = await self.db.execute(query)
            juntas = result.scalars().all()
            
            return [
                JuntaListResponse(
                    id_junta=junta.id_junta,
                    nombre=junta.nombre,
                    rut=junta.rut,
                    email=junta.email,
                    direccion=junta.direccion,
                    comuna_nombre=junta.comuna.nombre,
                    region_nombre=junta.comuna.region.nombre,
                    activa=junta.activa,
                    created_at=junta.created_at
                ) for junta in juntas
            ]

        except Exception as e:
            logger.error(f"❌ Error obteniendo juntas de comuna {comuna_id}: {str(e)}")
            raise Exception(f"Error interno al obtener juntas de comuna: {str(e)}")
