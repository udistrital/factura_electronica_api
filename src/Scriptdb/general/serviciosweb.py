"""
Proyecto ODIN - Generador de servicios api-rest  
Módulo: Generador reportes Api-rest
Basado en framework Flask
Author: Jairol Lavado.
Fecha: Enero 2024
versión: 0.0.0.1
"""
def consultaServicio(conexion,busqueda):
    try:
        with conexion.cursor() as cursor:
            serviceQuery = " SELECT id_servicio Id, nombre Nombre, host Servidor, parametros Param, peticion Tipo, aplicacion Uso FROM adm_servicio_web "
            serviceQuery += " WHERE id_estado='1' AND nombre LIKE '%"+ busqueda +"%';"
            cursor.execute(serviceQuery)
            # fetchone trae uno por uno todas las filas ## servicios = cursor.fetchone()
            # fetchall trae todas las filas
            servicios = cursor.fetchall()
            return servicios
    except Exception as e:
        print("Ocurrió un error al consultar los servicios: ", e)
    finally:
        cursor.close()
        #conexion.close()