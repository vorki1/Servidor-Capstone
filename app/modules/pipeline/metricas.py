from .data_loader import quality_code_metris_api

import asyncio
import math

import pandas as pd

from app.core.logger import crear_logger

logger = crear_logger("Pipeline")


def redondeo_arriba_abs(x):
    return math.ceil(x * 100) / 100


def calcular_z_score(valor, media, desviacion_estandar):
    if desviacion_estandar == 0:
        return 0

    return redondeo_arriba_abs(
        (valor - media) / desviacion_estandar
    )


async def integracion_quality_code(identificador):
    try:
        data = await asyncio.to_thread(
            quality_code_metris_api,
            identificador
        )

        if not data:
            return None

        return {
            "Identificador": identificador,
            "Quality_code": data[0].get("quality")
        }

    except Exception as e:
        logger.error(
            f"Error obteniendo quality code para {identificador}: {e}"
        )
        return None


async def obtener_quality_codes(identificadores):
    semaphore = asyncio.Semaphore(10)

    async def tarea_limitada(identificador):
        async with semaphore:
            return await integracion_quality_code(identificador)

    resultados = await asyncio.gather(
        *[
            tarea_limitada(identificador)
            for identificador in identificadores
        ]
    )

    registros = [
        resultado for resultado in resultados
        if resultado is not None
    ]

    if not registros:
        return pd.DataFrame(
            columns=["Identificador", "Quality_code"]
        )

    return pd.DataFrame(registros)


async def metricas_de_matrices(df_datos_matriz):
    if df_datos_matriz.empty:
        return pd.DataFrame()

    df_datos_matriz = df_datos_matriz.reset_index(drop=True)

    columnas_tiempo = [
        col for col in df_datos_matriz.columns
        if col != "Identificador"
    ]

    columnas_tiempo = sorted(columnas_tiempo)

    if not columnas_tiempo:
        return pd.DataFrame({
            "Identificador": (
                df_datos_matriz["Identificador"]
                .astype("Int64")
            ),
            "Media": None,
            "Desviacion_Estandar": None,
            "Quality_code": None,
            "Gradiente_Max": None,
            "Gradiente_Intensidad": None,
        })

    df_datos_matriz = df_datos_matriz[
        ["Identificador"] + columnas_tiempo
    ]

    identificadores = (
        df_datos_matriz["Identificador"]
        .astype("Int64")
    )

    valores = df_datos_matriz[columnas_tiempo].apply(
        pd.to_numeric,
        errors="coerce"
    )

    df_medidas_estadisticas = pd.DataFrame({
        "Identificador": identificadores,
        "Media": valores.mean(axis=1, skipna=True).round(3),
        "Desviacion_Estandar": valores.std(axis=1, skipna=True).round(3),
    })

    df_quality = await obtener_quality_codes(
        identificadores.dropna().astype(int).tolist()
    )

    if not df_quality.empty:
        df_medidas_estadisticas = df_medidas_estadisticas.merge(
            df_quality,
            on="Identificador",
            how="left"
        )
    else:
        df_medidas_estadisticas["Quality_code"] = None

    gradiente = valores.diff(axis=1).abs()

    df_medidas_estadisticas["Gradiente_Max"] = (
        gradiente.max(axis=1, skipna=True).round(3)
    )

    df_medidas_estadisticas["Gradiente_Intensidad"] = (
        gradiente.mean(axis=1, skipna=True).round(3)
    )

    return df_medidas_estadisticas