# instrumento_repository.py
from .instrumento_schema import InstrumentoI
from app.core.config import settings
import requests

METRIS_BASE_URI = settings.METRIS_BASE_URI
METRIS_TOKEN = settings.METRIS_TOKEN
print("base uri: ", METRIS_BASE_URI, "token: ", METRIS_TOKEN)
headers = {
    "Authorization": f"Bearer {METRIS_TOKEN}"
}

url = f"{METRIS_BASE_URI}/api/public/Historian/trendvalues"

params = {
    "ID": "86743",
    "TagID": "86743",
    "Start": "2026-01-19T00:00:00Z",
    "End": "2026-01-20T00:00:00Z",
    "InterpolationMethod": 0,
    "AggregateFunction": 3,
    "InterpolationResolutionType": 1,
    "interpolationresolution": 600000000
}

response = requests.get(url, headers=headers, params=params)
print(response)
#print("STATUS:", response.status_code)
#print("RESPONSE:", response.text)

def obtener_desde_api():
    #response = requests.get(url, headers=headers, params=params)
    #print("STATUS:", response.status_code)
    #print("RESPONSE:", response.text)
    #return response.json()
    instrumento1 = InstrumentoI(id=1, nombre="Guitarra", tipo="Cuerda", valor=150.0)
    instrumento2 = InstrumentoI(id=2, nombre="Piano", tipo="Teclado", valor=1000.0)
    return {"Instrumento1":instrumento1,"instrumento2": instrumento2}