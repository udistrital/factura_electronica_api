"""
Proyecto ODIN - Generador de servicios api-rest  
Módulo: Generador reportes Api-rest
Basado en framework Flask
Author: Jairol Lavado.
Fecha: Enero 2024
versión: 0.0.0.1
"""
import os
import pyodbc
driver='FreeTDS'
def conectarMSS(dbconnect):
    try:
        connection = pyodbc.connect('DRIVER='+driver+';SERVER='+dbconnect["host"]+';DATABASE='+dbconnect["host"]+';UID='+dbconnect["username"]+';PWD=' +dbconnect["password"]+';Port=' + dbconnect["port"]+';TDS_Version=8.0;')
        return connection
        # conexión exitosa
    except Exception as es:
        print("Error al conectar a SQL Server: ", es)
