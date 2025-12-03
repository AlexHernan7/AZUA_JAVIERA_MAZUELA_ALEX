"""
Generador de PDFs para certificados de residencia (formato carta, igual al ejemplo).
"""

import logging
from datetime import datetime
from typing import Dict, Any
import tempfile
import base64
from io import BytesIO

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT

logger = logging.getLogger(__name__)


def _fecha_es(dt: datetime) -> str:
    """Devuelve fecha en español: '24 de Septiembre de 2025' (mes con mayúscula)."""
    meses = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]
    return f"{dt.day} de {meses[dt.month - 1]} de {dt.year}"


class CertificadoPDFGenerator:
    """Generador de PDFs para certificados de residencia."""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    # ---------- API PÚBLICA ----------
    def generar_certificado_pdf(self, datos_certificado: Dict[str, Any]) -> bytes:
        try:
            context = self._preparar_contexto(datos_certificado)
            return self._generar_pdf_reportlab(context)
        except Exception as e:
            logger.error(f"❌ Error generando PDF: {str(e)}")
            raise

    def generar_certificado_base64(self, datos_certificado: Dict[str, Any]) -> str:
        pdf_bytes = self.generar_certificado_pdf(datos_certificado)
        return base64.b64encode(pdf_bytes).decode("utf-8")

    def guardar_certificado_temporal(self, datos_certificado: Dict[str, Any]) -> str:
        pdf_bytes = self.generar_certificado_pdf(datos_certificado)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
            f.write(pdf_bytes)
            path = f.name
        logger.info(f"📄 Certificado guardado temporalmente en: {path}")
        return path

    # ---------- PREPARACIÓN ----------
    def _preparar_contexto(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        fecha_emision = datos.get("fecha_emision")
        if not isinstance(fecha_emision, datetime):
            fecha_emision = datetime.now()

        nombres = datos.get("nombres", "").strip()
        ap_pa = datos.get("apellido_paterno", "").strip()
        ap_ma = datos.get("apellido_materno", "").strip()
        nombre_completo = " ".join(x for x in [nombres, ap_pa, ap_ma] if x)

        # Procesar firma y timbre si existen (convertir de base64 a BytesIO para reportlab)
        firma_io = None
        timbre_io = None
        
        if datos.get("firma_presidente"):
            try:
                # Extraer base64 del data URL
                firma_base64 = datos["firma_presidente"]
                if "," in firma_base64:
                    firma_base64 = firma_base64.split(",", 1)[1]
                firma_bytes = base64.b64decode(firma_base64)
                firma_io = BytesIO(firma_bytes)
            except Exception as e:
                logger.warning(f"Error procesando firma: {str(e)}")
        
        if datos.get("timbre"):
            try:
                # Extraer base64 del data URL
                timbre_base64 = datos["timbre"]
                if "," in timbre_base64:
                    timbre_base64 = timbre_base64.split(",", 1)[1]
                timbre_bytes = base64.b64decode(timbre_base64)
                timbre_io = BytesIO(timbre_bytes)
            except Exception as e:
                logger.warning(f"Error procesando timbre: {str(e)}")

        # Preparar datos del presidente
        pres_nombres = datos.get("presidente_nombres", "").strip()
        pres_ap_pa = datos.get("presidente_apellido_paterno", "").strip()
        pres_ap_ma = datos.get("presidente_apellido_materno", "").strip()
        pres_nombre_completo = " ".join(x for x in [pres_nombres, pres_ap_pa, pres_ap_ma] if x)
        pres_rut = datos.get("presidente_rut", "").strip()
        
        return {
            "folio": datos.get("numero", "CERT-2-2025-0000"),
            "titulo": "CERTIFICADO DE RESIDENCIA",
            "junta": datos.get("junta", 'Junta de Vecinos Las Américas'),
            "comuna": datos.get("comuna", "Maipú"),
            "region": datos.get("region", "Región Metropolitana de Santiago"),
            "nombre_completo": nombre_completo or "NOMBRE APELLIDO",
            "rut": datos.get("rut", "00.000.000-0"),
            "direccion": datos.get("direccion", "Mi Casa #1234"),
            "motivo":
                datos.get("motivo_solicitud",
                          "Postulación a beneficios sociales (Registro Social de Hogares, subsidios habitacionales, bonos)"),
            "lugar_fecha": f"Santiago, {datos.get('comuna', 'Maipú')}, {_fecha_es(fecha_emision)}",
            "firma_io": firma_io,
            "timbre_io": timbre_io,
            "presidente_nombre_completo": pres_nombre_completo or "",
            "presidente_rut": pres_rut or "",
        }

    def _setup_custom_styles(self):
        """Estilos en NEGRO, márgenes y tamaños similares al ejemplo."""
        # Número arriba a la derecha
        self.styles.add(ParagraphStyle(
            name="NumeroFolio",
            parent=self.styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10,
            alignment=TA_RIGHT,
            textColor=colors.black,
            spaceAfter=2*cm, #despues
        ))
        # Título principal
        self.styles.add(ParagraphStyle(
            name="Titulo",
            parent=self.styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=18,
            alignment=TA_CENTER,
            textColor=colors.black,
            spaceAfter=1*cm,#despues
        ))
        # Nombre de la Junta
        self.styles.add(ParagraphStyle(
            name="JuntaBold",
            parent=self.styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=13,
            alignment=TA_CENTER,
            textColor=colors.black,
            spaceAfter=0.2*cm,#despues
        ))
        # Comuna bajo la junta
        self.styles.add(ParagraphStyle(
            name="Comuna",
            parent=self.styles["Normal"],
            fontSize=11.5,
            alignment=TA_CENTER,
            textColor=colors.black,
            spaceAfter=1.5*cm,   #despues
        ))
        # Cuerpo
        self.styles.add(ParagraphStyle(
            name="Cuerpo",
            parent=self.styles["Normal"],
            fontSize=11.5,
            alignment=TA_JUSTIFY,
            leading=17,
            textColor=colors.black,
            spaceAfter= 1*cm,#despues
        ))
        # Texto de firmas
        self.styles.add(ParagraphStyle(
            name="FirmaRol",
            parent=self.styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11.5,
            alignment=TA_CENTER,
            textColor=colors.black,
            spaceAfter= 2.5*cm#despues
        ))

                # Pie (lugar y fecha) centrado
        self.styles.add(ParagraphStyle(
            name="PieFecha",
            parent=self.styles["Normal"],
            fontSize=10.5,
            alignment=TA_CENTER,
            textColor=colors.black,
            
        ))

    # ---------- RENDER ----------
    def _generar_pdf_reportlab(self, c: Dict[str, Any]) -> bytes:
        buffer = BytesIO()

        # Documento tamaño CARTA y márgenes suaves como en el ejemplo
        doc = SimpleDocTemplate(
            buffer,
            pagesize=LETTER,
            leftMargin=2.2 * cm,
            rightMargin=2.2 * cm,
            topMargin=2.0 * cm,
            bottomMargin=1 * cm,
        )

        story = []

        # Número de certificado arriba a la derecha (N° + folio)
        story.append(Paragraph(f"N°{c['folio']}", self.styles["NumeroFolio"]))

        # Título centrado
        story.append(Paragraph(c["titulo"], self.styles["Titulo"]))

        # Bloque de Junta y Comuna
        story.append(Paragraph(f'Junta de Vecinos "{c["junta"]}"', self.styles["JuntaBold"]))
        story.append(Paragraph(c["comuna"], self.styles["Comuna"]))

        # Cuerpo (idéntico al texto del ejemplo)
        cuerpo = (
            f'La Junta de Vecinos "Junta de Vecinos Las Américas" de la comuna de {c["comuna"]}, '
            f'{c["region"]}, certifica que <b>{c["nombre_completo"]}</b>, '
            f'portador(a) de la cédula de identidad N° <b>{c["rut"]}</b>, es residente del sector bajo nuestra '
            f'jurisdicción, con domicilio actual en <b>{c["direccion"]}</b>.<br/><br/>'
            "La persona mencionada se encuentra debidamente inscrita en los registros de esta "
            "organización territorial y mantiene su residencia habitual en el área de influencia de "
            "nuestra junta de vecinos.<br/><br/>"
            "Se extiende el presente certificado a solicitud del interesado para ser presentado ante "
            f"<b>{c['motivo']}</b>, y para los fines que estime conveniente."
        )
        story.append(Paragraph(cuerpo, self.styles["Cuerpo"]))

        # Espacio antes de firmas
        story.append(Spacer(1, 1.6 * cm))

        # Preparar contenido de la celda del presidente: firma si existe, sino línea
        celda_presidente_firma = None
        if c.get("firma_io"):
            try:
                celda_presidente_firma = Image(c["firma_io"], width=6*cm, height=2*cm, kind='proportional')
            except Exception as e:
                logger.warning(f"Error insertando firma en PDF: {str(e)}")
                celda_presidente_firma = "_" * 30
        else:
            celda_presidente_firma = "_" * 30
        
        # Preparar timbre si existe
        celda_timbre = None
        if c.get("timbre_io"):
            try:
                celda_timbre = Image(c["timbre_io"], width=3*cm, height=3*cm, kind='proportional')
            except Exception as e:
                logger.warning(f"Error insertando timbre en PDF: {str(e)}")
        
                # Crear tabla con timbre a la izquierda y firma + texto a la derecha

        # Columna izquierda: timbre (o vacío si no hay)
        col_timbre = celda_timbre if celda_timbre else ""

        # Columna derecha: firma, línea, nombre, rut, rol
        firma_image = celda_presidente_firma if celda_presidente_firma else ""

        nombre_pres = c.get("presidente_nombre_completo", "")
        rut_pres = c.get("presidente_rut", "")
        rol_pres = "Presidente" if nombre_pres or rut_pres else ""

        firma_tabla = Table(
            [
                # fila 0: timbre | firma
                [col_timbre, firma_image],
                # fila 1: (vacío) | línea bajo firma
                ["", ""],
                # fila 2: (vacío) | nombre
                ["", nombre_pres],
                # fila 3: (vacío) | RUT
                # ["", rut_pres],
                # fila 4: (vacío) | rol
                ["", rol_pres],
            ],
            colWidths=[5 * cm, 11 * cm],  # timbre más angosto, firma/texto más ancho
        )

        firma_tabla.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

                    # Línea bajo la firma: fila 1, columna 1
                    ("LINEABOVE", (1, 1), (1, 1), 0.7, colors.black),

                    # Nombre y RUT un poco más pequeños
                    ("FONTNAME", (1, 2), (1, 3), "Helvetica"),
                    ("FONTSIZE", (1, 2), (1, 3), 10),

                    # Rol en negrita
                    ("FONTNAME", (1, 4), (1, 4), "Helvetica-Bold"),
                    ("FONTSIZE", (1, 4), (1, 4), 11),

                    # Un poco de padding vertical para que todo "respire"
                    ("TOPPADDING", (0, 0), (-1, 0), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 0),
                    ("TOPPADDING", (1, 2), (1, 4), 1),
                    ("BOTTOMPADDING", (1, 2), (1, 4), 1),
                ]
            )
        )

        story.append(firma_tabla)


        

        # Pie de página con lugar y fecha CENTRADO
        story.append(Spacer(1, 1.2 * cm))
        story.append(Paragraph(c["lugar_fecha"], self.styles["PieFecha"]))

        doc.build(story)
        pdf = buffer.getvalue()
        buffer.close()
        return pdf
