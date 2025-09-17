"""
Módulo de base de datos para VecindApp.

Este módulo contiene la configuración base de SQLAlchemy y los modelos de la aplicación.
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData

# Create shared MetaData instance
metadata = MetaData()
Base = declarative_base(metadata=metadata)

# Importar todos los modelos para que estén disponibles
from src.database.models import *
from src.database.utils import DatabaseSetup

__all__ = [
    "Base",
    "DatabaseSetup",
    "Region",
    "Comuna",
    "Junta",
    "Rol",
    "Usuario",
    "UsuarioRol",
    "Vecino",
    "Espacio",
    "Reserva",
    "CertificadoPedido",
    "Certificado",
    "Transaccion",
    "PagoExterno",
    "DetalleTransaccion",
]
