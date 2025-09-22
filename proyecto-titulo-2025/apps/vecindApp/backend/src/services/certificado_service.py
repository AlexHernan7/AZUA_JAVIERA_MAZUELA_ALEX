"""
Servicio para manejo de certificados de residencia.
"""

import logging
from datetime import datetime
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from src.database.models.certificado import Certificado
from src.database.models.certificado_pedido import CertificadoPedido
from src.database.models.vecino import Vecino
from src.database.models.usuario import Usuario
from src.database.models.junta import Junta
from src.database.models.comuna import Comuna
from src.schemas.certificado_schemas import (
    CertificadoConfirmacionData,
    CertificadoPedidoResponse,
    CertificadoResponse
)
from src.utils.pdf_generator import CertificadoPDFGenerator

logger = logging.getLogger(__name__)


class CertificadoService:
    """Servicio para gestión de certificados de residencia."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.pdf_generator = CertificadoPDFGenerator()
    
    async def get_datos_confirmacion(self, user_id: int) -> CertificadoConfirmacionData:
        """
        Obtiene los datos del vecino para confirmación antes de generar certificado.
        
        Args:
            user_id: ID del usuario autenticado
            
        Returns:
            CertificadoConfirmacionData con los datos del vecino
            
        Raises:
            ValueError: Si no se encuentra el vecino o faltan datos
        """
        # Obtener datos completos del vecino
        result = await self.db.execute(
            select(Vecino)
            .options(
                selectinload(Vecino.usuario),
                selectinload(Vecino.junta),
                selectinload(Vecino.comuna).selectinload(Comuna.region)
            )
            .where(Vecino.id_usuario == user_id)
        )
        vecino = result.scalar_one_or_none()
        
        if not vecino:
            raise ValueError("No se encontró perfil de vecino asociado")
        
        if not vecino.junta:
            raise ValueError("El vecino debe estar asociado a una junta de vecinos")
        
        return CertificadoConfirmacionData(
            nombres=vecino.nombres,
            apellido_paterno=vecino.apellido_paterno,
            apellido_materno=vecino.apellido_materno,
            rut=vecino.rut,
            direccion=vecino.direccion,
            comuna=vecino.comuna.nombre if vecino.comuna else None,
            region=vecino.comuna.region.nombre if vecino.comuna and vecino.comuna.region else None,
            junta=vecino.junta.nombre if vecino.junta else None
        )
    
    async def crear_pedido_certificado(self, user_id: int, motivo_solicitud: str) -> CertificadoPedidoResponse:
        """
        Crea una nueva solicitud de certificado.
        
        Args:
            user_id: ID del usuario autenticado
            
        Returns:
            CertificadoPedidoResponse con los datos del pedido creado
            
        Raises:
            ValueError: Si ya existe un pedido pendiente o faltan datos
        """
        # Verificar que no exista un pedido pendiente
        result = await self.db.execute(
            select(CertificadoPedido)
            .join(Vecino)
            .where(
                Vecino.id_usuario == user_id,
                CertificadoPedido.estado.in_(["iniciado", "pagado"])
            )
        )
        pedido_existente = result.scalar_one_or_none()
        
        if pedido_existente:
            raise ValueError(f"Ya existe una solicitud de certificado en estado: {pedido_existente.estado}")
        
        # Obtener datos del vecino
        result = await self.db.execute(
            select(Vecino)
            .options(
                selectinload(Vecino.junta),
                selectinload(Vecino.comuna).selectinload(Comuna.region)
            )
            .where(Vecino.id_usuario == user_id)
        )
        vecino = result.scalar_one_or_none()
        
        if not vecino:
            raise ValueError("No se encontró perfil de vecino asociado")
        
        if not vecino.junta:
            raise ValueError("El vecino debe estar asociado a una junta de vecinos")
        
        # Crear nuevo pedido
        nuevo_pedido = CertificadoPedido(
            id_junta=vecino.junta.id_junta,
            id_vecino=vecino.id_vecino,
            creado_por=user_id,
            estado="iniciado",
            motivo_solicitud=motivo_solicitud
        )
        
        self.db.add(nuevo_pedido)
        await self.db.commit()
        await self.db.refresh(nuevo_pedido)
        
        logger.info(f"✅ Pedido de certificado creado: ID {nuevo_pedido.id_pedido}")
        
        return CertificadoPedidoResponse(
            id_pedido=nuevo_pedido.id_pedido,
            estado=nuevo_pedido.estado,
            created_at=nuevo_pedido.created_at,
            vecino_nombres=vecino.nombres,
            vecino_apellidos=f"{vecino.apellido_paterno} {vecino.apellido_materno}",
            vecino_rut=vecino.rut,
            vecino_direccion=vecino.direccion,
            comuna=vecino.comuna.nombre if vecino.comuna else None,
            region=vecino.comuna.region.nombre if vecino.comuna and vecino.comuna.region else None,
            junta=vecino.junta.nombre if vecino.junta else None,
            motivo_solicitud=nuevo_pedido.motivo_solicitud
        )
    
    async def generar_certificado(
        self, 
        user_id: int, 
        motivo_solicitud: str,
        direccion_actualizada: Optional[str] = None
    ) -> CertificadoResponse:
        """
        Genera el certificado de residencia para un pedido confirmado.
        
        Args:
            user_id: ID del usuario autenticado
            direccion_actualizada: Dirección actualizada si es diferente a la registrada
            
        Returns:
            CertificadoResponse con los datos del certificado generado
            
        Raises:
            ValueError: Si no existe pedido válido o ya existe certificado
        """
        # Buscar pedido pendiente
        result = await self.db.execute(
            select(CertificadoPedido)
            .options(
                selectinload(CertificadoPedido.vecino)
                .selectinload(Vecino.comuna)
                .selectinload(Comuna.region),
                selectinload(CertificadoPedido.junta)
            )
            .join(Vecino)
            .where(
                Vecino.id_usuario == user_id,
                CertificadoPedido.estado == "iniciado"  # Por ahora omitimos "pagado"
            )
        )
        pedido = result.scalar_one_or_none()
        
        if not pedido:
            raise ValueError("No se encontró solicitud de certificado pendiente")
        
        # Verificar que no exista ya un certificado para este pedido
        result = await self.db.execute(
            select(Certificado).where(Certificado.id_pedido == pedido.id_pedido)
        )
        certificado_existente = result.scalar_one_or_none()
        
        if certificado_existente:
            raise ValueError("Ya existe un certificado generado para esta solicitud")
        
        # Generar número de certificado único
        numero_certificado = await self._generar_numero_certificado(pedido.id_junta)
        
        # Usar dirección actualizada o la del vecino
        direccion_final = direccion_actualizada or pedido.vecino.direccion
        
        # Preparar datos para el PDF
        datos_pdf = {
            'numero': numero_certificado,
            'fecha_emision': datetime.now(),
            'nombres': pedido.vecino.nombres,
            'apellido_paterno': pedido.vecino.apellido_paterno,
            'apellido_materno': pedido.vecino.apellido_materno,
            'rut': pedido.vecino.rut,
            'direccion': direccion_final,
            'comuna': pedido.vecino.comuna.nombre if pedido.vecino.comuna else None,
            'region': (
                pedido.vecino.comuna.region.nombre 
                if pedido.vecino.comuna and pedido.vecino.comuna.region 
                else None
            ),
            'junta': pedido.junta.nombre if pedido.junta else None,
            'motivo_solicitud': motivo_solicitud
        }
        
        # Generar PDF y guardarlo como base64 (por ahora)
        pdf_base64 = self.pdf_generator.generar_certificado_base64(datos_pdf)
        pdf_url = f"data:application/pdf;base64,{pdf_base64}"
        
        # Crear certificado
        nuevo_certificado = Certificado(
            id_junta=pedido.id_junta,
            id_pedido=pedido.id_pedido,
            numero=numero_certificado,
            direccion=direccion_final,
            comuna=pedido.vecino.comuna.nombre if pedido.vecino.comuna else None,
            region=(
                pedido.vecino.comuna.region.nombre 
                if pedido.vecino.comuna and pedido.vecino.comuna.region 
                else None
            ),
            pdf_url=pdf_url
        )
        
        # Actualizar estado del pedido
        pedido.estado = "emitido"
        
        self.db.add(nuevo_certificado)
        await self.db.commit()
        await self.db.refresh(nuevo_certificado)
        
        logger.info(f"✅ Certificado generado: {numero_certificado}")
        
        return CertificadoResponse(
            id_certificado=nuevo_certificado.id_certificado,
            numero=nuevo_certificado.numero,
            fecha_emision=nuevo_certificado.fecha_emision,
            direccion=nuevo_certificado.direccion,
            comuna=nuevo_certificado.comuna,
            region=nuevo_certificado.region,
            pdf_url=nuevo_certificado.pdf_url
        )
    
    async def _generar_numero_certificado(self, id_junta: int) -> str:
        """
        Genera un número único de certificado para la junta.
        
        Args:
            id_junta: ID de la junta de vecinos
            
        Returns:
            Número de certificado único
        """
        # Obtener el último número de certificado para esta junta
        result = await self.db.execute(
            select(func.count(Certificado.id_certificado))
            .where(Certificado.id_junta == id_junta)
        )
        count = result.scalar() or 0
        
        # Generar número correlativo
        year = datetime.now().year
        numero = f"CERT-{id_junta}-{year}-{count + 1:04d}"
        
        return numero
    
    async def obtener_certificados_usuario(self, user_id: int) -> list[CertificadoResponse]:
        """
        Obtiene todos los certificados emitidos para un usuario.
        
        Args:
            user_id: ID del usuario autenticado
            
        Returns:
            Lista de certificados del usuario
        """
        result = await self.db.execute(
            select(Certificado)
            .join(CertificadoPedido)
            .join(Vecino)
            .where(Vecino.id_usuario == user_id)
            .order_by(Certificado.fecha_emision.desc())
        )
        certificados = result.scalars().all()
        
        return [
            CertificadoResponse(
                id_certificado=cert.id_certificado,
                numero=cert.numero,
                fecha_emision=cert.fecha_emision,
                direccion=cert.direccion,
                comuna=cert.comuna,
                region=cert.region,
                pdf_url=cert.pdf_url
            )
            for cert in certificados
        ]
