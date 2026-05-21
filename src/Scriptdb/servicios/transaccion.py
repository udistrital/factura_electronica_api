import json
from datetime import datetime

def consultaEnvio(conexion, datos):
    query = """
        SELECT 
            ENV_ID,
            ENV_FAC_ID,
            ENV_DATE,
            ENV_STATE_SEND,
            ENV_TR_ID,
            ENV_ERROR,
            ENV_STATE
        FROM MNTFE.FEENVIO
        WHERE
        ENV_FAC_ID = :factura
        AND ENV_STATE='A'
    """
    params = {
        "factura": int(datos.get("id_factura", 0))
    }
    try:
        with conexion.cursor() as cursor:
            cursor.execute(query, params)
            fields = [field_md[0] for field_md in cursor.description]
            rows = cursor.fetchall()
            registros = [dict(zip(fields, row)) for row in rows]
        if registros:
            return {"exec": True,"data": registros }
        else:
            return {"exec": False, "data": [], "message": "No se encontraron registros" }
    except Exception as e:
        #print("Ocurrió un error al ejecutar la inserción del envio:", e)
        response = {
            "exec": False,
            "error": str(e)
        }
        return response

def registroEnvio(conexion, datos):
    query = """
        INSERT INTO MNTFE.FEENVIO
        (
            ENV_FAC_ID, 
            ENV_DATE, 
            ENV_STATE_SEND, 
            ENV_TR_ID,  
            ENV_ERROR, 
            ENV_STATE
        )
        VALUES
        (   :factura,
            SYSDATE,
            :estado,
            :id_transaccion,
            :error_msg,
            'A'
        )
    """
    params = {
        "factura": int(datos.get("id_factura", 0)),
        "estado": str(datos.get("estado", "")),
        "id_transaccion": int(datos.get("id_transaccion", 0)) if datos.get("id_transaccion") not in [None, ""] else 0,
        "error_msg":str(datos.get("error_emision", "")),
    }
    try:
        with conexion.cursor() as cursor:
            cursor.execute(query, params)
            conexion.commit()
        response = {
            "exec": True,
            "data": params
        }
        return response
    except Exception as e:
        #print("Ocurrió un error al ejecutar la inserción del envio:", e)
        response = {
            "exec": False,
            "error": str(e)
        }
        return response

def registroEnvioOLD(conexion, datos):
    query = """
        INSERT INTO MNTFE.FEENVIO
        (
            ENV_ID,
            ENV_SECUENCIA, 
            ENV_SECUENCIA_ANO, 
            ENV_DATE, 
            ENV_STATE_SEND, 
            ENV_TR_ID,  
            ENV_ERROR, 
            ENV_STATE
        )
        VALUES
        (   (SELECT NVL(MAX(ENV_ID), 0) + 1 AS NEXT_ID
              FROM MNTFE.FEENVIO), 
            :secuencia,
            :vigencia,
            SYSDATE,
            :estado,
            :id_transaccion,
            :error_msg,
            'A'
        )
    """
    params = {
        "secuencia": int(datos.get("secuencia", 0)),
        "vigencia": int(datos.get("vigencia", 0)),
        "estado": str(datos.get("estado", "")),
        "id_transaccion": int(datos.get("id_transaccion", 0)) if datos.get("id_transaccion") not in [None, ""] else 0,
        "error_msg":str(datos.get("error_emision", "")),
    }
    try:
        with conexion.cursor() as cursor:
            cursor.execute(query, params)
            conexion.commit()
        response = {
            "exec": True,
            "data": params
        }
        return response
    except Exception as e:
        #print("Ocurrió un error al ejecutar la inserción del envio:", e)
        response = {
            "exec": False,
            "error": str(e)
        }
        return response


def consultaSolicitudes(conexion, datos):
    query = """
        SELECT 
            ENV_ID,
            ENV_FAC_ID, 
            ENV_DATE,
            ENV_STATE_SEND,
            ENV_TR_ID,
            ENV_ERROR,
            ENV_STATE,
            FAC_SECUENCIA,
            FAC_SECUENCIA_ANO
        FROM MNTFE.FEENVIO
        INNER JOIN MNTFE.FEFACTURA ON ENV_FAC_ID=FAC_ID
        WHERE
        ENV_STATE='A'
        AND ENV_STATE_SEND='S'
    """
    try:
        with conexion.cursor() as cursor:
            cursor.execute(query)
            fields = [field_md[0] for field_md in cursor.description]
            rows = cursor.fetchall()
            registros = [dict(zip(fields, row)) for row in rows]
        if registros:
            return {"exec": True,"data": registros }
        else:
            return {"exec": False, "data": [], "message": "No se encontraron registros" }
    except Exception as e:
        #print("Ocurrió un error al ejecutar la inserción del envio:", e)
        response = {
            "exec": False,
            "error": str(e)
        }
        return response

