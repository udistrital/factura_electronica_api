"""
Proyecto ODIN - Generador de servicios api-rest  
Módulo: Generador reportes Api-rest
Basado en framework Flask
Author: Jairol Lavado.
Fecha: Enero 2024
versión: 0.0.0.1
"""
def consultaUsuario(conexion,busqueda):
    try:
        with conexion.cursor() as cursor:
            serviceQuery = "SELECT DISTINCT "
            serviceQuery += "us.id \"Id\", "
            serviceQuery += "us.is_superuser \"Superadmin\",  "
            serviceQuery += "us.username \"Usuario\", "
            serviceQuery += "us.\"password\" \"Clave\", "
            serviceQuery += "us.first_name \"Nombres\", "
            serviceQuery += "us.last_name \"Apellidos\",  "
            serviceQuery += "us.email \"Correo\",  "
            serviceQuery += "us.is_active \"Activo\",  "
            serviceQuery += "gr.\"name\" \"Tipousuario\" "
            serviceQuery += "FROM public.auth_user us "
            serviceQuery += "INNER JOIN public.auth_user_groups grus ON grus.user_id=us.id  "
            serviceQuery += "INNER JOIN public.auth_group gr ON gr.id=grus.group_id   "
            serviceQuery += "WHERE  "
            serviceQuery += " us.is_active IS TRUE  "
            serviceQuery += "AND LOWER(gr.\"name\") IN ('aplicacion','administrador')  "
            #serviceQuery += "AND us.is_staff IS FALSE  "
            serviceQuery += "AND us.username = '"+ busqueda +"'"
            #print(serviceQuery)
            cursor.execute(serviceQuery)
            # fetchone trae uno por uno todas las filas ## servicios = cursor.fetchone()
            # fetchall trae todas las filas
            #registros = cursor.fetchall() ## retorna solo los valores
            # retorna alias y valores
            fields = [field_md[0] for field_md in cursor.description]
            registros = [dict(zip(fields,row)) for row in cursor.fetchall()]
            return registros
    except Exception as e:
        print("Ocurrió un error al consultar los usuarios: ", e)
    finally:
        cursor.close()
        #conexion.close()