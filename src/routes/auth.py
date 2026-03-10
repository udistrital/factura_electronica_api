"""
Proyecto ODIN - Generador de servicios api-rest  
Módulo: Generador reportes Api-rest
Basado en framework Flask
Author: Jairol Lavado.
Fecha: Enero 2024
versión: 0.0.0.1
"""
from re import split
from flask import Blueprint, request, jsonify
import os, sys
import logging
p = os.path.abspath('src')
sys.path.insert(1, p)
from Controllers.general.function_jwt import write_token, validate_token
from Controllers.auth.login import synchronizeData

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

routes_auth = Blueprint("routes_auth", __name__)

@routes_auth.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "Service is healthy"}), 200

@routes_auth.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    logging.info("username " + data.get("username", "No username provided"))
    respuesta = synchronizeData(data)
    logging.info(respuesta)
    return respuesta

@routes_auth.route("/auth/verify/token")
def verify():
    token = request.headers['Authorization'].split(" ")[1]
    return validate_token(token, output=True)
