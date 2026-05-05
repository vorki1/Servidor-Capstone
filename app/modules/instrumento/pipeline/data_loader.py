from app.core.config import settings
import requests
from datetime import datetime, timedelta, timezone
import urllib3
import pandas as pd
from pathlib import Path
import numpy as np
#######CRITICO!!!!!!!!!!!!!!!##################################
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TIEMPO_CONGELADO = 0

def tiempo_actual():
    now = datetime.now(timezone.utc)
    TIEMPO_CONGELADO = now
    return TIEMPO_CONGELADO

def datos_historicos_por_instrumento(instrumento_id, primer_muestreo):# datos historicos
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

def datos_excel_instrumentos_mapeados(): #Auxiliar de datos_matriz_a
    BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
    EXCEL_PATH = BASE_DIR / "data" / "TagsCNN_2026-04-30.xlsx"
    excel_instrumentos_mapeados = pd.read_excel(EXCEL_PATH)
    excel_instrumentos_mapeados.to_csv(EXCEL_PATH.with_suffix('.csv'), index=None, header=True)
    df_instrumentos_mapeados = pd.read_csv(EXCEL_PATH.with_suffix('.csv')).convert_dtypes()
    #Se retorna el dataframe leido
    return df_instrumentos_mapeados

def datos_matriz_a():#Matriz A con los datos sin identificador filtrados
    #print("Leyendo CSV de instrumentos...")
    #df_matriz_a = leer_csv_info_general_instrumentos() 
    #Esta funcion lee los csv

    
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