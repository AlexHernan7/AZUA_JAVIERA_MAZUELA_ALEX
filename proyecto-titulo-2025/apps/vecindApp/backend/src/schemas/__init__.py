"""
Schemas de validación para la API de VecindApp.

Los schemas definen la estructura de datos que acepta y devuelve la API.
"""

from .auth_schemas import *
from .user_schemas import *

__all__ = [
    "UsuarioRegistroRequest",
    "UsuarioRegistroResponse", 
    "VecinoCreate",
    "VecinoResponse",
    "ErrorResponse"
]
