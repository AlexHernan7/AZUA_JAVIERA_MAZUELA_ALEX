"""
Schemas de validación para la API de VecindApp.

Los schemas definen la estructura de datos que acepta y devuelve la API.
"""

from .auth_schemas import *
from .user_schemas import *
from .reserva_schemas import *

__all__ = [
    "UsuarioRegistroRequest",
    "UsuarioRegistroResponse",
    "VecinoCreate",
    "VecinoResponse",
    "ErrorResponse",
    # Reservas
    "TipoEspacio",
    "EstadoReserva",
    "EspacioBase",
    "EspacioResponse",
    "ReservaCreate",
    "ReservaUpdate",
    "ReservaResponse",
    "ReservaListResponse",
    "DisponibilidadRequest",
    "DisponibilidadResponse",
]
