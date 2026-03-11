"""
Proyecto ODIN - Generador de servicios api-rest  
Módulo: Generador reportes Api-rest
Basado en framework Flask
Author: Jairol Lavado.
Fecha: Enero 2024
versión: 0.0.0.1
"""
from jwt import encode, decode
from jwt import exceptions
from os import getenv
from datetime import datetime, timedelta
from flask import jsonify
import warnings
warnings.filterwarnings("ignore", message="The HMAC key is .* bytes long")


def expire_date(days: int):
    now = datetime.now()
    new_date = now + timedelta(days)
    return new_date

def write_token(data: dict):
    token = encode(payload={**data, "exp": expire_date(1)},
                   key=getenv("SECRET"), algorithm="HS256")
    return token.encode("UTF-8")

def validate_token_exp(token, output=False):
    try:
        if output:
            return decode(token, key=getenv("SECRET"), algorithms=["HS256"])
        decode(token, key=getenv("SECRET"), algorithms=["HS256"])
    except exceptions.DecodeError:
        response = jsonify({"message": "Invalid Token"})
        response.status_code = 401
        return response
    except exceptions.ExpiredSignatureError:
        response = jsonify({"message": "Token Expired"})
        response.status_code = 401
        return response

def validate_token(token, output=False):
    try:
        decoded = decode(
            token,
            key=getenv("SECRET"),
            algorithms=["HS256"],
            options={"verify_exp": False}
        )
        usuario = decoded.get("Usuario")
        # Validar usuario autorizado
        if usuario != "sgant":
            response = jsonify({"message": "Usuario no autorizado"})
            response.status_code = 401
            return response
        if output:
            return decoded
    except exceptions.DecodeError:
        response = jsonify({"message": "Invalid Token"})
        response.status_code = 401
        return response
    except exceptions.ExpiredSignatureError:
        response = jsonify({"message": "Token Expired"})
        response.status_code = 401
        return response