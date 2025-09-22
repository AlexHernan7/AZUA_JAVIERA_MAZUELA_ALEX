"""
Generador de PDFs para certificados de residencia.
"""

import logging
from datetime import datetime
from typing import Dict, Any
import tempfile
import base64
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT

logger = logging.getLogger(__name__)


class CertificadoPDFGenerator:
    """Generador de PDFs para certificados de residencia."""
    
    def __init__(self):
        # Configurar estilos para ReportLab
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def generar_certificado_pdf(self, datos_certificado: Dict[str, Any]) -> bytes:
        """
        Genera un PDF del certificado de residencia.
        
        Args:
            datos_certificado: Diccionario con los datos del certificado
            
        Returns:
            bytes: Contenido del PDF generado
        """
        try:
            # Preparar datos para el PDF
            context = self._preparar_contexto(datos_certificado)
            
            # Generar PDF con ReportLab
            pdf_bytes = self._generar_pdf_reportlab(context)
            
            logger.info(f"✅ PDF generado exitosamente para certificado {datos_certificado.get('numero', 'N/A')}")
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"❌ Error generando PDF: {str(e)}")
            raise
    
    def _preparar_contexto(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepara el contexto de datos para el template.
        
        Args:
            datos: Datos del certificado
            
        Returns:
            Contexto preparado para el template
        """
        # Formatear fecha de emisión
        fecha_emision = datos.get('fecha_emision')
        if isinstance(fecha_emision, datetime):
            fecha_formateada = fecha_emision.strftime("%d de %B de %Y")
        else:
            fecha_formateada = datetime.now().strftime("%d de %B de %Y")
        
        # Formatear nombre completo
        nombres = datos.get('nombres', '')
        apellido_paterno = datos.get('apellido_paterno', '')
        apellido_materno = datos.get('apellido_materno', '')
        nombre_completo = f"{nombres} {apellido_paterno} {apellido_materno}".strip()
        
        return {
            'numero_certificado': datos.get('numero', 'N/A'),
            'fecha_emision': fecha_formateada,
            'nombre_completo': nombre_completo,
            'rut': datos.get('rut', 'N/A'),
            'direccion': datos.get('direccion', 'No especificada'),
            'comuna': datos.get('comuna', 'No especificada'),
            'region': datos.get('region', 'No especificada'),
            'junta': datos.get('junta', 'No especificada'),
            'motivo_solicitud': datos.get('motivo_solicitud', 'Fines que estime conveniente'),
            'fecha_actual': datetime.now().strftime("%d de %B de %Y"),
            'año_actual': datetime.now().year
        }
    
    def _setup_custom_styles(self):
        """Configura estilos personalizados para el PDF."""
        
        # Título principal
        self.styles.add(ParagraphStyle(
            name='CertificadoTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c5aa0'),
            alignment=TA_CENTER,
            spaceAfter=12,
            fontName='Helvetica-Bold'
        ))
        
        # Subtítulo
        self.styles.add(ParagraphStyle(
            name='CertificadoSubtitle',
            parent=self.styles['Normal'],
            fontSize=16,
            textColor=colors.grey,
            alignment=TA_CENTER,
            spaceAfter=20
        ))
        
        # Número de certificado
        self.styles.add(ParagraphStyle(
            name='CertificadoNumero',
            parent=self.styles['Normal'],
            fontSize=12,
            alignment=TA_RIGHT,
            spaceAfter=20,
            fontName='Helvetica-Bold'
        ))
        
        # Texto del cuerpo
        self.styles.add(ParagraphStyle(
            name='CertificadoBody',
            parent=self.styles['Normal'],
            fontSize=12,
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            leading=18
        ))
        
        # Datos del vecino
        self.styles.add(ParagraphStyle(
            name='DatosVecino',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            leftIndent=20
        ))
        
        # Firma
        self.styles.add(ParagraphStyle(
            name='Firma',
            parent=self.styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER,
            spaceAfter=6,
            fontName='Helvetica-Bold'
        ))
        
        # Fecha
        self.styles.add(ParagraphStyle(
            name='Fecha',
            parent=self.styles['Normal'],
            fontSize=11,
            alignment=TA_RIGHT,
            fontStyle='italic'
        ))
        
        # Encabezado de la junta
        self.styles.add(ParagraphStyle(
            name='JuntaHeader',
            parent=self.styles['Normal'],
            fontSize=14,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER,
            spaceAfter=6
        ))
        
        # Información de la junta
        self.styles.add(ParagraphStyle(
            name='JuntaInfo',
            parent=self.styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER,
            spaceAfter=3
        ))
    
    def _generar_pdf_reportlab(self, context: Dict[str, Any]) -> bytes:
        """
        Genera PDF usando ReportLab con formato oficial chileno.
        
        Args:
            context: Contexto con datos del certificado
            
        Returns:
            bytes: Contenido del PDF
        """
        # Crear buffer en memoria
        buffer = BytesIO()
        
        # Crear documento PDF
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Construir contenido
        story = []
        
        # Encabezado con información de la junta
        story.append(Paragraph(f'Junta de Vecinos "{context["junta"]}"', self.styles['JuntaHeader']))
        story.append(Paragraph(f"{context['comuna']}", self.styles['JuntaInfo']))
        story.append(Spacer(1, 1*cm))
        
        # Título y número del certificado
        titulo_tabla = Table([
            ["CERTIFICADO DE RESIDENCIA", f"N°{context['numero_certificado']}"]
        ], colWidths=[12*cm, 4*cm])
        titulo_tabla.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, 0), 16),
            ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (1, 0), (1, 0), 14),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(titulo_tabla)
        story.append(Spacer(1, 0.8*cm))
        
        # Texto principal del certificado - formato moderno en párrafo corrido
        texto_certificado = f'''
        La Junta de Vecinos "{context["junta"]}" de la comuna de {context['comuna']}, 
        Región {context['region']}, certifica que <b>{context['nombre_completo']}</b>, portador(a) de la 
        cédula de identidad N° <b>{context['rut']}</b>, es residente del sector bajo nuestra jurisdicción, 
         con domicilio actual en <b>{context['direccion'] or 'dirección registrada en nuestros archivos'}</b>.
        
        <br/><br/>
        
        La persona mencionada se encuentra debidamente inscrita en los registros de esta organización 
        territorial y mantiene su residencia habitual en el área de influencia de nuestra junta de vecinos.
        
        <br/><br/>
        
        Se extiende el presente certificado a solicitud del interesado para ser presentado ante 
        <b>{context['motivo_solicitud']}</b>, y para los fines que estime conveniente.
        '''
        
        story.append(Paragraph(texto_certificado, self.styles['CertificadoBody']))
        
        # Espaciado antes de las firmas
        story.append(Spacer(1, 1.5*cm))
        
        # Tabla para firmas
        firma_tabla = Table([
            ["_" * 30, "_" * 30],
            ["Presidente", "Secretario"]
        ], colWidths=[8*cm, 8*cm])
        firma_tabla.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, 1), 12),
            ('TOPPADDING', (0, 1), (-1, 1), 10),
        ]))
        story.append(firma_tabla)
        
        # Fecha y lugar con fecha actual
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph(
            f"Santiago, {context['comuna']}, {context['fecha_emision']}",
            self.styles['Fecha']
        ))
        
        # Generar PDF
        doc.build(story)
        
        # Obtener bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    def generar_certificado_base64(self, datos_certificado: Dict[str, Any]) -> str:
        """
        Genera un certificado PDF y lo retorna en base64.
        
        Args:
            datos_certificado: Datos del certificado
            
        Returns:
            str: PDF codificado en base64
        """
        pdf_bytes = self.generar_certificado_pdf(datos_certificado)
        return base64.b64encode(pdf_bytes).decode('utf-8')
    
    def guardar_certificado_temporal(self, datos_certificado: Dict[str, Any]) -> str:
        """
        Genera un certificado PDF y lo guarda en un archivo temporal.
        
        Args:
            datos_certificado: Datos del certificado
            
        Returns:
            str: Ruta del archivo temporal
        """
        pdf_bytes = self.generar_certificado_pdf(datos_certificado)
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(pdf_bytes)
            temp_path = temp_file.name
        
        logger.info(f"📄 Certificado guardado temporalmente en: {temp_path}")
        return temp_path
