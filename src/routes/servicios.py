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
from Controllers.servicios.emitirFactura import emitBill
from Controllers.servicios.emitirNotaCredito import emitCredNote
from Controllers.servicios.emitirNotaDebito import emitDebitNote
from Controllers.servicios.sincronizaFactura import sincronizeBill
from Controllers.servicios.ejecutarFactura import executeBill

servicio = Blueprint("serv", __name__)
''' 
@servicio.before_request
def verify_token_middleware():
    token = request.headers['Authorization'].split(" ")[1]
    return validate_token(token,output=False)
'''
@servicio.route("/serv/emit", methods=["POST"])
def bill_service():
    data = request.get_json()
    respuesta = emitBill(data)
    return respuesta

@servicio.route("/serv/creditnote", methods=["POST"])
def credit_service():
    data = request.get_json()
    respuesta = emitCredNote(data)
    return respuesta

@servicio.route("/serv/debitnote", methods=["POST"])
def debit_service():
    data = request.get_json()
    respuesta = emitDebitNote(data)
    return respuesta    

@servicio.route("/serv/sinc", methods=["POST"])
def sinc_service():
    data = request.get_json()
    respuesta = sincronizeBill(data)
    return respuesta

@servicio.route("/serv/exec", methods=["POST"])
def exec_service():
    data = request.get_json()
    respuesta = executeBill(data)
    return respuesta

