"""
Servicio para envío de emails usando SendGrid API.

Este servicio maneja el envío de emails transaccionales como:
- Recuperación de contraseña
- Bienvenida
- Notificaciones

SendGrid funciona con API HTTP (no SMTP), por lo que funciona en Railway.
"""

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class EmailService:
    """
    Servicio para enviar emails usando SendGrid API.
    """

    def __init__(self, api_key: str, from_email: str = "vecindapp66@gmail.com", from_name: str = "VecindApp"):
        """
        Inicializa el servicio de email.
        
        Args:
            api_key: API key de SendGrid
            from_email: Email del remitente (debe estar verificado en SendGrid)
            from_name: Nombre del remitente
        """
        self.api_key = api_key
        self.from_email = from_email
        self.from_name = from_name
        self.client = SendGridAPIClient(api_key)

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        to_name: Optional[str] = None
    ) -> bool:
        """
        Envía un email usando SendGrid API.
        
        Args:
            to_email: Email del destinatario
            subject: Asunto del email
            html_body: Contenido HTML del email
            to_name: Nombre del destinatario (opcional)
            
        Returns:
            True si el email se envió correctamente, False en caso contrario
        """
        try:
            # Crear email con SendGrid
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_body)
            )
            
            # Enviar con SendGrid
            response = self.client.send(message)
            
            # Verificar respuesta
            if response.status_code in [200, 201, 202]:
                logger.info(f"✅ Email enviado exitosamente a {to_email} via SendGrid (Status: {response.status_code})")
                return True
            else:
                logger.error(f"❌ Error enviando email: Status {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"💥 Error inesperado enviando email con SendGrid: {str(e)}")
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
