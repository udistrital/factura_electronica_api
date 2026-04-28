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
def emitBill(req=""):
    try:
        #token = request.headers['Authorization'].split(" ")[1]
        #user=validate_token(token,output=True)
        conexion=switchconn('oracle')
        params=req.get('parametros')
        envio = consultaEnvio(conexion,params)
        exec_flag = envio.get("exec")
        # Normalizar exec
        if isinstance(exec_flag, str):
            exec_flag = exec_flag.lower() == "true"
        else:
            exec_flag = bool(exec_flag)

        data = envio.get("data") or []
        registro = data[0] if isinstance(data, list) and len(data) > 0 else {}
        estado_envio = registro.get("ENV_STATE_SEND")
        tr_id = registro.get("ENV_TR_ID")
        # consulat coidgo de factura para titanio
        code = consultaCodigoFactura(conexion,'')
        datacode = code.get("data") or []
        req['parametros']['tipo_transaccion']=datacode[0]["TD_TR_TYPE_COD"]
        
        if not exec_flag or estado_envio == "C":
            #print("Se envia")
            registros = extractData(req, conexion)
            resultado = transformData(req, registros)
            respuesta = loadData(resultado, conexion)
            #respuesta = registros
        elif estado_envio == "E":
            #print("NO Se envia")
            resultado = {
                "status": "error",
                "code": "422",
                "resultado": {
                    "estado": "error",
                    "mensaje": "No fue posible procesar la emisión de la factura a Titanio",
                    "datos": {
                        "detalle": "Ya existe una solicitud de emisión de la factura a Titanio, con errores que se deben corregir"
                    }
                }
            }
            respuesta = loadData(resultado, conexion)
        else:
            #print("NO Se envia")
            resultado = {
                "status": "error",
                "code": "422",
                "resultado": {
                    "estado": "error",
                    "mensaje": "No fue posible procesar la emisión de la factura a Titanio",
                    "datos": {
                        "detalle": f"Ya existe una emisión vigente de la factura, con el número de transacción {tr_id}"
                    }
                }
            }
            respuesta = loadData(resultado, conexion)

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
        return datos
    except Exception as e:
        #print("Ocurrió un error al rescatar datos del api de reportes: ", e) 
        return []  

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

        if resultado :     
            ## loguearse a plataforma Titanio
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
                    param_bill={
                            "token": acceso['token'],
                            "tr_tipo_id": req['parametros']['tipo_transaccion'],
                            "data": factura_base64
                        }    
                    #print(param_bill)
                    emitir_titanio="/PDE/public/api/PDE/emitir_v2"
                    #print(emitir_titanio)
                    factura=consumepost_trans(host_titanio,emitir_titanio,param_bill)
                    '''
                    factura = { 'error_id' : 0,
                                'error_msg' : 'Se realizo con exito la operacion.',
                                'mensaje' : ' ----------------------------\r\nMensajes de Conversión a Dataset:\r\nIniciando Conversión\r\nExcepción de conversión: \r\nEtiqueta final inesperada. línea 2, posición 3.\r\n\r\n----------------------------\r\nMensajes de la validación del Dataset:\r\nAdvertencia:[FAB36] El código QR (EXT/QRCode) se corrigió\r\n----------------------------\r\nMensajes de Conversión a UBL:\r\nIniciando Conversión\r\nTerminando Conversión\r\n\r\n----------------------------\r\nMensajes de la validación del UBL:\r\nXML Válido:\r\n----------------------------\r\nMensajes de Agregar a Cola:\r\nSe agrego a la cola con exito.\r\n.',
                                'tr_id' : 3873108,
                                'cufe': 'fc4a8bb60d850f198e4430f5cb0214ee25683d25b850cde840ce3795e83d959a25a5df61672c4994dd539071332f190c',
                                'qr': ' NumFac: SETP90000507\r\nFe...',
                                }
                    '''
                    '''
                    factura = {'error_id': 310, 'error_msg': '', 
                               'mensaje': "DOC ID:[SETT11581]\r\nAdvertencia:  [FAB05b] La resolución (EXT/InvoiceAuthorization) se corrigió\r\nAdvertencia:  [FAB07b] La fecha desde (EXT/StartDate) se corrigió\r\nAdvertencia:  [FAB08b] La fecha hasta (EXT/EndDate) se corrigió\r\nAdvertencia:  [FAB11b] El Rango de numeración Desde (EXT/From) se corrigió\r\nAdvertencia:  [FAB12b] El Rango de numeración Hasta (EXT/To) se corrigió\r\nAdvertencia:  [FAB36] El código QR (EXT/QRCode) se corrigió\r\nAdvertencia:  [FAD03] La versión del perfil (FAC/ProfileID) se corrigió\r\nAdvertencia:  [FAB10a] El prefijo de la resolución debe coincidir con el prefijo (Document/ASP/CorporateRegistrationScheme_ID). Será corregido\r\nAdvertencia:  [FAK26] La Responsabilidad Fiscal del contribuyente en (Document/ACP/TaxLevelCode) () fué reemplazado por R-99-PN\r\nError:  [FAV06] El Valor Total en Document/IVL[4]/LineExtensionAmount no es un número válido\r\nError:  [FABB02] El Precio en Document/IVL[4]/PriceAmount no es un número válido\r\nError:  [FAW01] Si el valor indicado en Document/IVL[4]/LineExtensionAmount es '0' debe indicar un valor en Document/IVL[4]/AlternativeConditionPrice_PriceAmount\r\nError:  [FAU02] El Total Valor Bruto Antes de Tributos en Document/TOT/LineExtensionAmount (116300) debe coincidir con la suma del mismo valor en todos los renglones (641300)\r\n", 
                               'tr_id': 0,
                               'cufe': None, 'qr': None}
                    '''           
                    #print(factura)
                    recibo = req.get("parametros", {})
                    # se verifica si se presento error en la solicitud de emision d ela factura
                    if factura.get("error_id") > 0:
                        mensaje = factura.get("mensaje") if factura.get("mensaje") else factura.get("error_msg")
                        datos_transaccion = {      "vigencia": recibo.get("vigencia"),
                                                    "secuencia": recibo.get("secuencia"),
                                                    "identificacion": recibo.get("identificacion"),
                                                    "estado": "E",
                                                    "estado_dian": "",
                                                    "error_emision": mensaje,
                                                    "id_transaccion": factura.get("tr_id"),
                                                    "fecha_emision": "",
                                                    "cufe": "",
                                                    "qr_cod": ""
                                                }
                        respuesta['status'] = "error"
                        respuesta['code'] = 422
                        respuesta['resultado']['estado'] = "error"
                        respuesta['resultado']['mensaje'] = "No fue posible procesar la solicitud de emitir la factura a Titanio."
                        respuesta['resultado']['datos']= datos_transaccion
                        
                        return respuesta
                    else:
                        #recibo = req.get("parametros", {})
                        param_search = {
                            "token": acceso.get('token'),
                            "transaccion_id": factura.get("tr_id")
                        }
                        search_trans = "/PDE/public/api/PDE/detalle"
                        #search_result = consumepost_trans(host_titanio, search_trans, param_search)
                        max_intentos = 3          # número de intentos
                        espera_segundos = 5       # tiempo entre intentos
                        search_result = None
                        for intento in range(max_intentos):
                            time.sleep(espera_segundos)
                            search_result = consumepost_trans(host_titanio, search_trans, param_search)
                            #print(f"Intento {intento+1}:", search_result)
                            if not isinstance(search_result, dict):
                                continue
                            estados = search_result.get('detalleTransaccion', {}).get('estado_id', '')
                            if estados:
                                break

                        # Inicializar variables
                        estado_dian = None
                        error_dian = ""
                        fecha_emision = ""
                        cufe = ""
                        qr = ""

                        # Validar estructura
                        if isinstance(search_result, dict):
                            estados = search_result.get('detalleTransaccion', {}).get('estado_id', '')
                            lista_estados = [x.strip() for x in estados.split(",") if x.strip()]
                            if len(lista_estados) >= 4:
                                estado_dian = lista_estados[3]
                            metadata = search_result.get('detalleMetadata', [])
                            metadata_dict = {
                                item.get("campo"): item.get("valor")
                                for item in metadata if isinstance(item, dict)
                            }

                            if estado_dian:
                                if "Rechazado" in estado_dian:
                                    error_dian = (search_result.get("error") or search_result.get("mensaje") or "Documento rechazado por la DIAN" )
                                    param_del = { "token": acceso.get('token'),
                                                "transaccion": factura.get("tr_id")
                                                }
                                    #print(param_del)            
                                    del_trans = "/PDE/public/api/PDE/borrar"
                                    del_result = consumepost_trans(host_titanio, del_trans, param_del)
                                elif "Validado" in estado_dian:
                                    fecha_emision = metadata_dict.get("FECHA", "")
                                    cufe = metadata_dict.get("CUFE", "")
                                    qr = metadata_dict.get("QR", "")
                        #else:
                        #    print("⚠️ search_result no es válido:", search_result)

                        datos_transaccion = {
                            "vigencia": recibo.get("vigencia"),
                            "secuencia": recibo.get("secuencia"),
                            "identificacion": recibo.get("identificacion"),
                            "estado_dian": estado_dian,
                            "error_emision": error_dian,
                            "id_transaccion": factura.get("tr_id"),
                            "fecha_emision": fecha_emision, 
                            "cufe": cufe,
                            "qr_cod": qr
                        }

                        respuesta['status'] = "success"
                        respuesta['code'] = 200
                        respuesta['resultado']['estado'] = "success"
                        respuesta['resultado']['mensaje'] = (
                            f"Solicitud de generación de factura electrónica en Titanio, con estado {estado_dian}."
                        )
                        respuesta['resultado']['datos'] = datos_transaccion
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
        else:
            #print("Ocurrió un error al emitir la factura: ", e)
            respuesta['status'] = "error"
            respuesta['code'] = 404
            respuesta['resultado']['estado'] = "error"
            respuesta["resultado"]["mensaje"] = "Error al solicitar la emisión de la factura en Titanio."
            respuesta["resultado"]["datos"] = {"detalle": "No existen datos validos del recibo con el consecutivo y vigencia enviados."}
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


