"""
Proyecto ODIN - Generador de servicios api-rest  
Módulo: Generador reportes Api-rest
Basado en framework Flask
Author: Jairol Lavado.
Fecha: Enero 2024
versión: 0.0.0.1
"""
import os
from dotenv import load_dotenv
load_dotenv()
import cx_Oracle

def conectarORA(dbconnect):
    try:
        # Establece los detalles de la conexión
        dsn_tns = cx_Oracle.makedsn(dbconnect["host"], dbconnect["port"], service_name=dbconnect["database"])
        # Conéctate a la base de datos
        connection = cx_Oracle.connect(dbconnect["username"], dbconnect["password"], dsn_tns)
        return connection
        # conexión exitosa
    except Exception as e:
        print("Error al conectar a ORACLE Server: ", e)
