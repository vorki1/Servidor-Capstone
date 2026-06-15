from .data_loader import (
    datos_historicos_por_instrumento,
    ultimo_valor_interpolado_por_instrumento
)

from .filtros_iniciales import eliminar_booleanos

import pandas as pd
from datetime import datetime
import asyncio

from app.core.logger import crear_logger

logger = crear_logger("Pipeline")


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


async def generar_dataframe_datos_historicos(
    df_matriz,
    fecha_inicio,
    fecha_fin,
    minutos_muestreo,
    segundos_muestreo
):
    identificadores = df_matriz["Identificador"].tolist()

    semaphore = asyncio.Semaphore(10)

    async def obtener_historico_limitado(identificador):
        async with semaphore:
            return await obtener_historico(
                identificador,
                fecha_inicio,
                fecha_fin,
                minutos_muestreo,
                segundos_muestreo
            )

    tasks = [
        obtener_historico_limitado(id)
        for id in identificadores
    ]

    resultados = await asyncio.gather(*tasks)

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

    df_historicos = pd.DataFrame(registros)

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


async def generar_dataframe_ultima_columna(
    df_identificadores,
    fecha_inicio,
    fecha_fin,
    minutos_muestreo,
    segundos_muestreo
):
    identificadores = df_identificadores.tolist()

    timestamp_global = (
        datetime.now()
        .replace(microsecond=0)
        .astimezone()
        .isoformat()
    )

    tasks = [
        asyncio.to_thread(
            ultimo_valor_interpolado_por_instrumento,
            id,
            fecha_inicio,
            fecha_fin,
            minutos_muestreo,
            segundos_muestreo
        )
        for id in identificadores
    ]

    resultados = await asyncio.gather(
        *tasks,
        return_exceptions=True
    )

    registros = []

    for id, resultado in zip(identificadores, resultados):
        if isinstance(resultado, Exception):
            logger.error(f"Error en instrumento {id}: {resultado}")
            continue

        if resultado is None:
            logger.warning(f"Sin datos para instrumento {id}")
            continue

        valor = resultado.get("y")

        registros.append({
            "Identificador": id,
            timestamp_global: valor
        })

    df_ultima_columna = pd.DataFrame(registros)

    return df_ultima_columna