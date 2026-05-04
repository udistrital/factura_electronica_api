import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional

import requests

p = os.path.abspath("src")
sys.path.insert(1, p)

from Controllers.general.function_consume import consumepost
from Scriptdb.servicios.transaccion import consultaPendientes
from Connect.pgsqlbd import conectarPG
from Connect.orasqlbd import conectarORA
from Connect.mysqlbd import conectarMY


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)


DEFAULT_MAX_WORKERS = int(os.getenv("BILL_MAX_WORKERS", "4"))
DEFAULT_HTTP_TIMEOUT = int(os.getenv("BILL_HTTP_TIMEOUT", "70"))


class BillProcessError(Exception):
    """Error controlado del proceso de emisión de facturas."""



def executeBill(req: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    conexion = None
    req = req or {}

    try:
        conexion = switchconn("oracle")
        data = extractData(req, conexion)
        resultado = transformData(req, data)
        return loadData(resultado, conexion)

    except Exception as e:
        logger.exception("Error ejecutando el proceso de emisión de facturas")
        return {
            "status": "error",
            "code": 500,
            "resultado": {
                "estado": "error",
                "mensaje": "No fue posible procesar la emisión de la factura a Titanio.",
                "detalle": str(e),
            },
        }
    finally:
        try:
            if conexion:
                conexion.close()
        except Exception:
            logger.warning("No fue posible cerrar la conexión de base de datos")



def extractData(busqueda: Optional[Dict[str, Any]] = None, conexion: Any = None) -> Dict[str, Any]:
    busqueda = busqueda or {}

    try:
        params = busqueda.get("parametros", {})
        facturas = consultaPendientes(conexion, params)

        if isinstance(facturas, dict):
            return facturas

        return {"data": facturas or []}

    except Exception as e:
        logger.exception("Error extrayendo facturas pendientes")
        return {
            "status": "error",
            "code": 500,
            "resultado": {
                "estado": "error",
                "mensaje": "No fue posible consultar las facturas pendientes.",
                "detalle": str(e),
            },
            "data": [],
        }



def transformData(req: Optional[Dict[str, Any]], resultado: Dict[str, Any]) -> Dict[str, Any]:
    req = req or {}
    host_bill = os.getenv("UD_BILL_HOST")
    url_bill = "/bills/serv/emit"

    respuesta = {
        "status": "success",
        "resultado": {
            "estado": "ok",
            "mensaje": "Proceso ejecutado.",
            "resumen": {
                "total": 0,
                "correctos": 0,
                "errados": 0,
            },
            "detalle": [],
        },
    }

    try:
        if not host_bill:
            raise BillProcessError("La variable de entorno UD_BILL_HOST no está configurada")

        registros = resultado.get("data", [])
        if not isinstance(registros, list):
            raise BillProcessError("La estructura de datos de entrada no contiene una lista válida en 'data'")

        if not registros:
            respuesta["resultado"]["mensaje"] = "No se encontraron facturas pendientes para procesar."
            return respuesta

        max_workers = min(DEFAULT_MAX_WORKERS, len(registros)) or 1
        logger.info("Iniciando procesamiento de %s factura(s) con %s worker(s)", len(registros), max_workers)

        detalle: List[Dict[str, Any]] = []
        correctos = 0
        errados = 0

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(process_bill_record, fila, host_bill, url_bill)
                for fila in registros
            ]

            for future in as_completed(futures):
                result = future.result()
                detalle.append(result)

                if result["estado_proceso"] == "correcto":
                    correctos += 1
                else:
                    errados += 1

        respuesta["resultado"]["detalle"] = sorted(
            detalle,
            key=lambda x: (str(x.get("vigencia", "")), str(x.get("secuencia", "")))
        )
        respuesta["resultado"]["resumen"] = {
            "total": len(registros),
            "correctos": correctos,
            "errados": errados,
        }

        if errados > 0:
            respuesta["resultado"]["mensaje"] = "Proceso ejecutado con novedades."

        return respuesta

    except BillProcessError as e:
        logger.error("Error controlado en transformación: %s", e)
        return {
            "status": "error",
            "code": 422,
            "resultado": {
                "estado": "error",
                "mensaje": "No fue posible procesar las facturas.",
                "detalle": str(e),
            },
        }
    except Exception as e:
        logger.exception("Error general en transformación de datos")
        return {
            "status": "error",
            "code": 500,
            "resultado": {
                "estado": "error",
                "mensaje": "Error general durante el procesamiento de facturas.",
                "detalle": str(e),
            },
        }