def consultaEnviosDocumentoDuplicado(conexion, datos=None):
    query = """
        SELECT
            ENV_ID,
            ENV_ERROR
        FROM MNTFE.FEENVIO
        WHERE
        ENV_STATE = 'A'
        AND ENV_STATE_SEND = 'E'
        AND UPPER(ENV_ERROR) LIKE '%ERROR AL CREAR LA TRANSACCION. DOCUMENTO DUPLICADO.%'
        AND REGEXP_LIKE(ENV_ERROR, 'TR_ID[[:space:]]*:[[:space:]]*[[:digit:]]+')
    """
    try:
        with conexion.cursor() as cursor:
            cursor.execute(query)
            fields = [field_md[0] for field_md in cursor.description]
            rows = cursor.fetchall()
            registros = [dict(zip(fields, row)) for row in rows]
        if registros:
            return {"exec": True, "data": registros}
        return {"exec": False, "data": [], "message": "No se encontraron registros"}
    except Exception as e:
        response = {
            "exec": False,
            "error": str(e)
        }
        return response

def actualizaEnvioDocumentoDuplicado(conexion, datos):
    query = """
        UPDATE MNTFE.FEENVIO
        SET
        ENV_TR_ID = :id_transaccion,
        ENV_STATE_SEND = 'S'
        WHERE
        ENV_ID = :envio
        AND ENV_STATE = 'A'
        AND ENV_STATE_SEND = 'E'
    """
    params = {
        "envio": int(datos.get("envio", 0)),
        "id_transaccion": int(datos.get("id_transaccion", 0))
    }
    try:
        with conexion.cursor() as cursor:
            cursor.execute(query, params)
            filas = cursor.rowcount
            conexion.commit()
        response = {
            "exec": True,
            "data": params,
            "rows": filas
        }
        return response
    except Exception as e:
        response = {
            "exec": False,
            "error": str(e)
        }
        return response

def actualizaEnviosSinRespuestaTitanio(conexion, datos=None):
    query = """
        UPDATE MNTFE.FEENVIO
        SET
        ENV_STATE_SEND = 'C'
        WHERE
        ENV_STATE = 'A'
        AND ENV_STATE_SEND = 'E'
        AND (
            TRIM(ENV_ERROR) = :error_msg
            OR UPPER(ENV_ERROR) LIKE :error_interno
            OR UPPER(ENV_ERROR) LIKE :intente_mas_tarde
        )
    """
    params = {
        "error_msg": "No se obtuvo respuesta válida de Titanio al emitir la factura.",
        "error_interno": "%HA OCURRIDO UN ERROR INTERNO,%",
        "intente_mas_tarde": "%INTENTE MÁS TARDE%"
    }
    try:
        with conexion.cursor() as cursor:
            cursor.execute(query, params)
            filas = cursor.rowcount
            conexion.commit()
        response = {
            "exec": True,
            "data": params,
            "rows": filas
        }
        return response
    except Exception as e:
        response = {
            "exec": False,
            "error": str(e)
        }
        return response

def consultaEnviosActivosConError(conexion, datos=None):
    query = """
        SELECT
            env.ENV_FAC_ID,
            env.ENV_ERROR,
            fac.FAC_DOCUMENT_ID,
            fac.FAC_SECUENCIA,
            fac.FAC_SECUENCIA_ANO
        FROM MNTFE.FEENVIO env
        INNER JOIN MNTFE.FEFACTURA fac ON env.ENV_FAC_ID = fac.FAC_ID
        WHERE
        env.ENV_STATE = 'A'
        AND env.ENV_STATE_SEND = 'E'
    """
    try:
        with conexion.cursor() as cursor:
            cursor.execute(query)
            fields = [field_md[0] for field_md in cursor.description]
            rows = cursor.fetchall()
            registros = [dict(zip(fields, row)) for row in rows]
        if registros:
            return {"exec": True, "data": registros}
        return {"exec": False, "data": [], "message": "No se encontraron registros"}
    except Exception as e:
        response = {
            "exec": False,
            "error": str(e)
        }
        return response

def actualizaSolicitud(conexion, datos):
    query = """
        UPDATE MNTFE.FEENVIO
        SET 
        ENV_STATE_SEND = :estado
        , ENV_ERROR = :error_msg
        WHERE
        ENV_TR_ID = :id_transaccion
    """
    params = {
        "estado": str(datos.get("estado", "")),
        "id_transaccion": int(datos.get("id_transaccion", 0)) if datos.get("id_transaccion") not in [None, ""] else 0,
        "error_msg": str(datos.get("error_emision") or datos.get("error_dian", "")),
    }
    try:
        with conexion.cursor() as cursor:
            cursor.execute(query, params)
            conexion.commit()
        response = {
            "exec": True,
            "data": params
        }
        return response
    except Exception as e:
        #print("Ocurrió un error al ejecutar la inserción del envio:", e)
        response = {
            "exec": False,
            "error": str(e)
        }
        return response

