"""
Generador de PDFs para certificados de residencia.
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any
from pathlib import Path
import tempfile
import base64
from io import BytesIO

from jinja2 import Environment, FileSystemLoader, select_autoescape
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
    
    def _generar_pdf_reportlab(self, context: Dict[str, Any]) -> bytes:
        """
        Genera PDF usando ReportLab.
        
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
        
        # Encabezado
        story.append(Paragraph("CERTIFICADO DE RESIDENCIA", self.styles['CertificadoTitle']))
        story.append(Paragraph(f"Junta de Vecinos {context['junta']}", self.styles['CertificadoSubtitle']))
        story.append(Spacer(1, 0.5*cm))
        
        # Número de certificado
        story.append(Paragraph(f"<b>Certificado N°: {context['numero_certificado']}</b>", self.styles['CertificadoNumero']))
        story.append(Spacer(1, 0.5*cm))
        
        # Cuerpo del certificado
        story.append(Paragraph(
            f"La Junta de Vecinos <b>{context['junta']}</b>, de la comuna de <b>{context['comuna']}</b>, "
            f"Región de <b>{context['region']}</b>, certifica que:",
            self.styles['CertificadoBody']
        ))
        
        story.append(Spacer(1, 0.5*cm))
        
        # Tabla con datos del vecino
        datos_vecino = [
            ['DATOS DEL VECINO', ''],
            ['Nombre completo:', context['nombre_completo']],
            ['RUT:', context['rut']],
            ['Dirección:', context['direccion']],
            ['Comuna:', context['comuna']],
            ['Región:', context['region']]
        ]
        
        tabla = Table(datos_vecino, colWidths=[4*cm, 10*cm])
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(tabla)
        story.append(Spacer(1, 0.5*cm))
        
        # Texto de certificación
        story.append(Paragraph(
            f"La persona antes mencionada <b>ES RESIDENTE</b> del sector bajo la jurisdicción "
            f"de esta Junta de Vecinos, según consta en nuestros registros actualizados.",
            self.styles['CertificadoBody']
        ))
        
        story.append(Paragraph(
            "Se extiende el presente certificado para los fines que el interesado estime conveniente.",
            self.styles['CertificadoBody']
        ))
        
        # Espaciado para firma
        story.append(Spacer(1, 2*cm))
        
        # Línea de firma
        story.append(Paragraph("_" * 50, self.styles['Firma']))
        story.append(Paragraph("Presidente(a) Junta de Vecinos", self.styles['Firma']))
        story.append(Paragraph(context['junta'], self.styles['Firma']))
        
        # Fecha
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph(f"{context['comuna']}, {context['fecha_emision']}", self.styles['Fecha']))
        
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
