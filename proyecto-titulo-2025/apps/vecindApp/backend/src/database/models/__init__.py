"""
Modelos SQLAlchemy para VecindApp.

Este módulo contiene todos los modelos de base de datos de la aplicación.
"""

# Importar modelos en orden de dependencias (sin dependencias circulares)
from .region import Region
from .comuna import Comuna
from .junta import Junta
from .rol import Rol
from .usuario import Usuario
from .usuario_rol import UsuarioRol
from .vecino import Vecino
from .espacio import Espacio
from .reserva import Reserva
from .certificado import Certificado
from .certificado_pedido import CertificadoPedido
from .transaccion import Transaccion
from .pago_externo import PagoExterno
from .detalle_transaccion import DetalleTransaccion

__all__ = [
    "Region",
    "Comuna",
    "Junta",
    "Rol",
    "Usuario",
    "UsuarioRol",
    "Vecino",
    "Espacio",
    "Reserva",
    "Certificado",
    "CertificadoPedido",
    "Transaccion",
    "PagoExterno",
    "DetalleTransaccion",
]
