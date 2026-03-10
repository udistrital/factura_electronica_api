"""
Proyecto ODIN - Generador de servicios api-rest
Módulo: Generador reportes Api-rest
Basado en framework Flask
Author: Jairol Lavado.
Fecha: Enero 2024
versión: 0.0.0.1
"""

import os
import logging

from flask import Flask, request
from dotenv import load_dotenv
from waitress import serve

#from routes.auth import routes_auth
from routes.servicios import servicio

# Carga .env solo en local (si existe). No rompe en prod.
load_dotenv()

APP_ENV = os.getenv("APP_ENV", "production").lower()  # development | production
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8088"))

app = Flask(__name__)

# Logging: DEBUG en desarrollo, INFO en producción
log_level = logging.DEBUG if APP_ENV == "development" else logging.INFO
logging.basicConfig(
    level=log_level,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

@app.before_request
def log_request_info():
    # Evita ruido en health checks
    if request.path == "/bills/health":
        return
    logging.info("%s request to %s from %s", request.method, request.path, request.remote_addr)

print("servicio =", servicio, "type =", type(servicio))

#app.register_blueprint(routes_auth, url_prefix="/bills")
app.register_blueprint(servicio, url_prefix="/bills")

def run():
    logging.info("Starting API (env=%s) on %s:%s", APP_ENV, HOST, PORT)

    if APP_ENV == "development":
        # Debug + auto-reload (solo desarrollo)
        app.run(host=HOST, port=PORT, debug=True)
    else:
        # Producción: servidor WSGI
        serve(app, host=HOST, port=PORT)


if __name__ == "__main__":
    run()