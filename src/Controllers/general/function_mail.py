import os
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


MAIL_SERVERS = {
    "gmail": {"host": "smtp.gmail.com", "port": 587, "tls": True},
    "google": {"host": "smtp.gmail.com", "port": 587, "tls": True},
    "outlook": {"host": "smtp.office365.com", "port": 587, "tls": True},
    "hotmail": {"host": "smtp.office365.com", "port": 587, "tls": True},
    "office365": {"host": "smtp.office365.com", "port": 587, "tls": True},
    "yahoo": {"host": "smtp.mail.yahoo.com", "port": 587, "tls": True},
    "sendgrid": {"host": "smtp.sendgrid.net", "port": 587, "tls": True},
}


def limpiaVariableCorreo(valor):
    return str(valor or "").strip().strip("'").strip('"')


def obtieneDestinatarios(valor):
    destinatarios = limpiaVariableCorreo(valor)
    return [
        correo.strip()
        for correo in re.split(r"[,;]", destinatarios)
        if correo.strip()
    ]


def obtieneServidorCorreo(servicio):
    servicio = limpiaVariableCorreo(servicio).lower()
    if not servicio:
        servicio = "gmail"

    if servicio in MAIL_SERVERS:
        config = MAIL_SERVERS[servicio].copy()
        config["servicio"] = servicio
        return config

    return {
        "servicio": servicio,
        "host": servicio,
        "port": 587,
        "tls": True
    }


def enviarCorreo(asunto, mensaje, html=None, remitente=None, clave=None, destinatarios=None, servicio=None):
    remitente = limpiaVariableCorreo(remitente or os.getenv("MAIL_SEND"))
    clave = limpiaVariableCorreo(clave or os.getenv("MAIL_PWD"))
    destinatarios = obtieneDestinatarios(destinatarios or os.getenv("MAIL_RECIVE"))
    config = obtieneServidorCorreo(servicio or os.getenv("MAIL_SERV"))

    if not remitente or not clave or not destinatarios:
        return {
            "exec": False,
            "estado": "no_enviado",
            "message": "No se encontraron las variables de correo requeridas"
        }

    try:
        correo = MIMEMultipart("alternative")
        correo["From"] = remitente
        correo["To"] = ", ".join(destinatarios)
        correo["Subject"] = asunto
        correo.attach(MIMEText(str(mensaje or ""), "plain", "utf-8"))

        if html:
            correo.attach(MIMEText(str(html), "html", "utf-8"))

        with smtplib.SMTP(config["host"], config["port"]) as smtp:
            if config.get("tls"):
                smtp.starttls()
            smtp.login(remitente, clave)
            smtp.sendmail(remitente, destinatarios, correo.as_string())

        return {
            "exec": True,
            "estado": "enviado",
            "servicio": config["servicio"],
            "host": config["host"],
            "destinatarios": destinatarios
        }
    except Exception as e:
        return {
            "exec": False,
            "estado": "error",
            "servicio": config["servicio"],
            "host": config["host"],
            "error": str(e)
        }