def loadData(resultado, conexion=""):
    try:
        #print("Resultado recibido:", resultado)
        def estado_traza_ok():
            return {"estado": "success", "detalle": "ok"}

        def estado_traza_error(detalle):
            return {"estado": "error", "detalle": detalle}

        # Validación básica
        if not isinstance(resultado, dict):
            resp = {
                "estado": "error",
                "mensaje": "La respuesta recibida no tiene un formato válido.",
                "datos": {},
                "trazabilidad": {
                    "registro_envio": estado_traza_error("formato inválido"),
                    "actualizacion_factura": estado_traza_error("no ejecutado")
                }
            }
            response = Response(
                json.dumps(resp, ensure_ascii=False),
                content_type="application/json; charset=utf-8"
            )
            response.status_code = 500
            return response

        status = resultado.get("status")
        code = resultado.get("code", 500)
        datos = resultado.get("resultado", {}).get("datos", {})
        mensaje_origen = resultado.get("resultado", {}).get("mensaje", "")

        trazabilidad = {
            "registro_envio": estado_traza_ok(),
            "actualizacion_factura": estado_traza_ok()
        }

        # Si Titanio devolvió error
        if status != "success":
            # . Registrar envío
            try:
                if code != 404:
                    envio = registroEnvio(conexion, datos)
                    if not isinstance(envio, dict) or envio.get("exec") is not True:
                        trazabilidad["registro_envio"] = estado_traza_error("No registrado envío")
                        trazabilidad["actualizacion_factura"] = estado_traza_error("no ejecutado")
                        resp = {
                            "estado": "error",
                            "mensaje": "No fue posible registrar el envío de la factura.",
                            "datos": datos,
                            "trazabilidad": trazabilidad
                        }
                        response = Response(
                            json.dumps(resp, ensure_ascii=False),
                            content_type="application/json; charset=utf-8"
                        )
                        response.status_code = 500
                        return response
                
                trazabilidad["registro_envio"] = estado_traza_error("emisión rechazada")
                trazabilidad["actualizacion_factura"] = estado_traza_error("no ejecutado")
                resp = {
                    "estado": "error",
                    "mensaje": "No fue posible procesar la emisión de la factura.",
                    "datos": resultado.get("resultado", {}).get("datos", {}),
                    "trazabilidad": trazabilidad
                }
                response = Response(
                    json.dumps(resp, ensure_ascii=False),
                    content_type="application/json; charset=utf-8"
                )
                response.status_code = code if isinstance(code, int) else 422
                return response

            except Exception:
                trazabilidad["registro_envio"] = estado_traza_error("no registrado envío")
                trazabilidad["actualizacion_factura"] = estado_traza_error("no ejecutado")
                resp = {
                    "estado": "error",
                    "mensaje": "Ocurrió un error al registrar el envío de la factura.",
                    "datos": datos,
                    "trazabilidad": trazabilidad
                }
                response = Response(
                    json.dumps(resp, ensure_ascii=False),
                    content_type="application/json; charset=utf-8"
                )
                response.status_code = 500
                return response    


        # Validar datos mínimos
        if not isinstance(datos, dict) or not datos:
            trazabilidad["registro_envio"] = estado_traza_error("sin datos")
            trazabilidad["actualizacion_factura"] = estado_traza_error("no ejecutado")

            resp = {
                "estado": "error",
                "mensaje": "La respuesta exitosa no contiene datos para registrar.",
                "datos": {},
                "trazabilidad": trazabilidad
            }
            response = Response(
                json.dumps(resp, ensure_ascii=False),
                content_type="application/json; charset=utf-8"
            )
            response.status_code = 500
            return response

        estado_dian = str(datos.get("estado_dian", "")).strip()
        # Estado interno
        if "Rechazado" in estado_dian:
            datos["estado"] = "E"
        elif "Validado" in estado_dian:
            datos["estado"] = "G"
        else:
            datos["estado"] = "S"

        # 1. Actualizar envío anterior si existe
        try:
            envioant = actualizaEnvio(conexion, datos)
            # No bloquear si no encontró registros previos
            if isinstance(envioant, dict) and envioant.get("exec") is False:
                msg = str(envioant.get("error", "")).lower()
                if msg and "no se encontraron" not in msg and "sin registros" not in msg and "no data found" not in msg:
                    trazabilidad["registro_envio"] = estado_traza_error("actualización previa")
                    trazabilidad["actualizacion_factura"] = estado_traza_error("no ejecutado")

                    resp = {
                        "estado": "error",
                        "mensaje": "No fue posible actualizar el envío anterior.",
                        "datos": datos,
                        "trazabilidad": trazabilidad
                    }
                    response = Response(
                        json.dumps(resp, ensure_ascii=False),
                        content_type="application/json; charset=utf-8"
                    )
                    response.status_code = 500
                    return response

        except Exception:
            trazabilidad["registro_envio"] = estado_traza_error("actualización previa")
            trazabilidad["actualizacion_factura"] = estado_traza_error("no ejecutado")
            resp = {
                "estado": "error",
                "mensaje": "Ocurrió un error al actualizar el envío anterior.",
                "datos": datos,
                "trazabilidad": trazabilidad
            }
            response = Response(
                json.dumps(resp, ensure_ascii=False),
                content_type="application/json; charset=utf-8"
            )
            response.status_code = 500
            return response

        # 2. Registrar envío
        try:
            envio = registroEnvio(conexion, datos)
            if not isinstance(envio, dict) or envio.get("exec") is not True:
                trazabilidad["registro_envio"] = estado_traza_error("insert envío")
                trazabilidad["actualizacion_factura"] = estado_traza_error("no ejecutado")
                resp = {
                    "estado": "error",
                    "mensaje": "No fue posible registrar el envío de la factura.",
                    "datos": datos,
                    "trazabilidad": trazabilidad
                }
                response = Response(
                    json.dumps(resp, ensure_ascii=False),
                    content_type="application/json; charset=utf-8"
                )
                response.status_code = 500
                return response
            trazabilidad["registro_envio"] = estado_traza_ok()

        except Exception:
            trazabilidad["registro_envio"] = estado_traza_error("insert envío")
            trazabilidad["actualizacion_factura"] = estado_traza_error("no ejecutado")
            resp = {
                "estado": "error",
                "mensaje": "Ocurrió un error al registrar el envío de la factura.",
                "datos": datos,
                "trazabilidad": trazabilidad
            }
            response = Response(
                json.dumps(resp, ensure_ascii=False),
                content_type="application/json; charset=utf-8"
            )
            response.status_code = 500
            return response

        # 3. Actualizar factura (CUFE/QR/fecha) si aplica
        if datos["estado"] == "G":
            if datos.get("cufe") and datos.get("qr_cod") and datos.get("fecha_emision"):
                try:
                    cufe_resp = registroCUFE(conexion, datos)
                    if not isinstance(cufe_resp, dict) or cufe_resp.get("exec") is not True:
                        trazabilidad["actualizacion_factura"] = estado_traza_error("update factura")
                        resp = {
                            "estado": "error",
                            "mensaje": "Se registró el envío, pero no fue posible actualizar la factura.",
                            "datos": datos,
                            "trazabilidad": trazabilidad
                        }
                        response = Response(
                            json.dumps(resp, ensure_ascii=False),
                            content_type="application/json; charset=utf-8"
                        )
                        response.status_code = 500
                        return response
                    trazabilidad["actualizacion_factura"] = estado_traza_ok()

                except Exception:
                    trazabilidad["actualizacion_factura"] = estado_traza_error("update factura")
                    resp = {
                        "estado": "error",
                        "mensaje": "Se registró el envío, pero ocurrió un error al actualizar la factura.",
                        "datos": datos,
                        "trazabilidad": trazabilidad
                    }
                    response = Response(
                        json.dumps(resp, ensure_ascii=False),
                        content_type="application/json; charset=utf-8"
                    )
                    response.status_code = 500
                    return response
            else:
                trazabilidad["actualizacion_factura"] = estado_traza_error("datos incompletos")
                resp = {
                    "estado": "error",
                    "mensaje": "La factura fue validada, pero no llegaron datos suficientes para actualizar la factura.",
                    "datos": datos,
                    "trazabilidad": trazabilidad
                }
                response = Response(
                    json.dumps(resp, ensure_ascii=False),
                    content_type="application/json; charset=utf-8"
                )
                response.status_code = 500
                return response
        else:
            trazabilidad["actualizacion_factura"] = estado_traza_error("No se valido la factura")

        # Respuesta final resumida
        resp = {
            "estado": "success",
            "mensaje": "Proceso ejecutado correctamente.",
            "datos": datos,
            "trazabilidad": trazabilidad
        }
        response = Response(
            json.dumps(resp, ensure_ascii=False),
            content_type="application/json; charset=utf-8"
        )
        response.status_code = code if isinstance(code, int) else 200
        return response

    except Exception:
        resp = {
            "estado": "error",
            "mensaje": "Ocurrió un error en el registro de la emisión de la factura.",
            "datos": {},
            "trazabilidad": {
                "registro_envio": {"estado": "error", "detalle": "error general"},
                "actualizacion_factura": {"estado": "error", "detalle": "error general"}
            }
        }
        response = Response(
            json.dumps(resp, ensure_ascii=False),
            content_type="application/json; charset=utf-8"
        )
        response.status_code = 500
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
