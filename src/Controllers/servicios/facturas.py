"""
Proyecto ODIN - Generador de servicios api-rest  
Módulo: Generador reportes Api-rest
Basado en framework Flask
Author: Jairol Lavado.
Fecha: Enero 2024
versión: 0.0.0.1
"""
import json
import base64
import bcrypt
from flask import request, jsonify, Response
import numpy
import time
from datetime import datetime
import uuid
import re
import os, sys
p = os.path.abspath('src')
sys.path.insert(1, p)
from Controllers.general.function_jwt import write_token, validate_token
from Controllers.general.function_crypto import desencriptar_variable, keyEncode
from Controllers.general.function_consume import consumepostlogin, consumepost
#from Connect.mssqlbd import conexion
#from Connect.default_pgbd import conexion ## activar para conexión por defecto
from Scriptdb.servicios.facturas import *
from Connect.pgsqlbd import conectarPG
from Connect.orasqlbd import conectarORA
from Connect.mysqlbd import conectarMY

'''Funcion controladora del proceso ETL'''
def synchronizeFactura(req=""):
    try:
        #token = request.headers['Authorization'].split(" ")[1]
        #user=validate_token(token,output=True)
        registros = extractData(req)
        resultado = transformData(req,registros)
        respuesta = loadData(resultado)
        '''
        if api_reporte:
            respuesta = transformData(req,api_reporte)
        else:
            respuesta = {"Error":"El servicio no existe o el usuario no esta autorizado a consultarlo"}    
        '''    
        return respuesta
    except Exception as e:
        print("Ocurrió un error en sincronizar el api de reportes: ", e)   
        respuesta = {"Error":"El servicio no existe o el usuario no esta autorizado a consultarlo"}
        return respuesta
    #finally:
    #    conexion.close()        

'''Funcion que realiza las consulta de los datos de las fuentes de datos'''
def extractData(busqueda=""):
    try:
        #print(busqueda)
        #datos = consultaRegistros(conexion,busqueda)
        ruta_json = os.path.join(p, "Controllers/servicios/formatos", "JSON INDIVIDUAL FACTURA.json")
        with open(ruta_json, "r", encoding="utf-8") as file:
            datos = json.load(file)
        
        return datos
    except Exception as e:
        print("Ocurrió un error al rescatar datos del api de reportes: ", e)   

'''Funcion que realiza las validaciones y transformación de datos'''
def transformData(req,resultado):
    try:
        ## formatera variable respuesta
        respuesta={
                "status": "",
                "code": "",
                "resultado": {  "estado": "",
                                "mensaje": "",
                                "datos": ""
                              }
                }
        ## liguearse a plataforma Titanio
        host_titanio = os.getenv("TITANIO_HOST")
        login_titanio="/PDE/public/api/PDE/authentication"
        param_login={
                    "NIT": os.getenv("TITANIO_NIT"),
                    "usuario": os.getenv("TITANIO_USER"),
                    "password": os.getenv("TITANIO_PWD")
                }
        acceso=consumepostlogin(host_titanio,login_titanio,param_login)
        #print(acceso)
        #print(acceso['succes'])
        # Validar token
        ## validacion temporal,borrar 
        acceso['succes']= True
        acceso['token']='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJJZCI6MiwiVXN1YXJpbyI6ImphaXJvbGgiLCJOb21icmVzIjoiSmFpcm8iLCJBcGVsbGlkb3MiOiJMYXZhZG8iLCJTdXBlcmFkbWluIjp0cnVlLCJUaXBvIjoiQWRtaW5pc3RyYWRvciIsIlZlcnNpb24iOiI3OTgxMjIxMiIsImV4cCI6MTc2ODQwMjg1NX0.7jQgWLtuFVLfhNPDiwDT_ZZWjJyRioVfsnUB57x9Zv0'
        
        # Validar si no se obtuvo token
        if acceso['succes'] is False and acceso['token'] is None:
            respuesta['status']="error"
            respuesta['code']=401
            respuesta['resultado']['estado']="error"
            respuesta['resultado']['mensaje']="No fue posible obtener el token de autenticación Titanio."
        else:
            #print(resultado)
            # Convertir el objeto Python a string JSON
            json_string = json.dumps(resultado)
            # Convertir a bytes
            json_bytes = json_string.encode("utf-8")
            # Codificar en Base64
            base64_bytes = base64.b64encode(json_bytes)
            # Convertir nuevamente a string para imprimir o usar
            base64_resultado = base64_bytes.decode("utf-8")
            # print(base64_resultado)
            param_bill={
                    "token": acceso['token'],
                    "tr_tipo_id": 1,
                    "data": base64_resultado
                }    

           # print(param_bill)


            respuesta['status']="sucess"
            respuesta['code']=200
            respuesta['resultado']['estado']="sucess"
            respuesta['resultado']['mensaje']="Registro satisfactorio factura electronica Titanio."    
            respuesta['resultado']['datos']={"cufe":"adsasdjaosjdaosjdoisjdos" }   

        return respuesta

    except Exception as e:
        print("Ocurrió un error al transformar el api de reporte: ", e)   

'''Funcion que realiza el cargue de los datos al repositorio'''
def loadData(resultado):
    try:
        #print("load") 
        #print(resultado) 
        
        response = Response(
                json.dumps(resultado['resultado'], ensure_ascii=False),
                content_type="application/json; charset=utf-8"
            )
        #response = Response(resultado['resultado'],content_type="application/json; charset=utf-8" )                 
        response.status_code = resultado['code']
        return response 

    except Exception as e:
        print("Ocurrió un error al cargar el api de reporte: ", e) 


def muestra(registro,campos):
    try:
        suma = 0  
        for campo in campos:
            suma=suma+registro[campo]
        return suma
    except Exception as e:
        print("Ocurrió un error al sumar los datos: ", e)    

