"""
Proyecto ODIN - Generador de servicios api-rest  
Módulo: Generador Tebleros EDA como Servicio
Basado en framework Flask
Author: Jairo Lavado.
Fecha: Enero 2024
versión: 0.0.0.1
"""
import json
import bcrypt
from flask import request, jsonify, Response, send_file, abort
import requests
import numpy
import uuid
import os, sys
p = os.path.abspath('src')
sys.path.insert(1, p)
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def consumeget(auth,hostws,paginaws,parametrosws=''):
    ##Consultar datos
    auth_token=auth['token']
    header = {'Content-type':'application/json', 'Accept':'application/json',
              'Authorization':'Bearer ' + auth_token}
    url = hostws+paginaws+parametrosws
    response = requests.get(url, headers=header, verify = False)
    datos = response.json()
    return datos  

def consumepost(hostws,paginaws,parametrosws=''):
    #consumir servicio y obtener token
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    head_ws = {'Content-type':'application/json', 'Accept':'application/json'}
    url_ws = str(hostws)+str(paginaws)
    data_ws = parametrosws
    reslogin = requests.post(url_ws, json=data_ws,  headers=head_ws, verify = False)
    datos = reslogin.json()
    return datos

def consumepost_bearer(auth,hostws,paginaws,parametrosws=''):
    #consumir servicio y obtener token
    auth_token=auth['token']
    header = {'Content-type':'application/json', 'Accept':'application/json',
              'Authorization':'Bearer ' + auth_token}
    url = hostws+paginaws
    #print(url)
    data_param = parametrosws
    res = requests.post(url, json=data_param,  headers=header, verify = False)
    datos = res.json()
    return datos    

def validarget_bearer(auth,hostws,paginaws,parametrosws=''):
    auth_token=auth['token']
    header = {'Content-type':'application/json', 'Accept':'application/json',
             'Authorization':'Bearer ' + auth_token}  
    url = hostws+paginaws+parametrosws
    response = requests.get(url, headers=header, verify = False)
    datos = response.json()
    return datos  

def consumepost_trans(hostws, paginaws, parametrosws=''):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    url_ws = f"{hostws}{paginaws}"
    headers = {  "Content-Type": "application/json", "Accept": "application/json" }
    # Validar tamaño máximo de 2 MB
    payload_bytes = json.dumps(parametrosws).encode("utf-8")
    if len(payload_bytes) > 2 * 1024 * 1024:
        raise ValueError("El objeto DATA supera el límite permitido de 2 MB")
    retry_strategy = Retry(
        total=2,
        backoff_factor=2,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["POST"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    try:
        response = session.post(url_ws,json=parametrosws, headers=headers,verify=False,timeout=(5, 20))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        print("Timeout: el servicio tardó más de lo esperado en responder")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error consumiendo servicio: {e}")
        return None
