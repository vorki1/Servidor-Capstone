from .data_loader import quality_code_metris_api

import asyncio
import pandas as pd

from app.core.logger import crear_logger


logger = crear_logger("Pipeline")


MAX_CONSULTAS_QUALITY_CODE = 10


COLUMNAS_METRICAS = [
    "Identificador",
    "Media",
    "Desviacion_Estandar",
    "Quality_code",
    "Gradiente_Max",
    "Gradiente_Intensidad",
]


async def obtener_quality_code_instrumento(identificador):
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
    if not identificadores:
        return pd.DataFrame(
            columns=["Identificador", "Quality_code"]
        )

    semaforo = asyncio.Semaphore(MAX_CONSULTAS_QUALITY_CODE)

    async def tarea_limitada(identificador):
        async with semaforo:
            return await obtener_quality_code_instrumento(
                identificador
            )

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


def obtener_columnas_tiempo(df_datos_matriz):
    columnas_tiempo = [
        col for col in df_datos_matriz.columns
        if col != "Identificador"
    ]

    return sorted(columnas_tiempo)


def crear_metricas_vacias(df_datos_matriz):
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


def calcular_metricas_estadisticas(
    df_datos_matriz,
    columnas_tiempo
):
    identificadores = (
        df_datos_matriz["Identificador"]
        .astype("Int64")
    )

    valores = df_datos_matriz[columnas_tiempo].apply(
        pd.to_numeric,
        errors="coerce"
    )

    gradiente = valores.diff(axis=1).abs()

    df_metricas = pd.DataFrame({
        "Identificador": identificadores,
        "Media": valores.mean(axis=1, skipna=True).round(3),
        "Desviacion_Estandar": valores.std(axis=1, skipna=True).round(3),
        "Gradiente_Max": gradiente.max(axis=1, skipna=True).round(3),
        "Gradiente_Intensidad": gradiente.mean(axis=1, skipna=True).round(3),
    })

    return df_metricas


async def agregar_quality_code(df_metricas):
    identificadores = (
        df_metricas["Identificador"]
        .dropna()
        .astype(int)
        .drop_duplicates()
        .tolist()
    )

    df_quality = await obtener_quality_codes(identificadores)

    if df_quality.empty:
        df_metricas["Quality_code"] = None
        return df_metricas

    df_metricas = df_metricas.merge(
        df_quality,
        on="Identificador",
        how="left"
    )

    return df_metricas


async def metricas_de_matrices(df_datos_matriz):
    if df_datos_matriz.empty:
        return pd.DataFrame(columns=COLUMNAS_METRICAS)

    df_datos_matriz = df_datos_matriz.reset_index(drop=True)

    if "Identificador" not in df_datos_matriz.columns:
        logger.warning("No se pueden calcular métricas: falta Identificador")
        return pd.DataFrame(columns=COLUMNAS_METRICAS)

    columnas_tiempo = obtener_columnas_tiempo(df_datos_matriz)

    if not columnas_tiempo:
        return crear_metricas_vacias(df_datos_matriz)

    df_datos_matriz = df_datos_matriz[
        ["Identificador"] + columnas_tiempo
    ]

    df_metricas = calcular_metricas_estadisticas(
        df_datos_matriz,
        columnas_tiempo
    )

    df_metricas = await agregar_quality_code(df_metricas)

    return df_metricas[COLUMNAS_METRICAS]