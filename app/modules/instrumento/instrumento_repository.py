# instrumento_repository.py
from .instrumento_schema import InstrumentoI
from app.core.config import settings
import requests
from datetime import datetime, timedelta, timezone


METRIS_BASE_URI = settings.METRIS_BASE_URI
METRIS_TOKEN = settings.METRIS_TOKEN
headers = {
    "Authorization": f"Bearer {METRIS_TOKEN}"
}

url = f"{METRIS_BASE_URI}/api/public/Historian/trendvalues"

now = datetime.now(timezone.utc)
one_hour_ago = now - timedelta(hours=1)
five_minutes_ago = now - timedelta(minutes=5)

params = {
    "ID": "9367",
    "TagID": "9067",
    #"Start": one_hour_ago.strftime("%Y-%m-%dT%H:%M:%SZ"),#Hora actual menos una hora en formato ISO 8601
    "Start": five_minutes_ago.strftime("%Y-%m-%dT%H:%M:%SZ"),#Hora actual menos una hora en formato ISO 8601
    "End": now.strftime("%Y-%m-%dT%H:%M:%SZ"),#Hora actual en formato ISO 8601
    "InterpolationMethod": 0,
    "AggregateFunction": 1,#Cantidad de datos en el mismo json
    "InterpolationResolutionType": 1,
    "interpolationresolution": 600000000
}



def obtener_desde_api():
    response = requests.get(url, headers=headers, params=params, verify=False)
    print(response)
    data = response.json()
    return data
    #instrumento1 = InstrumentoI(id=1, nombre="Guitarra", tipo="Cuerda", valor=150.0)
    #instrumento2 = InstrumentoI(id=2, nombre="Piano", tipo="Teclado", valor=1000.0)
    #return {"Instrumento1":instrumento1,"instrumento2": instrumento2}