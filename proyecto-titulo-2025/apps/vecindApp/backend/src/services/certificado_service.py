"""
Servicio para manejo de certificados de residencia.
"""

import logging
from datetime import datetime
from typing import Optional, Tuple
from decimal import Decimal
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
from src.services.payment_service import PaymentService
from src.schemas.payment_schemas import PaymentIntentResponse

logger = logging.getLogger(__name__)


class CertificadoService:
    """Servicio para gestión de certificados de residencia."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.pdf_generator = CertificadoPDFGenerator()
        # No inicializar PaymentService aquí para evitar conflictos de sesión
        
    # Configuración de precios (en CLP)
    PRECIO_CERTIFICADO = Decimal("2000")  # $2.000 CLP
    
    async def crear_certificado_con_pago(
        self, 
        user_id: int, 
        motivo_solicitud: str
    ) -> Tuple[CertificadoPedidoResponse, PaymentIntentResponse]:
        """
        Crea un certificado pendiente de pago y genera la intención de pago.
        
        Args:
            user_id: ID del usuario solicitante
            motivo_solicitud: Motivo de la solicitud
            
        Returns:
            Tupla (CertificadoPedido, PaymentIntent)
            
        Raises:
            ValueError: Si hay errores en la creación
        """
        try:
            # 1. Obtener datos del vecino para la descripción
            result = await self.db.execute(
                select(Vecino).where(Vecino.id_usuario == user_id)
            )
            vecino = result.scalar_one_or_none()
            if not vecino:
                raise ValueError("No se encontró perfil de vecino asociado")
            
            # 2. Crear pedido de certificado (estado: pendiente_pago)
            pedido = await self.crear_pedido_certificado(user_id, motivo_solicitud, estado_inicial="pendiente_pago", valor_certificado=self.PRECIO_CERTIFICADO)
            
            # 3. Crear intención de pago
            payment_intent = await self.payment_service.create_payment_intent(
                user_id=user_id,
                entity_type="certificado",
                entity_id=pedido.id_pedido,
                amount=pedido.valor_certificado,
                description=f"Certificado de residencia - {vecino.nombres} {vecino.apellido_paterno}",
                extra_data={
                    "certificado_pedido_id": pedido.id_pedido,
                    "motivo_solicitud": motivo_solicitud,
                    "vecino_rut": vecino.rut
                }
            )
            
            logger.info(f"📄💳 Certificado con pago creado: pedido={pedido.id_pedido}, payment={payment_intent.id_payment_intent}")
            
            return pedido, payment_intent
            
        except Exception as e:
            logger.error(f"💥 Error creando certificado con pago: {str(e)}")
            raise ValueError(f"Error creando certificado con pago: {str(e)}")

    async def crear_certificado_con_webpay(
        self, 
        user_id: int, 
        id_motivo: int
    ) -> Tuple[CertificadoPedidoResponse, PaymentIntentResponse, str, str]:
        """
        Crea un certificado pendiente de pago y genera la intención de pago con Webpay.
        
        Args:
            user_id: ID del usuario solicitante
            id_motivo: ID del motivo de solicitud
            
        Returns:
            Tupla (CertificadoPedido, PaymentIntent, webpay_url, webpay_token)
            
        Raises:
            ValueError: Si hay errores en la creación
        """
        try:
            # 1. Obtener datos del vecino para la descripción
            result = await self.db.execute(
                select(Vecino).where(Vecino.id_usuario == user_id)
            )
            vecino = result.scalar_one_or_none()
            if not vecino:
                raise ValueError("No se encontró perfil de vecino asociado")
            
            # 2. Crear pedido de certificado (estado: pendiente_pago) - sin commit
            pedido = await self.crear_pedido_certificado(user_id, id_motivo, estado_inicial="pendiente_pago", valor_certificado=self.PRECIO_CERTIFICADO, hacer_commit=False)
            
            # 3. Crear intención de pago con Webpay usando una nueva sesión
            from src.database.session import get_transaction_session
            async with get_transaction_session() as payment_db:
                payment_service = PaymentService(payment_db)
                payment_intent, webpay_url, webpay_token = await payment_service.create_webpay_payment_intent(
                    user_id=user_id,
                    entity_type="certificado",
                    entity_id=pedido.id_pedido,
                    amount=pedido.valor_certificado,
                    description=f"Certificado de residencia - {vecino.nombres} {vecino.apellido_paterno}",
                    extra_data={
                        "certificado_pedido_id": pedido.id_pedido,
                        "id_motivo": id_motivo,
                        "vecino_rut": vecino.rut
                    }
                )
            
            # 4. Hacer commit de la transacción principal
            await self.db.commit()
            
            logger.info(f"📄💳 Certificado con Webpay creado: pedido={pedido.id_pedido}, payment={payment_intent.id_payment_intent}")
            
            return pedido, payment_intent, webpay_url, webpay_token
            
        except Exception as e:
            logger.error(f"💥 Error creando certificado con Webpay: {str(e)}")
            raise ValueError(f"Error creando certificado con Webpay: {str(e)}")
    
    async def liberar_certificado_por_pago(self, certificado_pedido_id: int) -> CertificadoResponse:
        """
        Libera (genera el PDF) un certificado después de un pago exitoso.
        
        Este método es llamado por el webhook service cuando se confirma un pago.
        
        Args:
            certificado_pedido_id: ID del pedido de certificado
            
        Returns:
            CertificadoResponse con el certificado generado
            
        Raises:
            ValueError: Si no se puede generar el certificado
        """
        try:
            # 1. Obtener el pedido de certificado
            result = await self.db.execute(
                select(CertificadoPedido)
                .options(
                    selectinload(CertificadoPedido.vecino).selectinload(Vecino.comuna).selectinload(Comuna.region),
                    selectinload(CertificadoPedido.junta)
                )
                .where(CertificadoPedido.id_pedido == certificado_pedido_id)
            )
            
            pedido = result.scalar_one_or_none()
            if not pedido:
                raise ValueError(f"No se encontró pedido de certificado con ID {certificado_pedido_id}")
            
            # 2. Verificar que está en estado correcto
            if pedido.estado != "pendiente_pago":
                logger.warning(f"⚠️ Certificado {certificado_pedido_id} no está pendiente de pago (estado: {pedido.estado})")
                # Si ya está emitido, retornar el certificado existente
                if pedido.estado == "emitido":
                    existing_cert = await self._get_certificado_by_pedido_id(certificado_pedido_id)
                    if existing_cert:
                        return CertificadoResponse(
                            id_certificado=existing_cert.id_certificado,
                            numero=existing_cert.numero,
                            fecha_emision=existing_cert.fecha_emision,
                            direccion=existing_cert.direccion,
                            comuna=existing_cert.comuna,
                            region=existing_cert.region,
                            pdf_url=existing_cert.pdf_url
                        )
            
            # 3. Generar certificado (similar al método original pero sin verificar pago)
            numero_certificado = await self._generar_numero_certificado(pedido.id_junta)
            
            # 4. Preparar datos para el PDF
            datos_pdf = {
                'numero': numero_certificado,
                'fecha_emision': datetime.now(),
                'nombres': pedido.vecino.nombres,
                'apellido_paterno': pedido.vecino.apellido_paterno,
                'apellido_materno': pedido.vecino.apellido_materno,
                'rut': pedido.vecino.rut,
                'direccion': pedido.vecino.direccion,
                'comuna': pedido.vecino.comuna.nombre if pedido.vecino.comuna else None,
                'region': (
                    pedido.vecino.comuna.region.nombre 
                    if pedido.vecino.comuna and pedido.vecino.comuna.region 
                    else None
                ),
                'junta': pedido.junta.nombre if pedido.junta else None,
                'motivo_solicitud': pedido.motivo_solicitud
            }
            
            # 5. Generar PDF
            pdf_base64 = self.pdf_generator.generar_certificado_base64(datos_pdf)
            pdf_url = f"data:application/pdf;base64,{pdf_base64}"
            
            # 6. Crear certificado
            nuevo_certificado = Certificado(
                id_junta=pedido.id_junta,
                id_pedido=pedido.id_pedido,
                numero=numero_certificado,
                direccion=pedido.vecino.direccion,
                comuna=pedido.vecino.comuna.nombre if pedido.vecino.comuna else None,
                region=(
                    pedido.vecino.comuna.region.nombre 
                    if pedido.vecino.comuna and pedido.vecino.comuna.region 
                    else None
                ),
                pdf_url=pdf_url
            )
            
            # 7. Actualizar estado del pedido
            pedido.estado = "emitido"
            
            # 8. Guardar en base de datos
            self.db.add(nuevo_certificado)
            await self.db.commit()
            await self.db.refresh(nuevo_certificado)
            
            logger.info(f"📄✅ Certificado liberado por pago: {numero_certificado}")
            
            # 9. Retornar respuesta directamente sin llamar a método async
            return CertificadoResponse(
                id_certificado=nuevo_certificado.id_certificado,
                numero=nuevo_certificado.numero,
                fecha_emision=nuevo_certificado.fecha_emision,
                direccion=nuevo_certificado.direccion,
                comuna=nuevo_certificado.comuna,
                region=nuevo_certificado.region,
                pdf_url=nuevo_certificado.pdf_url
            )
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"💥 Error liberando certificado por pago: {str(e)}")
            raise ValueError(f"Error liberando certificado: {str(e)}")
    
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
    
    async def crear_pedido_certificado(self, user_id: int, id_motivo: int, estado_inicial: str = "iniciado", valor_certificado: Optional[Decimal] = None, hacer_commit: bool = True) -> CertificadoPedidoResponse:
        """
        Crea una nueva solicitud de certificado.
        
        Args:
            user_id: ID del usuario autenticado
            id_motivo: ID del motivo de solicitud
            estado_inicial: Estado inicial del pedido
            valor_certificado: Valor del certificado (opcional, usa valor por defecto si no se especifica)
            hacer_commit: Si hacer commit de la transacción (por defecto True)
            
        Returns:
            CertificadoPedidoResponse con los datos del pedido creado
            
        Raises:
            ValueError: Si faltan datos del vecino o junta
        """
        # Se permite crear múltiples solicitudes de certificado
        
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
        
        # Usar valor proporcionado o valor por defecto
        valor_final = valor_certificado if valor_certificado is not None else self.PRECIO_CERTIFICADO
        
        # Obtener ID del estado
        from src.database.models.estado_certificado import EstadoCertificado
        estado_result = await self.db.execute(
            select(EstadoCertificado).where(EstadoCertificado.nombre_estado == estado_inicial)
        )
        estado_obj = estado_result.scalar_one_or_none()
        if not estado_obj:
            raise ValueError(f"Estado '{estado_inicial}' no encontrado")
        
        # Crear nuevo pedido
        nuevo_pedido = CertificadoPedido(
            id_junta=vecino.junta.id_junta,
            id_vecino=vecino.id_vecino,
            creado_por=user_id,
            id_estado=estado_obj.id_estado,
            id_motivo=id_motivo,
            valor_certificado=valor_final
        )
        
        self.db.add(nuevo_pedido)
        if hacer_commit:
            await self.db.commit()
            await self.db.refresh(nuevo_pedido)
        else:
            await self.db.flush()  # Solo flush para obtener el ID
        
        logger.info(f"✅ Pedido de certificado creado: ID {nuevo_pedido.id_pedido}")
        
        # Obtener datos del motivo
        from src.database.models.motivo_solicitud import MotivoSolicitud
        motivo_result = await self.db.execute(
            select(MotivoSolicitud).where(MotivoSolicitud.id_motivo == id_motivo)
        )
        motivo_obj = motivo_result.scalar_one_or_none()
        
        return CertificadoPedidoResponse(
            id_pedido=nuevo_pedido.id_pedido,
            id_estado=nuevo_pedido.id_estado,
            estado=estado_obj.nombre_estado,
            created_at=nuevo_pedido.created_at,
            valor_certificado=nuevo_pedido.valor_certificado,
            vecino_nombres=vecino.nombres,
            vecino_apellidos=f"{vecino.apellido_paterno} {vecino.apellido_materno}",
            vecino_rut=vecino.rut,
            vecino_direccion=vecino.direccion,
            comuna=vecino.comuna.nombre if vecino.comuna else None,
            region=vecino.comuna.region.nombre if vecino.comuna and vecino.comuna.region else None,
            junta=vecino.junta.nombre if vecino.junta else None,
            id_motivo=nuevo_pedido.id_motivo,
            motivo_solicitud=motivo_obj.motivo if motivo_obj else "Motivo no encontrado",
            motivo_grupo=motivo_obj.grupo if motivo_obj else None
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
            ValueError: Si no existe solicitud de certificado
        """
        # Buscar el pedido más reciente del usuario
        result = await self.db.execute(
            select(CertificadoPedido)
            .options(
                selectinload(CertificadoPedido.vecino)
                .selectinload(Vecino.comuna)
                .selectinload(Comuna.region),
                selectinload(CertificadoPedido.junta)
            )
            .join(Vecino)
            .where(Vecino.id_usuario == user_id)
            .order_by(CertificadoPedido.created_at.desc())
        )
        pedido = result.scalars().first()
        
        if not pedido:
            raise ValueError("No se encontró solicitud de certificado")
        
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
    
    async def _get_certificado_by_pedido_id(self, pedido_id: int) -> Optional[Certificado]:
        """Obtiene un certificado por ID de pedido."""
        result = await self.db.execute(
            select(Certificado).where(Certificado.id_pedido == pedido_id)
        )
        return result.scalar_one_or_none()
    
    async def _certificado_to_response(self, certificado: Certificado) -> CertificadoResponse:
        """Convierte un modelo Certificado a CertificadoResponse."""
        return CertificadoResponse(
            id_certificado=certificado.id_certificado,
            numero=certificado.numero,
            fecha_emision=certificado.fecha_emision,
            direccion=certificado.direccion,
            comuna=certificado.comuna,
            region=certificado.region,
            pdf_url=certificado.pdf_url
        )
    
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

    async def descargar_certificado(self, certificado_id: int, user_id: int) -> Tuple[bytes, str]:
        """
        Descarga un certificado en formato PDF.
        
        Args:
            certificado_id: ID del certificado a descargar
            user_id: ID del usuario que solicita la descarga
            
        Returns:
            Tupla (pdf_data, filename)
            
        Raises:
            ValueError: Si el certificado no existe o no pertenece al usuario
        """
        # Verificar que el certificado existe y pertenece al usuario
        result = await self.db.execute(
            select(Certificado)
            .join(CertificadoPedido)
            .join(Vecino)
            .where(
                Certificado.id_certificado == certificado_id,
                Vecino.id_usuario == user_id
            )
        )
        certificado = result.scalar_one_or_none()
        
        if not certificado:
            raise ValueError("Certificado no encontrado o no tienes permisos para descargarlo")
        
        # Decodificar el PDF desde base64 (Data URL)
        try:
            import base64
            
            # Verificar que es un Data URL
            if not certificado.pdf_url.startswith('data:application/pdf;base64,'):
                raise ValueError("Formato de PDF no válido")
            
            # Extraer el base64 del Data URL
            base64_data = certificado.pdf_url.split(',')[1]
            
            # Decodificar base64 a bytes
            pdf_data = base64.b64decode(base64_data)
            
            filename = f"certificado_{certificado.numero}.pdf"
            logger.info(f"📄 Certificado {certificado_id} descargado por usuario {user_id}")
            
            return pdf_data, filename
            
        except Exception as e:
            logger.error(f"💥 Error decodificando PDF: {str(e)}")
            raise ValueError(f"Error al procesar el certificado: {str(e)}")
