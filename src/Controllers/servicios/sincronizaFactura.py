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
from Controllers.general.function_mail import enviarCorreo
#from Connect.default_pgbd import conexion ## activar para conexión por defecto
from Scriptdb.servicios.transaccion import * 
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
def sincronizeBill(req=""):
    conexion = None
    params = None
    respuesta = []
    notificacion = {
        "exec": False,
        "estado": "sin_ejecutar",
        "message": "No se ejecutó la notificación"
    }
    try:
        #token = request.headers['Authorization'].split(" ")[1]
        #user=validate_token(token,output=True)
        conexion=switchconn('oracle')
        params=req.get('parametros')
        try:
            corrigeEnviosConError(conexion, params)
        except Exception:
            pass
        envio = consultaSolicitudes(conexion,params)
        exec_flag = envio.get("exec")
        # Normalizar exec
        if isinstance(exec_flag, str):
            exec_flag = exec_flag.lower() == "true"
        else:
            exec_flag = bool(exec_flag)

        data = envio.get("data") or []
        respuestas = []
        for registro in data:
            try:
                if not isinstance(registro, dict):
                    continue

                estado_envio = registro.get("ENV_STATE_SEND")
                tr_id = registro.get("ENV_TR_ID")
                # Solo procesar si cumple condición
                if estado_envio == "S":
                    # Construir request dinámico si lo necesitas
                    solicitud = {
                                "secuencia": registro.get("FAC_SECUENCIA"),
                                "vigencia": registro.get("FAC_SECUENCIA_ANO"),
                                "transaccion": registro.get("ENV_TR_ID"),  # ajusta si aplica
                                "id_factura": registro.get("ENV_FAC_ID")  # ajusta si aplica
                                }
                    # print(solicitud)
                    # 1. Transformar
                    resultado = transformData(req, solicitud)
                    # 3. Cargar
                    response = loadData(resultado, conexion)
                    #print(response)
                    respuestas.append(response)
                #else:
                   # print(f"TR_ID {tr_id} no requiere procesamiento")

            except Exception as e:
                #print(f"Error procesando TR_ID {tr_id}: {e}")
                respuestas.append({
                                    "estado": "error",
                                    "mensaje": "Error en procesamiento",
                                    "resultado": {
                                        "detalle": str(e)
                                    }
                                })

        respuesta = respuestas
    except Exception as e:
        #print("Ocurrió un error en sincronizar el api de reportes: ", e)   
        respuesta = {"Error":f"No fue posible procesar la emisión de la factura a Titanio, {e}"}
    finally:
        if conexion is not None:
            try:
                notificacion = notificaEnviosActivosConError(conexion, params)
            except Exception as e:
                notificacion = {
                    "exec": False,
                    "estado": "error",
                    "error": str(e)
                }
        else:
            notificacion = {
                "exec": False,
                "estado": "sin_conexion",
                "message": "No fue posible consultar los envíos con error para notificar"
            }
    return {
        "sincronizacion": respuesta,
        "notificacion": notificacion
    }
    #finally:
    #    conexion.close()

def corrigeEnviosConError(conexion, datos=None):
    sin_respuesta = actualizaEnviosSinRespuestaTitanio(conexion, datos)
    duplicados = corrigeEnviosDocumentoDuplicado(conexion, datos)
    duplicados_ok = (
        isinstance(duplicados, dict)
        and (
            duplicados.get("exec") is True
            or duplicados.get("message") == "No se encontraron registros"
        )
    )

    return {
        "exec": (
            isinstance(sin_respuesta, dict)
            and sin_respuesta.get("exec") is True
            and duplicados_ok
        ),
        "data": {
            "sin_respuesta_titanio": sin_respuesta,
            "documento_duplicado": duplicados
        }
    }

def corrigeEnviosDocumentoDuplicado(conexion, datos=None):
    envios = consultaEnviosDocumentoDuplicado(conexion, datos)
    if not isinstance(envios, dict) or envios.get("exec") is not True:
        return envios

    respuestas = []
    for envio in envios.get("data") or []:
        error = envio.get("ENV_ERROR", "")
        if hasattr(error, "read"):
            error = error.read()

        match = re.search(r"TR_ID\s*:\s*(\d+)", str(error or ""), re.IGNORECASE)
        if not match:
            continue

        respuesta = actualizaEnvioDocumentoDuplicado(
            conexion,
            {
                "envio": envio.get("ENV_ID"),
                "id_transaccion": match.group(1)
            }
        )
        respuestas.append(respuesta)

    return {
        "exec": True,
        "data": respuestas,
        "total": len(respuestas)
    }

