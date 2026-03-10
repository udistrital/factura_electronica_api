"""
Proyecto ODIN - Generador de servicios api-rest  
Módulo: Generador reportes Api-rest
Basado en framework Flask
Author: Jairol Lavado.
Fecha: Enero 2024
versión: 0.0.0.1
"""
import jwt 
from os import getenv
from datetime import datetime, timedelta
from cryptography.fernet import Fernet , InvalidToken
import hashlib

# Encripta una variable
def encriptar_variable(variable, clave):
    f = Fernet(clave)
    return f.encrypt(variable.encode())

# Desencripta una variable
def desencriptar_variable(variable_encriptada, clave):
    try:
        f = Fernet(clave)
        return f.decrypt(variable_encriptada).decode()
    except InvalidToken:
        # Manejo de errores en caso de que la desencriptación falle
        print("Error: InvalidToken - No se pudo desencriptar la variable")
        return None

def keyEncode():
    clave = 'G3st10nG3n3r4d0rS3rv1c10sW3b4g1lJL4v4d0ODIN='
    return str(clave) 

