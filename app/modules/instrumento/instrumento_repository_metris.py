from app.core.config import settings
import requests
from datetime import datetime, timedelta, timezone
import urllib3
import httpx
from app.infrastructure.metrisapi.historian import HistorianClient
#######CRITICO!!!!!!!!!!!!!!!##################################
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
        "ID": "6314",
        "TagID": "6314",
        "get_tag_values": 6314,
        "Start": one_hour_ago.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "End": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "InterpolationMethod": 1,
        "AggregateFunction": 0,
        "InterpolationResolutionType": 1,
        "interpolationresolution": 600000000
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        verify=False
    )

    data = response.json()

    return data


#Por ver
async def datos_historicos_por_instrumento(instrumento_id, minutos):# datos historicos
    METRIS_BASE_URI = settings.METRIS_BASE_URI
    METRIS_TOKEN = settings.METRIS_TOKEN
    headers = {
        "Authorization": f"Bearer {METRIS_TOKEN}"
    }
    url = f"{METRIS_BASE_URI}/api/public/Historian/trendvalues"
    
    #$$$$$$$$$$$$$$$$$ Cuanto tiempo vamos a mandar datos, minutos o segundos$$$$$$$$$$$$$$$$
    now = datetime.now(timezone.utc)
    start = now - timedelta(minutes=minutos)

    params = {
        "ID": instrumento_id,
        "TagID": instrumento_id,
        "Start": start.strftime("%Y-%m-%dT%H:%M:%SZ"),#Hora actual menos una hora en formato ISO 8601
        "End": now.strftime("%Y-%m-%dT%H:%M:%SZ"),#Hora actual en formato ISO 8601
        "InterpolationMethod": 0,
        "AggregateFunction": 1,#Cantidad de datos en el mismo json
        "InterpolationResolutionType": 1, #Cuantos puntos yo reconstruyo la serie de tiempo original
        "interpolationresolution": 600000000 #Muestreo de interpolación, cantidad de muestra por minuto
    }
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, headers=headers, params=params)
    data = response.json()
    return data
