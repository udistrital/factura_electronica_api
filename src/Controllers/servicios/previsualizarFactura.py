import json
import logging
import os
import sys

from flask import Response

p = os.path.abspath('src')
sys.path.insert(1, p)

from Controllers.servicios.emitirFactura import normalizar_resultado, switchconn
from Scriptdb.servicios.facturas import consultaRegistroFactura

logger = logging.getLogger(__name__)


def json_response(payload, status_code=200):
    response = Response(
        json.dumps(payload, ensure_ascii=False),
        content_type="application/json; charset=utf-8"
    )
    response.status_code = status_code
    return response


def extractPreviewData(busqueda="", conexion=""):
    recibo = busqueda.get('parametros', {}) if isinstance(busqueda, dict) else {}
    id_factura = recibo.get("id_factura")

    if not id_factura:
        return {
            "estado": "error",
            "mensaje": "El parámetro id_factura es obligatorio para generar el JSON de la factura.",
            "datos": {
                "id_factura": id_factura,
                "secuencia": recibo.get("secuencia"),
                "vigencia": recibo.get("vigencia")
            }
        }, 400

    data = consultaRegistroFactura(conexion, recibo)

    if not isinstance(data, dict):
        return {
            "estado": "error",
            "mensaje": "La consulta de factura no retornó una estructura válida.",
            "datos": {"respuesta": data}
        }, 500

    if data.get("exec") is not True:
        return {
            "estado": "error",
            "mensaje": data.get("message") or "No fue posible consultar el JSON de la factura.",
            "datos": {
                "detalle": data.get("error", ""),
                "id_factura": id_factura,
                "secuencia": recibo.get("secuencia"),
                "vigencia": recibo.get("vigencia")
            }
        }, 404 if data.get("message") else 500

    registros = data.get("data") or []
    if not registros:
        return {
            "estado": "error",
            "mensaje": "No se encontraron registros para la factura.",
            "datos": {
                "id_factura": id_factura,
                "secuencia": recibo.get("secuencia"),
                "vigencia": recibo.get("vigencia")
            }
        }, 404

    json_result = registros[0].get("JSON_RESULT")
    if json_result is None:
        return {
            "estado": "error",
            "mensaje": "La consulta no retornó el campo JSON_RESULT.",
            "datos": {"campos": list(registros[0].keys())}
        }, 500

    if hasattr(json_result, "read"):
        json_result = json_result.read()

    datos = json.loads(json_result) if isinstance(json_result, str) else json_result
    return normalizar_resultado(datos), 200


'''Funcion controladora para inspeccionar el JSON de la factura antes de codificarlo'''
def previewBill(req=""):
    conexion = None
    try:
        conexion = switchconn('oracle')
        factura_json, status_code = extractPreviewData(req, conexion)

        if status_code != 200:
            return json_response(factura_json, status_code)

        #print(json.dumps(factura_json, ensure_ascii=False, indent=2))
        resp = {
            "estado": "success",
            "mensaje": "JSON de factura generado antes de codificar en base64.",
            "datos": factura_json
        }
        return json_response(resp, 200)
    except Exception as e:
        logger.exception("EMISION: error generando vista previa del JSON de factura")
        resp = {
            "estado": "error",
            "mensaje": f"No fue posible generar el JSON de la factura, {e}",
            "datos": {}
        }
        return json_response(resp, 500)
    finally:
        if conexion:
            try:
                conexion.close()
            except Exception:
                logger.exception("EMISION: error cerrando/devolviendo conexion Oracle al pool")
