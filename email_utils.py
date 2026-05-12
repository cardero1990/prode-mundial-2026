"""
email_utils.py - Envio de emails via Gmail SMTP para Prode Mundial 2026
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_reset_email(to_email: str, code: str, display_name: str) -> tuple[bool, str]:
    """
    Envia un email con codigo de recuperacion de contraseña.
    Retorna (True, "") si exitoso, o (False, mensaje_error) si fallo.
    """
    try:
        import streamlit as st
        sender = st.secrets["gmail"]["sender_email"]
        app_password = st.secrets["gmail"]["app_password"]
    except Exception:
        return False, "No se pudo leer la configuracion de Gmail. Revisá secrets.toml."

    subject = "Prode Mundial 2026 - Recuperacion de Contraseña"

    body = f"""Hola {display_name},

Recibimos una solicitud para restablecer tu contraseña del Prode Mundial 2026.

Tu codigo de recuperacion es:

    {code}

Este codigo expira en 15 minutos.

Pasos para recuperar tu contraseña:
1. Volvé a la app del Prode.
2. Hacé clic en "Olvide mi contraseña".
3. Ingresá tu email y luego este codigo.
4. Creá una nueva contraseña.

Si no solicitaste este cambio, ignorá este mensaje. Tu contraseña actual no cambiará.

Suerte en el Prode Mundial 2026!
"""

    try:
        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = to_email
        msg.attach(MIMEText(body, "plain", "utf-8"))

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender, app_password)
            server.sendmail(sender, to_email, msg.as_bytes())

        return True, ""

    except smtplib.SMTPAuthenticationError:
        return False, "Error de autenticacion con Gmail. Verificá el App Password en secrets.toml."
    except smtplib.SMTPException as e:
        return False, f"Error al enviar el email: {str(e)}"
    except Exception as e:
        return False, f"Error inesperado: {str(e)}"
