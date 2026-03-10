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
import psycopg2

try:
    conexion = psycopg2.connect(host=os.environ['BILLPG_HOST'],database=os.environ['BILLPG_DB'],user=os.environ['BILLPG_USER'],password=os.environ['BILLPG_PASSWORD'],port=os.environ['BILLPG_PORT'])
    # conexión exitosa
except Exception as e:
    print("Error al conectar a Postgres: ", e)
