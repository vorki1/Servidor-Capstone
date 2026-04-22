import requests
from .instrumento_schema import InstrumentoI
from .instrumento_repository import obtener_desde_api

def obtener_datos():
    #response = requests.get("https://api.externa.com/instrumentos")
    #data = response.json()

    #instrumentos = [InstrumentoAPI(**item) for item in data]
    instrumento = InstrumentoI(id=1, nombre="Guitarra", tipo="Cuerda", valor=150.0)
    return instrumento

def all_instrumentos():
    #Llamada a la API de "Metris" para obtener datos de instrumentos
    instrumentos = obtener_desde_api()
    return instrumentos