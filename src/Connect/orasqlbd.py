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

_pool = None

def crearPoolORA(dbconnect):
    dsn_tns = cx_Oracle.makedsn(
        dbconnect["host"],
        dbconnect["port"],
        service_name=dbconnect["database"]
    )
    return cx_Oracle.SessionPool(
        user=dbconnect["username"],
        password=dbconnect["password"],
        dsn=dsn_tns,
        min=1,
        max=5,
        increment=1,
        threaded=True,
        getmode=cx_Oracle.SPOOL_ATTRVAL_WAIT,
        encoding="UTF-8"
    )

def conectarORA(dbconnect):
    global _pool
    try:
        if _pool is None:
            _pool = crearPoolORA(dbconnect)
        return _pool.acquire()
    except Exception as e:
        print("Error al conectar a ORACLE Server: ", e)
        return None