def process_bill_record(fila: Dict[str, Any], host_bill: str, url_bill: str) -> Dict[str, Any]:
    id_factura = fila.get("FAC_ID", "")
    secuencia = fila.get("FAC_SECUENCIA", "")
    vigencia = fila.get("FAC_SECUENCIA_ANO", "")

    payload = build_bill_payload(secuencia=secuencia, vigencia=vigencia, id_factura=id_factura)

    try:
        logger.info("Procesando factura id_factura=%s secuencia=%s vigencia=%s", id_factura, secuencia, vigencia)
        response = call_bill_service(host_bill, url_bill, payload)
        estado_proceso = evaluate_bill_response(response)

        return {
            "id_factura": id_factura,
            "secuencia": secuencia,
            "vigencia": vigencia,
            "estado_proceso": estado_proceso,
            "respuesta_servicio": response,
        }

    except requests.exceptions.Timeout as e:
        logger.warning("Timeout emitiendo factura secuencia=%s vigencia=%s", secuencia, vigencia)
        return {
            "id_factura": id_factura,
            "secuencia": secuencia,
            "vigencia": vigencia,
            "estado_proceso": "error",
            "detalle": f"Timeout en servicio de emisión: {str(e)}",
        }
    except requests.exceptions.RequestException as e:
        logger.warning("Error HTTP emitiendo factura secuencia=%s vigencia=%s", secuencia, vigencia)
        return {
            "id_factura": id_factura,
            "secuencia": secuencia,
            "vigencia": vigencia,
            "estado_proceso": "error",
            "detalle": f"Error de comunicación con Titanio: {str(e)}",
        }
    except Exception as e:
        logger.exception("Error procesando factura secuencia=%s vigencia=%s", secuencia, vigencia)
        return {
            "id_factura": id_factura,
            "secuencia": secuencia,
            "vigencia": vigencia,
            "estado_proceso": "error",
            "detalle": str(e),
        }



def build_bill_payload(secuencia: Any, vigencia: Any, id_factura: str = "") -> Dict[str, Any]:
    return {
        "parametros": {
            "secuencia": secuencia,
            "vigencia": vigencia,
            "id_factura": id_factura,
        }
    }



def call_bill_service(host_bill: str, url_bill: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    # Si consumepost soporta timeout, conviene pasarlo dentro de esa función.
    # Aquí se conserva la integración actual para no romper compatibilidad.
    return consumepost(host_bill, url_bill, payload)



def evaluate_bill_response(response: Dict[str, Any]) -> str:
    estado_general = response.get("estado")
    estado_dian = response.get("datos", {}).get("estado")

    if estado_general == "success" and estado_dian == "G":
        return "correcto"

    return "error"



def loadData(resultado: Dict[str, Any], conexion: Any = None) -> Dict[str, Any]:
    try:
        status = resultado.get("status", "error")
        data = resultado.get("resultado", {})

        if status != "success":
            return {
                "status": "error",
                "resultado": {
                    "estado": "error",
                    "mensaje": data.get("mensaje", "Error en la ejecución del proceso"),
                    "detalle": data.get("detalle", ""),
                },
            }

        return {
            "status": "success",
            "resultado": data,
        }

    except Exception as e:
        logger.exception("Error general en loadData")
        return {
            "status": "error",
            "code": 500,
            "resultado": {
                "estado": "error",
                "mensaje": "Error general en procesamiento",
                "detalle": str(e),
            },
        }



def switchconn(motor: str):
    motor = (motor or "").lower()

    if motor == "oracle":
        dbconnect = {
            "host": os.getenv("BILLORA_HOST"),
            "port": os.getenv("BILLORA_PORT"),
            "database": os.getenv("BILLORA_DB"),
            "username": os.getenv("BILLORA_USER"),
            "password": os.getenv("BILLORA_PASSWORD"),
        }
        return conectarORA(dbconnect)

    if motor == "pgsql":
        dbconnect = {
            "host": os.getenv("BILLPG_HOST"),
            "port": os.getenv("BILLPG_PORT"),
            "database": os.getenv("BILLPG_DB"),
            "username": os.getenv("BILLPG_USER"),
            "password": os.getenv("BILLPG_PASSWORD"),
        }
        return conectarPG(dbconnect)

    if motor == "mysql":
        dbconnect = {
            "host": os.getenv("BILLMY_HOST"),
            "port": os.getenv("BILLMY_PORT"),
            "database": os.getenv("BILLMY_DB"),
            "username": os.getenv("BILLMY_USER"),
            "password": os.getenv("BILLMY_PASSWORD"),
        }
        return conectarMY(dbconnect)

    raise BillProcessError(f"Motor de base de datos no soportado: {motor}")
