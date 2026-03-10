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




def consumeget(auth,hostws,paginaws,parametrosws=''):
    ##Consultar datos
    auth_token=auth['token']
    header = {'Content-type':'application/json', 'Accept':'application/json',
              'Authorization':'Bearer ' + auth_token}
    url = hostws+paginaws+parametrosws
    response = requests.get(url, headers=header, verify = False)
    datos = response.json()
    return datos  

def consumepostlogin(hostws,paginaws,parametrosws):
    #consumir servicio y obtener token
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    head_auth = {'Content-type':'application/json', 'Accept':'application/json'}
    url_auth = str(hostws)+str(paginaws)
    data_auth = parametrosws
    reslogin = requests.post(url_auth, json=data_auth,  headers=head_auth, verify = False)
    datos = reslogin.json()
    return datos

def consumepost(auth,hostws,paginaws,parametrosws=''):
    #consumir servicio y obtener token
    auth_token=auth['token']
    header = {'Content-type':'application/json', 'Accept':'application/json',
              'Authorization':'Bearer ' + auth_token}
    url = hostws+paginaws
    print(url)
    data_param = parametrosws
    res = requests.post(url, json=data_param,  headers=header, verify = False)
    datos = res.json()
    return datos    

def validarget(auth,hostws,paginaws,parametrosws=''):
    auth_token=auth['token']
    header = {'Content-type':'application/json', 'Accept':'application/json',
             'Authorization':'Bearer ' + auth_token}  
    url = hostws+paginaws+parametrosws
    response = requests.get(url, headers=header, verify = False)
    datos = response.json()
    return datos  