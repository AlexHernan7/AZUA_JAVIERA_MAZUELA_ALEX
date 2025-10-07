"""
Modelos SQLAlchemy para VecindApp.

Este módulo contiene todos los modelos de base de datos de la aplicación.
"""

# Importar modelos en orden de dependencias (sin dependencias circulares)
# Tablas maestras primero
from .region import Region
from .comuna import Comuna
from .rol import Rol
from .estado_certificado import EstadoCertificado
from .motivo_solicitud import MotivoSolicitud
from .tipo_espacio import TipoEspacio
from .estado_reserva import EstadoReserva
# Modelos principales
from .junta import Junta
from .usuario import Usuario
from .usuario_rol import UsuarioRol
from .vecino import Vecino
from .directiva import Directiva
from .espacio import Espacio
from .reserva import Reserva
from .certificado import Certificado
from .certificado_pedido import CertificadoPedido
# Modelos de pagos - nueva implementación limpia
from .payment_intent import PaymentIntent
from .payment_transaction import PaymentTransaction
from .webhook_event import WebhookEvent

__all__ = [
    "Region",
    "Comuna",
    "Rol",
    "EstadoCertificado",
    "MotivoSolicitud",
    "TipoEspacio",
    "EstadoReserva",
    "Junta",
    "Usuario",
    "UsuarioRol",
    "Vecino",
    "Directiva",
    "Espacio",
    "Reserva",
    "Certificado",
    "CertificadoPedido",
    "PaymentIntent",
    "PaymentTransaction",
    "WebhookEvent",
]
