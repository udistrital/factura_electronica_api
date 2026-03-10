"""
Proyecto ODIN - Generador de servicios api-rest  
Módulo: Generador reportes Api-rest
Basado en framework Flask
Author: Jairol Lavado.
Fecha: Enero 2024
versión: 0.0.0.1
"""
import os
#import pyodbc
import psycopg2

def conectarPG(dbconnect):
    try:
        # Conéctate a la base de datos
        connection = psycopg2.connect(host=dbconnect["host"],database=dbconnect["database"],user=dbconnect["username"],password=dbconnect["password"],port=dbconnect["port"])
        return connection
        # conexión exitosa
    except Exception as epg:
        print("Error al conectar a Postgres Server: ", epg)
