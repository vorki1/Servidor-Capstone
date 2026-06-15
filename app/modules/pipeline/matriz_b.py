from .data_loader import tiempo_actual

from .filtros_iniciales import (
    subarea_chancado_primario,
    subarea_chancado_secundario,
    subarea_chancado_terciario,
    subarea_chancado_cuaternario,
    subarea_acopio_fino,
    eliminar_instrumentos_control_operacional
)

import pandas as pd
import asyncio
from dateutil.relativedelta import relativedelta

from .filtrar_datos import filtrar_datos_historicos
from .historian_builder import generar_dataframe_datos_historicos
from .metricas import metricas_de_matrices
from .storage import guardar_metricas_matriz_b
from app.core.logger import crear_logger

logger = crear_logger("Pipeline")

SUBAREAS_MATRIZ_B = [
    subarea_chancado_primario,
    subarea_chancado_secundario,
    subarea_chancado_terciario,
    subarea_chancado_cuaternario,
    subarea_acopio_fino,
]

matriz_b_lock = asyncio.Lock()


async def procesar_subarea_matriz_b(
    obtener_subarea,
    fecha_inicio,
    fecha_fin,
    periodo_muestreo_matriz_b,
    semaforo
):
    async with semaforo:
        df_matriz_a_subarea = obtener_subarea()

        if df_matriz_a_subarea.empty:
            logger.warning(f"Subárea vacía: {obtener_subarea.__name__}")
            return None

        subarea = df_matriz_a_subarea["Subarea"].iloc[0]

        logger.info(f"Construyendo matriz B para subárea: {subarea}")

        df_matriz_a_datos = await generar_dataframe_datos_historicos(
            df_matriz=df_matriz_a_subarea,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            minutos_muestreo=periodo_muestreo_matriz_b,
            segundos_muestreo=0
        )

        if df_matriz_a_datos.empty:
            logger.warning(f"No hay datos históricos para subárea: {subarea}")
            return None

        df_matriz_b_datos = filtrar_datos_historicos(
            df_matriz_a_datos,
            subarea
        )

        return df_matriz_b_datos


async def construccion_datos_matriz_b():
    fecha_fin = tiempo_actual()
    fecha_inicio = fecha_fin - relativedelta(days=30)

    periodo_muestreo_matriz_b = 1
    semaforo = asyncio.Semaphore(2)

    tareas = [
        procesar_subarea_matriz_b(
            obtener_subarea=obtener_subarea,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            periodo_muestreo_matriz_b=periodo_muestreo_matriz_b,
            semaforo=semaforo
        )
        for obtener_subarea in SUBAREAS_MATRIZ_B
    ]

    resultados = await asyncio.gather(*tareas)

    matrices_b = [
        df for df in resultados
        if df is not None and not df.empty
    ]

    if not matrices_b:
        logger.warning("No se construyó ninguna matriz B")
        return pd.DataFrame()

    df_matriz_b_final = pd.concat(
        matrices_b,
        ignore_index=True
    )

    df_matriz_b_final = eliminar_instrumentos_control_operacional(
        df_matriz_b_final
    )

    logger.info(
        f"Matriz B final construida con {len(df_matriz_b_final)} instrumentos"
    )

    return df_matriz_b_final


def analizar_metricas_matriz_b(df_metricas):
    total = len(df_metricas)

    df_sospechosos = df_metricas[
        df_metricas["Media"].isna()
        | (df_metricas["Media"] == 0)
        | df_metricas["Desviacion_Estandar"].isna()
        | (df_metricas["Desviacion_Estandar"] == 0)
    ]

    logger.info(
        f"Matriz B métricas | Total: {total} | Sospechosos: {len(df_sospechosos)}"
    )


async def construccion_matriz_b():
    async with matriz_b_lock:
        df_datos_matriz_b = await construccion_datos_matriz_b()

        if df_datos_matriz_b.empty:
            logger.warning("Matriz B vacía. No se calcularon métricas.")
            return "No se construyó la matriz B porque no hay datos disponibles"

        df_medidas_estadisticas = await metricas_de_matrices(
            df_datos_matriz_b
        )

        analizar_metricas_matriz_b(df_medidas_estadisticas)

        guardar_metricas_matriz_b(df_medidas_estadisticas)

        info = (
            "Se construyó la matriz B con sus medidas estadísticas "
            "y se guardó en CSV"
        )

        logger.info(info)

        return info