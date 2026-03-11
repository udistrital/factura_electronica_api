"""
Proyecto ODIN - Generador de servicios api-rest  
Módulo: Generador reportes Api-rest
Basado en framework Flask
Author: Jairol Lavado.
Fecha: Enero 2024
versión: 0.0.0.1
"""
import json

def consultaRegistros(conexion,busqueda):
    try:
        with conexion.cursor() as cursor:
            '''
            searchQuery =  "SELECT DISTINCT repos.id, repos.nombre, repos.descripcion, repos.procedimiento, repos.tipo, repos.acceso, repos.consulta_db, repos.parametros, repos.tratamiento, repos.estado, conn.motor, conn.conexion "
            searchQuery += "FROM generador_api_reporte repos "
            searchQuery += "INNER JOIN generador_db_conexion conn on conn.id = repos.conexion_id "
            searchQuery += "INNER JOIN generador_usuario_apireporte usapi ON repos.id = usapi.id_api_id AND usapi.estado ='A'"
            searchQuery += "WHERE repos.estado='A' "
            searchQuery += "AND repos.procedimiento = '"+ busqueda['procedimiento'] +"' "
            searchQuery += "AND repos.acceso = '"+ busqueda['api'] +"' "
            searchQuery += "AND usapi.id_usuario = '"+ str(busqueda['usuario']) +"' "
            searchQuery += "; "
            #print(searchQuery)
            cursor.execute(searchQuery)
            # fetchone trae uno por uno todas las filas ## servicios = cursor.fetchone()
            # retorna alias y valores
            fields = [field_md[0] for field_md in cursor.description]
            registros = [dict(zip(fields,row)) for row in cursor.fetchall()]
            '''
            registros = '{"resp":"hola"}'


            return registros
    except Exception as e:
        print("Ocurrió un error al consultar los apis de reportes: ", e)
    finally:
        cursor.close()


def registroEnvio(conexion, datos):
    query = """
        INSERT INTO MNTFE.FEENVIO
        (
            ENV_SECUENCIA,
            ENV_SECUENCIA_ANO,
            ENV_DATE,
            ENV_STATE,
            ENV_TR_ID,
            ENV_QR
        )
        VALUES
        (
            :secuencia,
            :vigencia,
            SYSDATE,
            :estado,
            :id_transaccion,
            :qr_cod
        )
    """
    params = {
        "secuencia": int(datos.get("secuencia", 0)),
        "vigencia": int(datos.get("vigencia", 0)),
        "estado": str(datos.get("estado", "")),
        "id_transaccion": int(datos.get("id_transaccion", 0)) if datos.get("id_transaccion") not in [None, ""] else 0,
        "qr_cod": datos.get("qr_cod")
    }
    #print(query)
    #print(params)
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
        print("Ocurrió un error al ejecutar la inserción del envio:", e)
        response = {
            "exec": False,
            "error": str(e)
        }
        return response

def registroCUFE(conexion, datos):
    query = """
        UPDATE MNTFE.FEFACTURA
        SET FAC_UUID=:cufe
        WHERE 
        FAC_SECUENCIA=:secuencia
        AND FAC_SECUENCIA_ANO=:vigencia
    """
    params = {
        "secuencia": int(datos.get("secuencia", 0)),
        "vigencia": int(datos.get("vigencia", 0)),
        "cufe": str(datos.get("cufe", ""))
    }
    #print(query)
    #print(params)
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
        print("Ocurrió un error al ejecutar la actualización:", e)
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
        print("Ocurrió un error al consultar los reportes: ", e)
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
        print("Ocurrió un error al ejecutar la inserción: ", e)
        response= { "exec" : False}
        return response  # Indicador de fallo
    finally:
        cursor.close()



    try:
        with conexion.cursor() as cursor:
            searchQuery =  query
            print(query)
            cursor.execute(searchQuery)
            # fetchone trae uno por uno todas las filas ## servicios = cursor.fetchone()
            # retorna alias y valores
            fields = [field_md[0] for field_md in cursor.description]
            registros = [dict(zip(fields,row)) for row in cursor.fetchall()]
            #cursor.close()
            #conexion.close()
            return registros
    except Exception as e:
        print("Ocurrió un error al consultar los reportes: ", e)
        return ''
    finally:
        cursor.close()