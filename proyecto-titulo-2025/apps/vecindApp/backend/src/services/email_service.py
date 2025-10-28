"""
Servicio para envío de emails usando Gmail SMTP.

Este servicio maneja el envío de emails transaccionales como:
- Recuperación de contraseña
- Bienvenida
- Notificaciones
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

logger = logging.getLogger(__name__)


class EmailService:
    """
    Servicio para enviar emails usando Gmail SMTP.
    """

    def __init__(self, gmail_user: str, gmail_password: str, from_name: str = "VecindApp"):
        """
        Inicializa el servicio de email.
        
        Args:
            gmail_user: Email de Gmail
            gmail_password: Contraseña de aplicación de Gmail
            from_name: Nombre del remitente
        """
        self.gmail_user = gmail_user
        self.gmail_password = gmail_password
        self.from_name = from_name
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        to_name: Optional[str] = None
    ) -> bool:
        """
        Envía un email usando Gmail SMTP.
        
        Args:
            to_email: Email del destinatario
            subject: Asunto del email
            html_body: Contenido HTML del email
            to_name: Nombre del destinatario (opcional)
            
        Returns:
            True si el email se envió correctamente, False en caso contrario
        """
        try:
            # Crear mensaje
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.gmail_user}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Agregar contenido HTML
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
            
            # Conectar al servidor SMTP de Gmail
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # Iniciar conexión segura TLS
            
            # Autenticar
            server.login(self.gmail_user, self.gmail_password)
            
            # Enviar email
            server.send_message(msg)
            server.quit()
            
            logger.info(f"✅ Email enviado exitosamente a {to_email} desde Gmail")
            return True

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"❌ Error de autenticación Gmail: {str(e)}")
            logger.error("💡 Verifica que uses una contraseña de aplicación, no tu contraseña normal")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"❌ Error SMTP: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"💥 Error inesperado enviando email: {str(e)}")
            return False

    def send_password_reset_code(
        self,
        to_email: str,
        code: str,
        user_name: str = "Usuario"
    ) -> bool:
        """
        Envía un código de recuperación de contraseña.
        
        Args:
            to_email: Email del destinatario
            code: Código de 6 dígitos
            user_name: Nombre del usuario
            
        Returns:
            True si el email se envió correctamente
        """
        subject = "Código de Recuperación de Contraseña - VecindApp"
        
        # HTML body con diseño moderno
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    margin: 0;
                    padding: 0;
                    background-color: #f5f5f5;
                }}
                .container {{
                    max-width: 600px;
                    margin: 20px auto;
                    background: white;
                    border-radius: 12px;
                    overflow: hidden;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #0f766e 0%, #0d9488 100%);
                    color: white;
                    padding: 30px 20px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 24px;
                    font-weight: 600;
                }}
                .content {{
                    padding: 40px 30px;
                }}
                .greeting {{
                    font-size: 18px;
                    color: #333;
                    margin-bottom: 20px;
                }}
                .message {{
                    color: #666;
                    margin-bottom: 30px;
                    font-size: 15px;
                }}
                .code-container {{
                    background: linear-gradient(135deg, #f0fdfa 0%, #e6fffa 100%);
                    border: 2px solid #0f766e;
                    border-radius: 12px;
                    padding: 30px;
                    text-align: center;
                    margin: 30px 0;
                }}
                .code-label {{
                    color: #0f766e;
                    font-size: 14px;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                    margin-bottom: 15px;
                }}
                .code {{
                    font-size: 48px;
                    font-weight: bold;
                    color: #0f766e;
                    letter-spacing: 8px;
                    font-family: 'Courier New', monospace;
                }}
                .warning {{
                    background: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 4px;
                }}
                .warning-text {{
                    color: #856404;
                    font-size: 14px;
                    margin: 0;
                }}
                .footer {{
                    background: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    color: #6c757d;
                    font-size: 13px;
                    border-top: 1px solid #dee2e6;
                }}
                .footer p {{
                    margin: 5px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏘️ VecindApp</h1>
                </div>
                <div class="content">
                    <div class="greeting">
                        Hola <strong>{user_name}</strong>,
                    </div>
                    <div class="message">
                        Recibimos una solicitud para restablecer la contraseña de tu cuenta. 
                        Usa el siguiente código de verificación para continuar con el proceso:
                    </div>
                    <div class="code-container">
                        <div class="code-label">Tu código de verificación</div>
                        <div class="code">{code}</div>
                    </div>
                    <div class="warning">
                        <p class="warning-text">
                            ⏱️ <strong>Este código expirará en 15 minutos.</strong><br>
                            🔒 Si no solicitaste este cambio, ignora este correo y tu contraseña permanecerá segura.
                        </p>
                    </div>
                    <div class="message">
                        Para tu seguridad, nunca compartas este código con nadie.
                    </div>
                </div>
                <div class="footer">
                    <p><strong>VecindApp</strong> - Tu comunidad digital</p>
                    <p>Este es un correo automático, por favor no respondas.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return self.send_email(
            to_email=to_email,
            subject=subject,
            html_body=html_body,
            to_name=user_name
        )
