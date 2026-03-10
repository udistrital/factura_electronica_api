"""
Proyecto ODIN - Generador de servicios api-rest  
Módulo: Generador reportes Api-rest
Basado en framework Flask
Author: Jairol Lavado.
Fecha: Enero 2024
versión: 0.0.0.1
"""
import json
import bcrypt
import numpy
import time
from datetime import datetime
import uuid
from statistics import mean, median, mode

def switch(lang,registro,campos):
    if lang == "suma":
        return suma(registro,campos)
    elif lang == "resta":
        return resta(registro,campos)
    elif lang == "multiplica":
        return multiplica(registro,campos)
    elif lang == "divide":
        return divide(registro,campos)
    elif lang == "media":
        return media(registro,campos)
    elif lang == "mediana":
        return mediana(registro,campos)
    elif lang == "moda":
        return moda(registro,campos)
    else:
        return ''

def suma(registro,campos):
    try:
        suma = 0  
        for campo in campos:
            suma=suma+registro[campo]
        return suma
    except Exception as e:
        print("Ocurrió un error al sumar los datos: ", e)    

def resta(registro,campos):
    try:
        resta = 0 
        for campo in campos:
            resta=(registro[campo] - resta)
        return resta       
    except Exception as e:
        print("Ocurrió un error al restar los datos: ", e)         

def multiplica(registro,campos):
    try:
        multiplo = 1  
        for campo in campos:
            multiplo=multiplo*registro[campo]
        return multiplo
    except Exception as e:
        print("Ocurrió un error al multiplicar los datos: ", e)    

def divide(registro,campos):
    try:
        valores=[];
        for campo in campos:
            valores.append(registro[campo])
        valores.sort(reverse=True)
        divisor = 1  
        for valor in valores:
            divisor=valor/divisor
        return divisor
    except Exception as e:
        print("Ocurrió un error al dividir los datos: ", e)    

def media(registro,campos):
    try:
        data = []  
        for campo in campos:
            data.append(registro[campo])    
        media = mean(data)    
        return media
    except Exception as e:
        print("Ocurrió un error al obtener la media: ", e)          

def mediana(registro,campos):
    try:
        data = []  
        for campo in campos:
            data.append(registro[campo])    
        #ordenados = sorted(data, reverse=True)
        mediana = median(data)
        return mediana
    except Exception as e:
        print("Ocurrió un error al obtener la mediana: ", e)       

def moda(registro,campos):
    try:
        data = []  
        for campo in campos:
            data.append(registro[campo])    
        moda = mode(data)
        return moda
    except Exception as e:
        print("Ocurrió un error al obtener la moda: ", e)                 