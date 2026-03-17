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
#from Connect.default_pgbd import conexion ## activar para conexión por defecto
from Scriptdb.servicios.facturas import * 
from Connect.pgsqlbd import conectarPG
from Connect.orasqlbd import conectarORA
from Connect.mysqlbd import conectarMY

try:
    import cx_Oracle
    LOB_TYPES = (cx_Oracle.LOB,)
except Exception:
    LOB_TYPES = tuple()

'''Funcion controladora del proceso ETL'''
def synchronizeFactura(req=""):
    try:
        #token = request.headers['Authorization'].split(" ")[1]
        #user=validate_token(token,output=True)
        conexion=switchconn('oracle')
        registros = extractData(req,conexion)
        resultado = transformData(req,registros)
        respuesta = loadData(resultado,conexion)
        #respuesta = registros
        '''
        if api_reporte:
            respuesta = transformData(req,api_reporte)
        else:
            respuesta = {"Error":"El servicio no existe o el usuario no esta autorizado a consultarlo"}    
        '''    
        return respuesta
    except Exception as e:
        #print("Ocurrió un error en sincronizar el api de reportes: ", e)   
        respuesta = {"Error":"No fue posible procesar la emisión de la factura a Titanio"}
        return respuesta
    #finally:
    #    conexion.close()        

'''Funcion que realiza las consulta de los datos de las fuentes de datos'''
def extractData(busqueda="",conexion=""):
    try:
        recibo=busqueda.get('parametros')
        data = consultaRegistros(conexion,recibo)
        json_text = data['data'][0]['JSON_RESULT'].read()
        datos = json.loads(json_text)
        '''
        ruta_json = os.path.join(p, "Controllers/servicios/formatos", "JSON INDIVIDUAL FACTURA2.json")
        with open(ruta_json, "r", encoding="utf-8") as file:
            datos = json.load(file)
        '''
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

        try:
            acceso = consumepost(host_titanio, login_titanio, param_login)
        except requests.exceptions.Timeout:
            respuesta["status"] = "error"
            respuesta["code"] = 504
            respuesta["resultado"]["estado"] = "error"
            respuesta["resultado"]["mensaje"] = "Timeout al autenticar con Titanio."
            respuesta["resultado"]["datos"] = {"detalle": "El servicio de autenticación no respondió a tiempo."}
            return respuesta
        except requests.exceptions.RequestException as e:
            respuesta["status"] = "error"
            respuesta["code"] = 502
            respuesta["resultado"]["estado"] = "error"
            respuesta["resultado"]["mensaje"] = "Error de comunicación con Titanio al autenticar."
            respuesta["resultado"]["datos"] = {"detalle": str(e)}
            return respuesta


        #acceso=consumepost(host_titanio,login_titanio,param_login)
        # Validar token
        if not acceso.get("succes") or not acceso.get("token"):
            respuesta['status'] = "error"
            respuesta['code'] = 401
            respuesta['resultado']['estado'] = "error"
            respuesta['resultado']['mensaje'] = "No fue posible obtener el token de autenticación Titanio."
            return respuesta
        else:
            try:    
                factura_base64 = convertir_a_base64(resultado) 
                #print(factura_base64)
                param_bill={
                        "token": acceso['token'],
                        "tr_tipo_id": 12839,
                        "data": factura_base64
                    }    
                #print(param_bill)
                emitir_titanio="/PDE/public/api/PDE/emitir_v2"
                factura=consumepost_trans(host_titanio,emitir_titanio,param_bill)
                #factura= {"error_id": 300, "error_msg": "Su sesión ha caducado debe iniciar sesión nuevamente.", "mensaje": None, "tr_id": None, "cufe": None, "qr": None}
                '''
                factura = { 'error_id' : 0,
                            'error_msg' : 'Se realizo con exito la operacion.',
                            'mensaje' : ' ----------------------------\r\nMensajes de Conversión a Dataset:\r\nIniciando Conversión\r\nExcepción de conversión: \r\nEtiqueta final inesperada. línea 2, posición 3.\r\n\r\n----------------------------\r\nMensajes de la validación del Dataset:\r\nAdvertencia:[FAB36] El código QR (EXT/QRCode) se corrigió\r\n----------------------------\r\nMensajes de Conversión a UBL:\r\nIniciando Conversión\r\nTerminando Conversión\r\n\r\n----------------------------\r\nMensajes de la validación del UBL:\r\nXML Válido:\r\n----------------------------\r\nMensajes de Agregar a Cola:\r\nSe agrego a la cola con exito.\r\n.',
                            'tr_id' : 100,
                            'cufe': '2bec67asdasd9dasdasd46asdasdaassdasd',
                            'qr': ' NumFac: SETP90000507\r\nFe...',
                            }
                '''            
                # se verifica si se presento error en la solicitud de emision d ela factura
                if factura.get("error_id") > 0:
                    mensaje = factura.get("mensaje") if factura.get("mensaje") else factura.get("error_msg")
                    respuesta['status'] = "error"
                    respuesta['code'] = 422
                    respuesta['resultado']['estado'] = "error"
                    respuesta['resultado']['mensaje'] = "No fue posible procesar la solicitud de emitir la factura a Titanio."
                    respuesta['resultado']['datos']= {"mensaje_titanio":mensaje}
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
            

            except requests.exceptions.Timeout:
                respuesta["status"] = "error"
                respuesta["code"] = 504
                respuesta["resultado"]["estado"] = "error"
                respuesta["resultado"]["mensaje"] = "Timeout al emitir la factura en Titanio."
                respuesta["resultado"]["datos"] = {"detalle": "El servicio de emisión no respondió en el tiempo configurado."}
                return respuesta
            except requests.exceptions.RequestException as e:
                respuesta["status"] = "error"
                respuesta["code"] = 502
                respuesta["resultado"]["estado"] = "error"
                respuesta["resultado"]["mensaje"] = "Error de comunicación con Titanio al emitir la factura."
                respuesta["resultado"]["datos"] = {"detalle": str(e)}
                return respuesta
            except Exception as e:
                #print("Ocurrió un error al emitir la factura: ", e)
                respuesta['status'] = "error"
                respuesta['code'] = 422
                respuesta['resultado']['estado'] = "error"
                respuesta['resultado']['mensaje'] = "No fue posible la solicitud de emitir la factura a Titanio."   
                return respuesta

    except requests.exceptions.Timeout:
        respuesta["status"] = "error"
        respuesta["code"] = 504
        respuesta["resultado"]["estado"] = "error"
        respuesta["resultado"]["mensaje"] = "Timeout al emitir la factura en Titanio."
        respuesta["resultado"]["datos"] = {"detalle": "El servicio de emisión no respondió en el tiempo configurado."}
        return respuesta
    except requests.exceptions.RequestException as e:
        respuesta["status"] = "error"
        respuesta["code"] = 502
        respuesta["resultado"]["estado"] = "error"
        respuesta["resultado"]["mensaje"] = "Error de comunicación con Titanio al emitir la factura."
        respuesta["resultado"]["datos"] = {"detalle": str(e)}
        return respuesta

    except Exception as e:
        #print("Ocurrió un error al emitir la factura: ", e)
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

