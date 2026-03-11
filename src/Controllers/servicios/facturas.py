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
from Controllers.general.function_consume import consumepost_bearer, consumepost, consumepost_trans
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
        conexion=switchconn('oracle')
        registros = extractData(req,conexion)
        resultado = transformData(req,registros)
        respuesta = loadData(resultado,conexion)
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
def extractData(busqueda="",conexion=""):
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
        acceso={}#consumepost(host_titanio,login_titanio,param_login)
        #print(acceso)
        #print(acceso['succes'])
        # Validar token
        ## validacion temporal,borrar 
        acceso['succes']= True
        acceso['token']='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJJZCI6MiwiVXN1YXJpbyI6ImphaXJvbGgiLCJOb21icmVzIjoiSmFpcm8iLCJBcGVsbGlkb3MiOiJMYXZhZG8iLCJTdXBlcmFkbWluIjp0cnVlLCJUaXBvIjoiQWRtaW5pc3RyYWRvciIsIlZlcnNpb24iOiI3OTgxMjIxMiIsImV4cCI6MTc2ODQwMjg1NX0.7jQgWLtuFVLfhNPDiwDT_ZZWjJyRioVfsnUB57x9Zv0'
        
        # Validar si no se obtuvo token
            # Validar token
        if not acceso.get("succes") or not acceso.get("token"):
            respuesta['status'] = "error"
            respuesta['code'] = 401
            respuesta['resultado']['estado'] = "error"
            respuesta['resultado']['mensaje'] = "No fue posible obtener el token de autenticación Titanio."
            return respuesta
        else:
            try:    

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
                        "tr_tipo_id": 12839,
                        "data": base64_resultado
                    }    
                #print(param_bill)
                emitir_titanio="/PDE/public/api/PDE/emitir_v2"
                #factura=consumepost_trans(host_titanio,emitir_titanio,param_bill)
                
                #factura= {"error_id": 300, "error_msg": "Su sesión ha caducado debe iniciar sesión nuevamente.", "mensaje": None, "tr_id": None, "cufe": None, "qr": None}
                
                factura = { 'error_id' : 0,
                            'error_msg' : 'Se realizo con exito la operacion.',
                            'mensaje' : ' ----------------------------\r\nMensajes de Conversión a Dataset:\r\nIniciando Conversión\r\nExcepción de conversión: \r\nEtiqueta final inesperada. línea 2, posición 3.\r\n\r\n----------------------------\r\nMensajes de la validación del Dataset:\r\nAdvertencia:[FAB36] El código QR (EXT/QRCode) se corrigió\r\n----------------------------\r\nMensajes de Conversión a UBL:\r\nIniciando Conversión\r\nTerminando Conversión\r\n\r\n----------------------------\r\nMensajes de la validación del UBL:\r\nXML Válido:\r\n----------------------------\r\nMensajes de Agregar a Cola:\r\nSe agrego a la cola con exito.\r\n.',
                            'tr_id' : 100,
                            'cufe': '2bec67asdasd9dasdasd46asdasdaassdasd',
                            'qr': ' NumFac: SETP90000507\r\nFe...',
                            }
               
                # se verifica si se presento error en la solicitud de emision d ela factura
                if factura.get("error_id") > 0:
                    respuesta['status'] = "error"
                    respuesta['code'] = 422
                    respuesta['resultado']['estado'] = "error"
                    respuesta['resultado']['mensaje'] = "No fue posible la solicitud de emitir la factura a Titanio."
                    return respuesta
                else:
                    recibo=req.get("parametros")
                    datos_transaccion= {"vigencia":recibo.get("vigencia"), 
                                        "secuencia":recibo.get("secuencia"), 
                                        "identificacion":recibo.get("identificacion"), 
                                        "id_transaccion":factura.get("tr_id"), 
                                        "cufe":factura.get("cufe"),
                                        "qr_cod":factura.get("qr"),
                                       }
                    respuesta['status']="success"
                    respuesta['code']=200
                    respuesta['resultado']['estado']="success"
                    respuesta['resultado']['mensaje']="Registro satisfactorio factura electronica Titanio."    
                    respuesta['resultado']['datos']=datos_transaccion
                    return respuesta

            except Exception as e:
                print("Ocurrió un error al emitir la factura: ", e)
                respuesta['status'] = "error"
                respuesta['code'] = 422
                respuesta['resultado']['estado'] = "error"
                respuesta['resultado']['mensaje'] = "No fue posible la solicitud de emitir la factura a Titanio."   
                return respuesta

    except Exception as e:
        print("Ocurrió un error al emitir la factura: ", e)
        respuesta['status'] = "error"
        respuesta['code'] = 422
        respuesta['resultado']['estado'] = "error"
        respuesta['resultado']['mensaje'] = "No fue posible emitir la factura."
        return respuesta

'''Funcion que realiza el cargue de los datos al repositorio'''
def loadData(resultado,conexion=""):
    try:
        # si se logra solicitar la emision de la factura se registra en base de datos
        if resultado.get('status') == "success":
            datos = resultado['resultado']['datos']
            # Si se cunata con  CUFE, se actualiza en la factura
            if datos.get("cufe"):
                cufe = registroCUFE(conexion,datos)
                datos['estado'] = 'E' if datos.get("cufe") and cufe.get("exec") is True else 'S'
            else:
                datos['estado'] = 'S'
            #registrar datos de la solicitud de emision de la factura            
            envio = registroEnvio(conexion,datos)
        #se retorna respuesta de la emisión de la factura 
        response = Response(
                json.dumps(resultado['resultado'], ensure_ascii=False),
                content_type="application/json; charset=utf-8"
            )
        #response = Response(resultado['resultado'],content_type="application/json; charset=utf-8" )                 
        response.status_code = resultado['code']
        return response 

    except Exception as e:
        #print("Ocurrió un error en el registro de la emisión de la factura: ", e)
        resp = '{"estado":"error", "mensaje": "Ocurrió un error en el registro de la emisión de la factura."}'
        response = Response(
                json.dumps(resp, ensure_ascii=False),
                content_type="application/json; charset=utf-8"
            )
        response.status_code = 400
        return response 


def muestra(registro,campos):
    try:
        suma = 0  
        for campo in campos:
            suma=suma+registro[campo]
        return suma
    except Exception as e:
        print("Ocurrió un error al sumar los datos: ", e)    


def switchconn(motor):
    if motor.lower() == "oracle":
        dbconnect = {"host":os.getenv("BILLORA_HOST"),
                     "port":os.getenv("BILLORA_PORT") ,
                     "database":os.getenv("BILLORA_DB"),
                     "username":os.getenv("BILLORA_USER"),
                     "password":os.getenv("BILLORA_PASSWORD"),
                    }
        return conectarORA(dbconnect)
    elif motor.lower() == "pgsql":
        dbconnect = { "host":os.getenv("BILLPG_HOST"),
                      "port":os.getenv("BILLPG_PORT") ,
                      "database":os.getenv("BILLPG_DB"),
                      "username":os.getenv("BILLPG_USER"),
                      "password":os.getenv("BILLPG_PASSWORD")
                    }
        return conectarPG(dbconnect)
    elif motor.lower() == "mysql":
        return conectarMY(dbconnect)
    else:
        return conexion