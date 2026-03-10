"""
Proyecto ODIN - Generador de servicios api-rest  
Módulo: Generador reportes Api-rest
Basado en framework Flask
Author: Jairol Lavado.
Fecha: Enero 2024
versión: 0.0.0.1
"""
import os
import mysql.connector

def conectarMY(dbconnect):
    try:
        # Conéctate a la base de datos
        connection = mysql.connector.connect(host=dbconnect["host"],database=dbconnect["database"],user=dbconnect["username"],password=dbconnect["password"],port=dbconnect["port"], raise_on_warnings=True)
        return connection
        # conexión exitosa
    except Exception as emyg:
        print("Error al conectar a MySql Server: ", emy)