def reemplazar_none(obj):
    if isinstance(obj, dict):
        return {k: reemplazar_none(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [reemplazar_none(item) for item in obj]
    elif obj is None:
        return ""
    #elif isinstance(obj, bool):
    #    return str(obj).lower()
    else:
        return obj

def normalizar_resultado(resultado):
    #print("Contenido:", resultado_normalizado)
    #print("Tipo:", type(resultado_normalizado))
    # Caso 1: resultado completo es LOB
    if LOB_TYPES and isinstance(resultado, LOB_TYPES):
        resultado = resultado.read()
    # Caso 2: resultado es diccionario
    elif isinstance(resultado, dict):
        nuevo_resultado = {}
        for k, v in resultado.items():
            if LOB_TYPES and isinstance(v, LOB_TYPES):
                nuevo_resultado[k] = v.read()
            else:
                nuevo_resultado[k] = v
        resultado = nuevo_resultado
    # Caso 3: resultado es bytes
    elif isinstance(resultado, bytes):
        resultado = resultado.decode("utf-8")
    # Caso 4: si es string, validar si contiene JSON
    if isinstance(resultado, str):
        texto = resultado.strip()
        if texto.startswith("{") or texto.startswith("["):
            try:
                resultado = json.loads(texto)
            except json.JSONDecodeError:
                pass
    # Reemplazar None por ""
    resultado = reemplazar_none(resultado)
    return resultado        

def convertir_a_base64(resultado):
    resultado_normalizado = normalizar_resultado(resultado)
    #print("Contenido normalizado:", json.dumps(resultado_normalizado, ensure_ascii=False))
    # Convertir el objeto Python a string JSON
    json_string = json.dumps(resultado_normalizado, ensure_ascii=False)
    # Convertir a bytes
    json_bytes = json_string.encode("utf-8")
    # Codificar en Base64
    base64_bytes = base64.b64encode(json_bytes)
    # Convertir nuevamente a string
    base64_resultado = base64_bytes.decode("utf-8")
    return base64_resultado
