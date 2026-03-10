"""
Proyecto ODIN - Generador de servicios api-rest  
Módulo: Generador reportes Api-rest
Basado en framework Flask
Author: Jairol Lavado.
Fecha: Enero 2024
versión: 0.0.0.1
"""
from flask import Blueprint, request, jsonify
import os, sys

routes_health = Blueprint("routes_health", __name__)

@routes_health.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "Service is healthy"}), 200
