import asyncio
from datetime import timedelta

import pandas as pd

from .historian_debug import historico_instrumento_metris_api

from ..pipeline.data_loader import (
    datos_matriz_a,
    datos_historicos_por_instrumento,
    tiempo_actual
)


def historico_instrumento():
    data = historico_instrumento_metris_api()

    df = pd.DataFrame(data)

    return df.to_dict(orient="records")


async def areas_unicas():
    df_response = datos_matriz_a()

    areas = (
        df_response["Area"]
        .dropna()
        .astype(str)
        .str.strip()
        .loc[lambda x: x.str.upper() != "VACIO"]
        .loc[lambda x: x.str.upper() != "S/D"]
        .loc[lambda x: x.str.isnumeric()]
        .astype(int)
        .unique()
        .tolist()
    )

    return {
        "areas": sorted(areas)
    }


async def subareas_de_area(area):
    df_response = datos_matriz_a()

    df_filtrado = df_response[
        df_response["Area"] == area
    ]

    subareas = (
        df_filtrado["Subarea"]
        .dropna()
        .unique()
        .tolist()
    )
    
    return {
        "area": area,
        "subareas": subareas
    }


async def sistemas_por_subarea(subarea):
    df = datos_matriz_a()

    sistemas = (
        df[df["Subarea"] == subarea]["Sistema"]
        .dropna()
        .unique()
        .tolist()
    )

    return sistemas


async def instrumentos_por_sistema(sistema):
    df = datos_matriz_a()

    instrumentos = df[
        df["Sistema"] == sistema
    ]

    return instrumentos.to_dict(orient="records")


async def informacion_instrumento(id):
    df_response = datos_matriz_a()

    datos_instrumento = df_response[
        df_response["Identificador"] == id
    ]

    return {
        "informacion_general": datos_instrumento.to_dict(
            orient="records"
        )
    }


async def datos_historicos_por_id(id, minutos):
    if minutos <= 0:
        return {
            "error": "El número de minutos debe ser mayor que cero."
        }

    if minutos > 720:
        return {
            "error": "Intervalo de minutos no válido."
        }

    fecha_fin = tiempo_actual()
    fecha_inicio = fecha_fin - timedelta(minutes=minutos)

    if minutos < 60:
        minutos_muestreo = 0
        segundos_muestreo = 30
    else:
        minutos_muestreo = 1
        segundos_muestreo = 0

    data = await asyncio.to_thread(
        datos_historicos_por_instrumento,
        id,
        fecha_inicio,
        fecha_fin,
        minutos_muestreo,
        segundos_muestreo
    )

    return data