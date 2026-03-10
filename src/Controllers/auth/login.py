"""
Proyecto ODIN - Generador de servicios api-rest  
Módulo: Generador reportes Api-rest
Basado en framework Flask
Author: Jairol Lavado.
Fecha: Enero 2024
versión: 0.0.0.1
"""
import json
#import bcrypt
from flask import request, jsonify, Flask
import numpy
from pbkdf2 import PBKDF2
import hashlib
import base64

import os, sys
p = os.path.abspath('src')
sys.path.insert(1, p)
from Controllers.general.function_jwt import write_token, validate_token
from Connect.default_pgbd import conexion
from Scriptdb.auth.login import *
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

def synchronizeData(usuario):
    validalogin = None  # Inicializar la variable antes de usarla
    try:
        resultado = extractData(usuario['username'])
        if resultado and len(resultado) > 0:  # Asegurar que 'resultado' no sea None
            validalogin = transformData(usuario, resultado[0])
        else:
            response = jsonify({"message": "Usuario o clave incorrectos"})
            response.status_code = 404
            validalogin = response
        # loadData(instalaciones)
        return validalogin
    except Exception as e:
        logging.info("Ocurrió un error al sincronizar usuarios: ", e)
        if validalogin is None:  # Verificar si validalogin ya tiene un valor
            response = jsonify({"message": "No es posible rescatar datos"})
            response.status_code = 404
            validalogin = response
        return validalogin
    #finally:
    #    conexion.close()        

def extractData(busqueda=""):
    try:
        datos = consultaUsuario(conexion,busqueda)
        return datos
    except Exception as e:
        print("Ocurrió un error al rescatar datos de los usuarios: ", e)   

def transformData(usuario, resultado):
    try:
        password = usuario['password']
        passwordSaved = resultado['Clave']
        validapass = verificar_contrasena(password, passwordSaved)
        #validapass = bcrypt.checkpw(password.encode('utf8'), password2.encode('utf8'))
        if usuario['username'] in resultado['Usuario'] and validapass == True:
            data = { "Id": resultado['Id'],
                     "Usuario": resultado['Usuario'],
                     "Nombres": resultado['Nombres'],
                     "Apellidos": resultado['Apellidos'],
                     "Superadmin": resultado['Superadmin'],
                     "Tipo": resultado['Tipousuario'],
                     "Version": usuario['version'],
                    }
            token = write_token(data)    
            response = jsonify({"token": str(token)[2:-1]})
            response.status_code = 200
        else:
            logging.info("La contraseña o el usuario no son correctos")
            response = jsonify({"error": "Usuario o clave incorrectas"})
            response.status_code = 404
        return response
    except Exception as e:
        logging.error("Ocurrió un error al transformar los usuarios: ", e)
        response = jsonify({"error": "No es posible rescatar los datos"})
        response.status_code = 404
        return response

def loadData(registros):
    try:
        print("load")  
    except Exception as e:
        print("Ocurrió un error al cargar las usuarios: ", e)   


def verificar_contrasena(pass_ingresada, pass_almacenada):
    # Obtener la sal y el hash de la contraseña almacenada
    partespass = pass_almacenada.split('$')
    # identifica algoritmo
    partesalg = partespass[0].split('_')
    algoritmo = partesalg[1]
    # iteraciones segunda parte
    iteraciones = partespass[1]
    # La sal es la tercera parte
    salt = partespass[2]
    # hash password cuarta parte
    hashed_saved = partespass[3]
    # Calcular el hash PBKDF2 con SHA-256
    hashed_password = hashlib.pbkdf2_hmac(algoritmo, pass_ingresada.encode('utf-8'), salt.encode('utf-8'), int(iteraciones))
    hashed_password_b64 = base64.b64encode(hashed_password).decode("ascii").strip()
    # Comparar los hashes
    if hashed_password_b64 == hashed_saved:
        return True
    else:
        return False
