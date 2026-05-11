from app.core.config import settings
import requests
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta
import urllib3
import pandas as pd
from pathlib import Path
import numpy as np
from app.infrastructure.metrisapi.historian import HistorianClient
import httpx
#######CRITICO!!!!!!!!!!!!!!!##################################
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def quality_code_metris_api():
    hc = HistorianClient(base_uri=settings.METRIS_BASE_URI,token=lambda: settings.METRIS_TOKEN)
    data = hc.get_tag_values(ids=6248)
    print(data)
    return data

#===========================================Lectura de datos historicos ==================================================================
TIEMPO_CONGELADO = 0
def tiempo_actual():
    now = datetime.now(timezone.utc)
    TIEMPO_CONGELADO = now
    return TIEMPO_CONGELADO

async def datos_historicos_por_instrumento(instrumento_id,fecha_inicio, fecha_fin):# datos historicos
    METRIS_BASE_URI = settings.METRIS_BASE_URI
    METRIS_TOKEN = settings.METRIS_TOKEN
    headers = {
        "Authorization": f"Bearer {METRIS_TOKEN}"
    }
    url = f"{METRIS_BASE_URI}/api/public/Historian/trendvalues"
    params = {
        "ID": instrumento_id,
        "TagID": instrumento_id,
        "Start": fecha_inicio.strftime("%Y-%m-%dT%H:%M:%SZ"),#Hora actual menos una hora en formato ISO 8601
        "End": fecha_fin.strftime("%Y-%m-%dT%H:%M:%SZ"),#Hora actual en formato ISO 8601
        "InterpolationMethod": 0,
        "AggregateFunction": 1,#Cantidad de datos en el mismo json
        "InterpolationResolutionType": 1, #Cuantos puntos yo reconstruyo la serie de tiempo original
        "interpolationresolution": 50000000 #Muestreo de interpolación, cantidad de muestra por minuto (600000000 es un minuto)
    }
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, headers=headers, params=params)
    data = response.json()
    return data

#===================================================EXCEL Y GENERACION MATRIZ A ==========================================================
def datos_excel_instrumentos_mapeados(): #Auxiliar de datos_matriz_a
    BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
    EXCEL_PATH = BASE_DIR / "data" / "TagsCNN_2026-04-30.xlsx"
    excel_instrumentos_mapeados = pd.read_excel(EXCEL_PATH)
    excel_instrumentos_mapeados.to_csv(EXCEL_PATH.with_suffix('.csv'), index=None, header=True)
    df_instrumentos_mapeados = pd.read_csv(EXCEL_PATH.with_suffix('.csv')).convert_dtypes()
    #Se retorna el dataframe leido
    return df_instrumentos_mapeados

def datos_matriz_a():#Matriz A con los datos sin identificador filtrados

    df_mapeo_instrumentos = datos_excel_instrumentos_mapeados() #Aca es un dataframe
    cols_str = df_mapeo_instrumentos.select_dtypes(include=["object", "string"]).columns
    df_mapeo_instrumentos[cols_str] = df_mapeo_instrumentos[cols_str].fillna("Vacio").apply(lambda col: col.str.strip())
    cols_num = df_mapeo_instrumentos.select_dtypes(include=[np.number]).columns
    df_mapeo_instrumentos[cols_num] = df_mapeo_instrumentos[cols_num].fillna(0)
    df_mapeo_instrumentos = df_mapeo_instrumentos.rename(columns={"ID": "Identificador"})
    df_mapeo_instrumentos = df_mapeo_instrumentos[df_mapeo_instrumentos["Identificador"] > 0] #Se eliminan los instrumentos con identificador 0
    print("Leidos: matriz de excel de instrumentos mapeados...")
    #Mandamos objeto python de los datos del excel filtrados por los identificadores en 0 y columnas sin datos con "Vacio" o "0"
    return df_mapeo_instrumentos

async def obtener_ultimo_elemento():
    return