def notificaEnviosActivosConError(conexion, datos=None):
    consulta = consultaEnviosActivosConError(conexion, datos)
    if not isinstance(consulta, dict) or consulta.get("exec") is not True:
        return {
            "exec": False,
            "estado": "error_consulta" if isinstance(consulta, dict) and consulta.get("error") else "sin_notificacion",
            "message": consulta.get("message") if isinstance(consulta, dict) else "No fue posible consultar los envíos con error",
            "error": consulta.get("error") if isinstance(consulta, dict) else None
        }

    resumen = {}
    for envio in consulta.get("data") or []:
        if not isinstance(envio, dict):
            continue

        error = envio.get("ENV_ERROR")
        if hasattr(error, "read"):
            error = error.read()

        error = str(error or "").strip() or "Sin detalle de error"
        factura = str(
            envio.get("FAC_DOCUMENT_ID")
            or envio.get("FAC_SECUENCIA")
            or envio.get("ENV_FAC_ID")
            or "Sin número"
        ).strip()
        vigencia = str(envio.get("FAC_SECUENCIA_ANO") or "").strip()
        if vigencia and not envio.get("FAC_DOCUMENT_ID"):
            factura = f"{factura}/{vigencia}"

        if error not in resumen:
            resumen[error] = []
        resumen[error].append(factura)

    if not resumen:
        return {
            "exec": True,
            "estado": "sin_notificacion",
            "message": "No hay envíos activos con errores"
        }

    total = sum(len(facturas) for facturas in resumen.values())
    lineas = [
        "Notificación de envíos de facturación electrónica",
        "",
        f"Cantidad total de envíos activos con errores: {total}",
        "",
        "Detalle por error:"
    ]
    for error, facturas in sorted(resumen.items(), key=lambda item: len(item[1]), reverse=True):
        lineas.append(f"- {len(facturas)}: {error}")
        lineas.append(f"  Facturas: {', '.join(facturas)}")

    lineas.extend([
        "",
        "Esta es una notificación automatizada del servicio de gestión de facturas."
    ])

    respuesta = enviarCorreo(
        "Facturación electrónica - envíos activos con errores",
        "\n".join(lineas)
    )
    respuesta["total_registros_error"] = total
    respuesta["total_tipos_error"] = len(resumen)
    return respuesta

'''Funcion que realiza las consulta de los datos de las fuentes de datos'''
def extractData(busqueda="",conexion=""):
    try:
        return [] 
    except Exception as e:
        return []  

def normalizaClaveMetadata(valor):
    return re.sub(r"[^A-Z0-9]", "", str(valor or "").upper())

def obtieneValorMetadata(metadata, *claves):
    claves_normalizadas = {normalizaClaveMetadata(clave) for clave in claves}

    if isinstance(metadata, dict):
        for clave, valor in metadata.items():
            if normalizaClaveMetadata(clave) in claves_normalizadas and valor not in [None, ""]:
                return valor

    if isinstance(metadata, list):
        for item in metadata:
            if not isinstance(item, dict):
                continue

            campo = (
                item.get("campo")
                or item.get("nombre")
                or item.get("name")
                or item.get("key")
                or item.get("codigo")
            )
            valor = item.get("valor")
            if valor in [None, ""]:
                valor = item.get("value") or item.get("dato")

            if normalizaClaveMetadata(campo) in claves_normalizadas and valor not in [None, ""]:
                return valor

            for clave, valor_directo in item.items():
                if normalizaClaveMetadata(clave) in claves_normalizadas and valor_directo not in [None, ""]:
                    return valor_directo

    return ""

