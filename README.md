# Sistema Facturación   
El sistema para facturación electronicá esta basado en el proyecto ODIN. 

### Servicio Facturación electronica

El servicio para facturación electronica, permite integrar los sistemas de la Universidad Distrital con la plataforma Titanio en arquitectura de servicios Web Api-Rest.

## Despliegue
Crear las siguientes variables de entorno en el servidor, con los valores correspondientes:
- SECRET : Código secreto para codificación de 32 caracteres númericos y alfanumericos.
- APP_ENV : Variable que indica que entorno, valor por defecto 'production', solo cambiar a 'development', en equipo de desarrollo.
- BILLORA_DB : Nombre de la base de datos oracle.
- BILLORA_HOST : Dirección del servidor de base de datos oracle.
- BILLORA_PORT : Puerto de conexión  oracle
- BILLORA_USER : Nombre de usuario de conexión a al base de datos oracle.
- BILLORA_PASSWORD : Contraseña de conexión a al base de datos oracle.
- BILLORA_SCHEMA : Esquema de la base de datos oracle 
- TITANIO_HOST : Dirección URL para cosumier los servicios de Titanio
- TITANIO_NIT : Número NIT de la universidad para consumir el servicio de autenticación en Titanio
- TITANIO_USER : Nombre de usuario para consumir el servicio de autenticación en Titanio
- TITANIO_PWD : Contraseña para consumir el servicio de autenticación en Titanio

  ####  Desde una terminal Ejecutar comando crear el archivo .env, con las variables de entorno:
   ./create_env.sh 
 
   ####  Desde una terminal Ejecutar comando crear el contenedor:
   docker-compose up --build

   #### Consumir los servicios    

   Una vez desplegado puede consumir el servicio realizando una petición POST, como la del siguiente ejemplo:  
   http://127.0.0.1:8088/bills/serv/bill con el body:  {"parametros": {"secuencia": "", "vigencia": "", "identificacion": "" } }
