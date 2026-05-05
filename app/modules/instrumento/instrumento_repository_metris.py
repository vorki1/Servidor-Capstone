from app.core.config import settings
import requests
from datetime import datetime, timedelta, timezone
import urllib3
#######CRITICO!!!!!!!!!!!!!!!##################################
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ID_A_REVISAR = [6247,6248]
TIEMPO_CONGELADO = 0

def quality_code_metris_api():
    METRIS_BASE_URI = settings.METRIS_BASE_URI
    METRIS_TOKEN = settings.METRIS_TOKEN
    headers = {
        "Authorization": f"Bearer {METRIS_TOKEN}"
    }
    url = f"{METRIS_BASE_URI}/api/public/Historian/get_tag_values(6192)"
    response = requests.get(url, headers=headers, verify=False)
    print(response.status_code, response.text)  # Agrega esta línea para imprimir el código de estado y el texto de la respuesta
    if response.status_code == 404:
        print("Endpoint no encontrado (404)")
        return None
    data = response.json()
    print("Data obtenida de la API de Metris para Quality Code:", data)
    return data

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
    now = datetime.now(timezone.utc)

    enero_2021 = datetime(2021, 1, 1, tzinfo=timezone.utc)
    enero_2021_end = datetime(2021, 12, 31, tzinfo=timezone.utc)
    enero_2022 = datetime(2022, 1, 1, tzinfo=timezone.utc)
    enero_2022_end = datetime(2022, 12, 31, tzinfo=timezone.utc)
    enero_2023 = datetime(2023, 1, 1, tzinfo=timezone.utc)
    enero_2023_end = datetime(2023, 12, 31, tzinfo=timezone.utc)
    enero_2024 = datetime(2024, 1, 1, tzinfo=timezone.utc)
    enero_2024_end = datetime(2024, 12, 31, tzinfo=timezone.utc)
    enero_2025 = datetime(2025, 1, 1, tzinfo=timezone.utc)
    enero_2025_end = datetime(2025, 12, 31, tzinfo=timezone.utc)
    enero_2026 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)

    params = {
        "ID": "6192",
        "TagID": "6192",
        "get_tag_values":6192,
        "Start": five_minutes_ago.strftime("%Y-%m-%dT%H:%M:%SZ"),#Hora actual menos una hora en formato ISO 8601
        "End": now.strftime("%Y-%m-%dT%H:%M:%SZ"),#Hora actual en formato ISO 8601
        "InterpolationMethod": 1,
        "AggregateFunction": 0,#Cantidad de datos en el mismo json
        "InterpolationResolutionType": 1,
        "interpolationresolution": 600000000 #10.000.000 son 1 segundo, es decir, 1 muestra cada 100 segundos #1 tick = 100 nanosegundos
    }
    response = requests.get(url, headers=headers, params=params, verify=False)
    data = response.json()
    print(data)
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
        "interpolationresolution": 600000000 #Muestreo de interpolación, cantidad de muestra por minuto
    }
    response = requests.get(url, headers=headers, params=params, verify=False)
    data = response.json()
    return data