"""
Rutas relacionadas con usuarios y vecinos.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_db_session
from src.services.user_service import UserService
from src.schemas.auth_schemas import VecinoResponse

# Crear router para rutas de usuarios
router = APIRouter(prefix="/users", tags=["Usuarios"])


@router.get(
    "/vecino/{vecino_id}",
    response_model=VecinoResponse,
    summary="Obtener vecino por ID",
    description="Obtiene los datos de un vecino por su ID"
)
async def get_vecino(
    vecino_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Obtiene los datos de un vecino por su ID.
    
    Args:
        vecino_id: ID del vecino
        db: Sesión de base de datos
        
    Returns:
        Datos del vecino
        
    Raises:
        HTTPException: Si el vecino no existe
    """
    try:
        user_service = UserService(db)
        vecino = await user_service.get_vecino_by_id(vecino_id)
        
        if not vecino:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vecino no encontrado"
            )
        
        # Obtener el usuario asociado para el email
        usuario = await user_service.get_user_by_id(vecino.id_usuario)
        
        return VecinoResponse(
            id_vecino=vecino.id_vecino,
            nombres=vecino.nombres,
            apellidos=vecino.apellidos,
            email=usuario.email if usuario else "",
            telefono=vecino.telefono,
            direccion=vecino.direccion,
            fecha_nacimiento=vecino.fecha_nacimiento
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener vecino: {str(e)}"
        )