def extraeDetalleTitanio(search_result):
    detalle = {
        "estado_dian": None,
        "fecha_emision": "",
        "cufe": "",
        "qr": ""
    }

    if not isinstance(search_result, dict):
        return detalle

    detalle_transaccion = search_result.get('detalleTransaccion') or {}
    estados = ""
    if isinstance(detalle_transaccion, dict):
        estados = detalle_transaccion.get('estado_id', '')
    if not estados:
        estados = search_result.get("estado_id", "")
    lista_estados = [x.strip() for x in str(estados).split(",") if x.strip()]
    if len(lista_estados) >= 4:
        detalle["estado_dian"] = lista_estados[3]

    metadata = search_result.get('detalleMetadata', [])
    detalle["fecha_emision"] = (
        obtieneValorMetadata(metadata, "FECHA", "FECHA_EMISION", "FECHAEMISION")
        or search_result.get("fecha_emision")
        or search_result.get("fecha")
        or ""
    )
    detalle["cufe"] = (
        obtieneValorMetadata(metadata, "CUFE", "CUDE")
        or search_result.get("cufe")
        or search_result.get("CUFE")
        or ""
    )
    detalle["qr"] = (
        obtieneValorMetadata(metadata, "QR", "QRCODE", "QR_CODE", "CODIGO_QR", "CODIGOQR")
        or search_result.get("qr")
        or search_result.get("QR")
        or search_result.get("QRCode")
        or search_result.get("qr_code")
        or ""
    )

    return detalle

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
                recibo = req.get("parametros", {})
                param_search = {
                   "token": acceso.get('token'),
                    "transaccion_id": resultado.get("transaccion")
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

                    detalle_titanio = extraeDetalleTitanio(search_result)
                    estado_intento = str(detalle_titanio.get("estado_dian") or "")
                    if "Rechazado" in estado_intento:
                        break
                    if (
                        "Validado" in estado_intento
                        and detalle_titanio.get("fecha_emision")
                        and detalle_titanio.get("cufe")
                        and detalle_titanio.get("qr")
                    ):
                        break
                # Inicializar variables
                estado_dian = None
                error_dian = ""
                fecha_emision = ""
                cufe = ""
                qr = ""

                # Validar estructura
                if isinstance(search_result, dict):
                    detalle_titanio = extraeDetalleTitanio(search_result)
                    estado_dian = detalle_titanio.get("estado_dian")
                    
                    if estado_dian:
                        if "Rechazado" in estado_dian:
                            error_dian = (search_result.get("error") or search_result.get("mensaje") or "Documento rechazado por la DIAN" )
                            param_del = { "token": acceso.get('token'),
                                          "transaccion": resultado.get("transaccion")
                                        }
                            #print(param_del)            
                            del_trans = "/PDE/public/api/PDE/borrar"
                            del_result = consumepost_trans(host_titanio, del_trans, param_del)
                        elif "Validado" in estado_dian:
                            fecha_emision = detalle_titanio.get("fecha_emision", "")
                            cufe = detalle_titanio.get("cufe", "")
                            qr = detalle_titanio.get("qr", "")
                #else:
                #    print("⚠️ search_result no es válido:", search_result)
                datos_transaccion = {
                    "vigencia": resultado.get("vigencia"),
                    "secuencia": resultado.get("secuencia"),
                    "id_factura": resultado.get("id_factura"),
                    "estado_dian": estado_dian,
                    "error_emision": error_dian,
                    "id_transaccion": resultado.get("transaccion"),
                    "fecha_emision": fecha_emision, 
                    "cufe": cufe,
                    "qr_cod": qr
                }
                #print(datos_transaccion)
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
                respuesta["resultado"]["mensaje"] = "Timeout al verificar la factura en Titanio."
                respuesta["resultado"]["datos"] = {"detalle": "El servicio de emisión no respondió en el tiempo configurado."}
                return respuesta
            except requests.exceptions.RequestException as e:
                respuesta["status"] = "error"
                respuesta["code"] = 502
                respuesta["resultado"]["estado"] = "error"
                respuesta["resultado"]["mensaje"] = "Error de comunicación con Titanio al verificar la factura."
                respuesta["resultado"]["datos"] = {"detalle": str(e)}
                return respuesta
            except Exception as e:
                #print("Ocurrió un error al emitir la factura: ", e)
                respuesta['status'] = "error"
                respuesta['code'] = 422
                respuesta['resultado']['estado'] = "error"
                respuesta['resultado']['mensaje'] = "No fue posible la solicitud de verificar la factura a Titanio."   
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

        def ok():
            return {"estado": "success", "detalle": "ok"}

        def err(msg):
            return {"estado": "error", "detalle": msg}

        # Validación básica
        if not isinstance(resultado, dict):
            return {
                "estado": "error",
                "mensaje": "Formato de respuesta inválido",
                "datos": {},
                "trazabilidad": {
                    "registro_envio": err("formato"),
                    "actualizacion_factura": err("no ejecutado")
                },
                "code": 500
            }

        status = resultado.get("status")
        code = resultado.get("code", 500)
        datos = resultado.get("resultado", {}).get("datos", {})

        trazabilidad = {
            "registro_envio": ok(),
            "actualizacion_factura": ok()
        }

        # Error desde Titanio
        if status != "success":
            trazabilidad["registro_envio"] = err("emisión")
            trazabilidad["actualizacion_factura"] = err("no ejecutado")

            return {
                "estado": "error",
                "mensaje": "Error en emisión de factura",
                "datos": datos,
                "trazabilidad": trazabilidad,
                "code": 422
            }

        # Validar datos
        if not isinstance(datos, dict) or not datos:
            trazabilidad["registro_envio"] = err("sin datos")
            trazabilidad["actualizacion_factura"] = err("no ejecutado")

            return {
                "estado": "error",
                "mensaje": "Sin datos para procesar",
                "datos": {},
                "trazabilidad": trazabilidad,
                "code": 500
            }

        estado_dian = str(datos.get("estado_dian", "")).strip()

        # Estado interno
        if "Rechazado" in estado_dian:
            datos["estado"] = "E"
        elif "Validado" in estado_dian:
            datos["estado"] = "G"
        else:
            datos["estado"] = "S"

        # =========================
        # 1. REGISTRO ENVÍO
        # =========================
        try:
            envio = actualizaSolicitud(conexion, datos)
            if not isinstance(envio, dict) or not envio:
                trazabilidad["registro_envio"] = err("insert")
                return {
                    "estado": "error",
                    "mensaje": "Error registrando envío",
                    "datos": datos,
                    "trazabilidad": trazabilidad,
                    "code": 500
                }
            trazabilidad["registro_envio"] = ok()

        except Exception as e:
            trazabilidad["registro_envio"] = err("insert")
            return {
                "estado": "error",
                "mensaje": "Excepción registrando envío",
                "datos": datos,
                "trazabilidad": trazabilidad,
                "code": 500
            }
        # =========================
        # 2. ACTUALIZAR FACTURA
        # =========================
        if datos.get("estado") == "G":
            if datos.get("cufe") and datos.get("fecha_emision"):
                try:
                    resp_cufe = registroCUFE(conexion, datos)
                    if not isinstance(resp_cufe, dict) or resp_cufe.get("exec") is not True:
                        trazabilidad["actualizacion_factura"] = err("update")
                        return {
                            "estado": "error",
                            "mensaje": "Error actualizando factura",
                            "datos": datos,
                            "trazabilidad": trazabilidad,
                            "code": 500
                        }
                    trazabilidad["actualizacion_factura"] = ok()

                except Exception:
                    trazabilidad["actualizacion_factura"] = err("update")
                    return {
                        "estado": "error",
                        "mensaje": "Excepción actualizando factura",
                        "datos": datos,
                        "trazabilidad": trazabilidad,
                        "code": 500
                    }
            else:
                trazabilidad["actualizacion_factura"] = err("datos incompletos")
                return {
                    "estado": "error",
                    "mensaje": "Faltan datos para actualizar factura",
                    "datos": datos,
                    "trazabilidad": trazabilidad,
                    "code": 500
                }

        # =========================
        # RESPUESTA FINAL
        # =========================
        return {
            "estado": "success",
            "mensaje": f"Factura procesada ({estado_dian})",
            "datos": datos,
            "trazabilidad": trazabilidad,
            "code": code if isinstance(code, int) else 200
        }

    except Exception as e:
        return {
            "estado": "error",
            "mensaje": "Error general en procesamiento",
            "datos": {},
            "trazabilidad": {
                "registro_envio": {"estado": "error", "detalle": "general"},
                "actualizacion_factura": {"estado": "error", "detalle": "general"}
            },
            "code": 500
        }


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
