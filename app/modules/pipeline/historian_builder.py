from datetime import datetime, timezone
import asyncio

import pandas as pd

from .data_loader import (
    datos_historicos_por_instrumento,
    ultimo_valor_interpolado_por_instrumento
)

from .filtros_iniciales import eliminar_booleanos
from app.core.logger import crear_logger


logger = crear_logger("Pipeline")


MAX_CONSULTAS_HISTORIAN = 10


async def obtener_historico(
    identificador,
    fecha_inicio,
    fecha_fin,
    minutos_muestreo,
    segundos_muestreo
):
    try:
        data = await asyncio.to_thread(
            datos_historicos_por_instrumento,
            identificador,
            fecha_inicio,
            fecha_fin,
            minutos_muestreo,
            segundos_muestreo
        )

        return {
            "identificador": identificador,
            "data": data
        }

    except Exception as e:
        logger.error(
            f"Error obteniendo histórico para {identificador}: {e}"
        )
        return None


async def obtener_historicos_limitados(
    identificadores,
    fecha_inicio,
    fecha_fin,
    minutos_muestreo,
    segundos_muestreo
):
    semaforo = asyncio.Semaphore(MAX_CONSULTAS_HISTORIAN)

    async def tarea_limitada(identificador):
        async with semaforo:
            return await obtener_historico(
                identificador,
                fecha_inicio,
                fecha_fin,
                minutos_muestreo,
                segundos_muestreo
            )

    tareas = [
        tarea_limitada(identificador)
        for identificador in identificadores
    ]

    return await asyncio.gather(*tareas)


def convertir_historicos_a_dataframe(resultados):
    registros = []

    for resultado in resultados:
        if resultado is None:
            continue

        identificador = resultado["identificador"]
        data = resultado["data"]

        if not data:
            continue

        for punto in data:
            registros.append({
                "Identificador": identificador,
                "timestamp": punto.get("x"),
                "valor": (
                    float(punto.get("y"))
                    if punto.get("y") is not None
                    else None
                )
            })

    if not registros:
        return pd.DataFrame(columns=["Identificador"])

    return pd.DataFrame(registros)


def pivotear_historicos(df_historicos):
    if df_historicos.empty:
        return pd.DataFrame(columns=["Identificador"])

    df_matriz_datos = (
        df_historicos
        .pivot_table(
            index="Identificador",
            columns="timestamp",
            values="valor",
            aggfunc="last"
        )
        .reset_index()
    )

    df_matriz_datos.columns.name = None

    df_matriz_datos = eliminar_booleanos(df_matriz_datos)

    df_matriz_datos["Identificador"] = (
        df_matriz_datos["Identificador"]
        .astype("Int64")
    )

    return df_matriz_datos


async def generar_dataframe_datos_historicos(
    df_matriz,
    fecha_inicio,
    fecha_fin,
    minutos_muestreo,
    segundos_muestreo
):
    if df_matriz.empty or "Identificador" not in df_matriz.columns:
        return pd.DataFrame(columns=["Identificador"])

    identificadores = (
        df_matriz["Identificador"]
        .dropna()
        .astype(int)
        .drop_duplicates()
        .tolist()
    )

    if not identificadores:
        return pd.DataFrame(columns=["Identificador"])

    resultados = await obtener_historicos_limitados(
        identificadores,
        fecha_inicio,
        fecha_fin,
        minutos_muestreo,
        segundos_muestreo
    )

    df_historicos = convertir_historicos_a_dataframe(resultados)

    return pivotear_historicos(df_historicos)


async def obtener_ultimo_valor(
    identificador,
    fecha_inicio,
    fecha_fin,
    minutos_muestreo,
    segundos_muestreo
):
    try:
        resultado = await asyncio.to_thread(
            ultimo_valor_interpolado_por_instrumento,
            identificador,
            fecha_inicio,
            fecha_fin,
            minutos_muestreo,
            segundos_muestreo
        )

        return {
            "identificador": identificador,
            "resultado": resultado
        }

    except Exception as e:
        logger.error(f"Error en instrumento {identificador}: {e}")
        return {
            "identificador": identificador,
            "resultado": None
        }

async def obtener_ultimos_valores_limitados(
    identificadores,
    fecha_inicio,
    fecha_fin,
    minutos_muestreo,
    segundos_muestreo
):
    semaforo = asyncio.Semaphore(MAX_CONSULTAS_HISTORIAN)

    async def tarea_limitada(identificador):
        async with semaforo:
            return await obtener_ultimo_valor(
                identificador,
                fecha_inicio,
                fecha_fin,
                minutos_muestreo,
                segundos_muestreo
            )

    tareas = [
        tarea_limitada(identificador)
        for identificador in identificadores
    ]

    return await asyncio.gather(*tareas)

async def generar_dataframe_ultima_columna(
    df_identificadores,
    fecha_inicio,
    fecha_fin,
    minutos_muestreo,
    segundos_muestreo
):
    identificadores = (
        pd.Series(df_identificadores)
        .dropna()
        .astype(int)
        .drop_duplicates()
        .tolist()
    )

    if not identificadores:
        return pd.DataFrame(columns=["Identificador"])

    timestamp_global = (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
    )

    resultados = await obtener_ultimos_valores_limitados(
        identificadores,
        fecha_inicio,
        fecha_fin,
        minutos_muestreo,
        segundos_muestreo
    )

    registros = []

    for resultado in resultados:
        identificador = resultado["identificador"]
        punto = resultado["resultado"]

        if punto is None:
            logger.warning(f"Sin datos para instrumento {identificador}")
            continue

        registros.append({
            "Identificador": identificador,
            timestamp_global: punto.get("y")
        })

    return pd.DataFrame(registros)