def actualizaEnvio(conexion, datos):
    query = """
        UPDATE MNTFE.FEENVIO
        SET ENV_STATE = 'I'
        WHERE
        ENV_FAC_ID = :transaccion
    """
    params = {
        "transaccion": int(datos.get("id_factura", 0))
    }

    try:
        with conexion.cursor() as cursor:
            cursor.execute(query, params)
            conexion.commit()
        response = {
            "exec": True,
            "data": params
        }
        return response
    except Exception as e:
        #print("Ocurrió un error al ejecutar la inserción del envio:", e)
        response = {
            "exec": False,
            "error": str(e)
        }
        return response

def registroCUFE(conexion, datos):
    query = """
        UPDATE MNTFE.FEFACTURA
        SET FAC_UUID=:cufe
        , FAC_QR=:qr_code
        , FAC_ISSUE_DATE=TO_DATE(:emision, 'YYYY-MM-DD HH24:MI:SS')
        WHERE 
        FAC_ID = :factura
    """

    fecha_raw = datos.get("fecha_emision")
    if fecha_raw:
        fecha_raw = str(fecha_raw).strip()
        if len(fecha_raw) >= 19:
            # Caso con zona horaria o completo
            fecha_emite = fecha_raw[:19]
        elif len(fecha_raw) == 10:
            # Solo fecha → completar hora
            fecha_emite = f"{fecha_raw} 00:00:00"
        else:
            # Formato inesperado
            fecha_emite = None
    else:
        fecha_emite = None

    params = {
        "factura": int(datos.get("id_factura", 0)),
        "cufe": str(datos.get("cufe", "")),
        "qr_code": str(datos.get("qr_cod", "")),
        "emision": fecha_emite
    }
    try:
        with conexion.cursor() as cursor:
            cursor.execute(query, params)
            conexion.commit()
        response = {
            "exec": True,
            "data": params
        }
        return response
    except Exception as e:
        #print("Ocurrió un error al ejecutar la actualización:", e)
        response = {
            "exec": False,
            "error": str(e)
        }
        return response

def consultaPendientes(conexion, datos):
    query = """
        SELECT
            fac.FAC_ID,
            fac.FAC_SECUENCIA,
            fac.FAC_SECUENCIA_ANO,
            fac.FAC_UUID,
            fac.FAC_STATE,
            fac.FAC_CREATION_DATE
        FROM MNTFE.FEFACTURA fac
        WHERE fac.FAC_STATE = 'A'
        AND FAC_CUSTOMIZATION_ID=1
        AND NOT EXISTS (
            SELECT 1
            FROM MNTFE.FEENVIO env
            WHERE env.ENV_STATE = 'A'
                AND env.ENV_STATE_SEND IN ('G', 'E', 'S')
                AND env.ENV_FAC_ID = fac.FAC_ID
        )
        ORDER BY fac.FAC_CREATION_DATE
        FETCH FIRST :items ROWS ONLY
    """
    items = datos.get("items")
    try:
        items = int(items)
        if items <= 0:
            items = 20
    except (TypeError, ValueError):
        items = 210

    params = {
        "items": items
        }

    try:
        with conexion.cursor() as cursor:
            cursor.execute(query, params)
            #cursor.execute(query)
            fields = [field_md[0] for field_md in cursor.description]
            rows = cursor.fetchall()
            registros = [dict(zip(fields, row)) for row in rows]
        if registros:
            return {"exec": True,"data": registros }
        else:
            return {"exec": False, "data": [], "message": "No se encontraron registros" }
    except Exception as e:
        #print("Ocurrió un error al ejecutar la inserción del envio:", e)
        response = {
            "exec": False,
            "error": str(e)
        }
        return response

def consultaReporte(conexion,query,busqueda):
    try:
        cursor = conexion.cursor()
        cursor.execute(query)
        # fetchone trae uno por uno todas las filas ## servicios = cursor.fetchone()
        # retorna alias y valores
        fields = [field_md[0] for field_md in cursor.description]
        registros = [dict(zip(fields,row)) for row in cursor.fetchall()]
        #cursor.close()
        #conexion.close()
        return registros
    except Exception as e:
        #print("Ocurrió un error al consultar los reportes: ", e)
        return ''
    finally:
        cursor.close()

def executeReporte(conexion,query,busqueda):
    try:
        with conexion.cursor() as cursor:
            cursor.execute(query)
            conexion.commit() 
            datos_actualizados = cursor.fetchone()  # O fetchall() si esperas múltiples filas
            registros = {}
            if datos_actualizados:
                fields = [field_md[0] for field_md in cursor.description]
                for campo, dato in zip(fields, datos_actualizados):
                    registros[campo] = dato
            response= { "exec" : True, "data": registros}
            return response 
    except Exception as e:
        #print("Ocurrió un error al ejecutar la inserción: ", e)
        response= { "exec" : False}
        return response  # Indicador de fallo
    finally:
        cursor.close()
