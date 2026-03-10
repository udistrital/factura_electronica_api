"""
Proyecto ODIN - Generador de servicios api-rest  
Módulo: Generador reportes Api-rest
Basado en framework Flask
Author: Jairol Lavado.
Fecha: Enero 2024
versión: 0.0.0.1
"""
from flask import Blueprint, request, jsonify
from requests import get
import time
import uuid
import json
from datetime import datetime

import os, sys
p = os.path.abspath('src')
sys.path.insert(1, p)
from Controllers.general.function_jwt import validate_token
from Controllers.servicios.facturas import synchronizeFactura

servicio = Blueprint("serv", __name__)
''' 
@servicio.before_request
def verify_token_middleware():
    token = request.headers['Authorization'].split(" ")[1]
    return validate_token(token,output=False)
'''
@servicio.route("/serv/bill", methods=["POST"])
def bill_service():
    data = request.get_json()
    respuesta = synchronizeFactura(data)
    return respuesta

