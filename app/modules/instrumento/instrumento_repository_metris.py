from app.core.config import settings
import requests
from datetime import datetime, timedelta, timezone

TIEMPO_CONGELADO = 0
def historico_instrumento_metris_api():
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
        "ID": "6299",
        "TagID": "6299",
        "Start": five_minutes_ago.strftime("%Y-%m-%dT%H:%M:%SZ"),#Hora actual menos una hora en formato ISO 8601
        "End": now.strftime("%Y-%m-%dT%H:%M:%SZ"),#Hora actual en formato ISO 8601
        "InterpolationMethod": 0,
        "AggregateFunction": 1,#Cantidad de datos en el mismo json
        "InterpolationResolutionType": 1,
        "interpolationresolution": 600000000
    }
    response = requests.get(url, headers=headers, params=params, verify=False)
    data = response.json()
    return data

def tiempo_actual():
    now = datetime.now(timezone.utc)
    TIEMPO_CONGELADO = now
    return TIEMPO_CONGELADO

def historico_individual_por_instrumento(instrumento_id, primer_muestreo):
    METRIS_BASE_URI = settings.METRIS_BASE_URI
    METRIS_TOKEN = settings.METRIS_TOKEN
    headers = {
        "Authorization": f"Bearer {METRIS_TOKEN}"
    }

    url = f"{METRIS_BASE_URI}/api/public/Historian/trendvalues"

    one_hour_ago = primer_muestreo - timedelta(hours=1)
    five_minutes_ago = primer_muestreo - timedelta(minutes=5)

    params = {
        "ID": instrumento_id,
        "TagID": instrumento_id,
        "Start": five_minutes_ago.strftime("%Y-%m-%dT%H:%M:%SZ"),#Hora actual menos una hora en formato ISO 8601
        "End": primer_muestreo.strftime("%Y-%m-%dT%H:%M:%SZ"),#Hora actual en formato ISO 8601
        "InterpolationMethod": 0,
        "AggregateFunction": 1,#Cantidad de datos en el mismo json
        "InterpolationResolutionType": 1, #Cuantos puntos yo reconstruyo la serie de tiempo original
        "interpolationresolution": 600000000 #Muestreo de interpolación, cantidad de muestra
    }
    response = requests.get(url, headers=headers, params=params, verify=False)
    data = response.json()
    return data