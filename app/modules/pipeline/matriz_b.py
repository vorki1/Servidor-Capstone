from .data_loader import tiempo_actual

from .filtros_iniciales import (
    subarea_chancado_primario,
    subarea_chancado_secundario,
    subarea_chancado_terciario,
    subarea_chancado_cuaternario,
    subarea_acopio_fino,
    grupo_area_humeda,
    grupo_relaves,
    grupo_servicios_generales,
    grupo_concentraducto,
    eliminar_instrumentos_control_operacional
)

from time import perf_counter
import pandas as pd
import asyncio
from dateutil.relativedelta import relativedelta

from .filtrar_datos import filtrar_datos_historicos
from .historian_builder import generar_dataframe_datos_historicos
from .metricas import metricas_de_matrices
from .storage import guardar_metricas_matriz_b
from app.core.logger import crear_logger


logger = crear_logger("Pipeline")


DIAS_HISTORICO_MATRIZ_B = 4 #15
PERIODO_MUESTREO_MATRIZ_B = 1
MAX_GRUPOS_CONCURRENTES = 2


GRUPOS_MATRIZ_B = [
    {
        "nombre": "Chancado Primario",
        "grupo_area": "AREA_SECA",
        "obtener_df": subarea_chancado_primario,
    },
    {
        "nombre": "Chancado Secundario",
        "grupo_area": "AREA_SECA",
        "obtener_df": subarea_chancado_secundario,
    },
    {
        "nombre": "Chancado Terciario",
        "grupo_area": "AREA_SECA",
        "obtener_df": subarea_chancado_terciario,
    },
    {
        "nombre": "Chancado Cuaternario",
        "grupo_area": "AREA_SECA",
        "obtener_df": subarea_chancado_cuaternario,
    },
    {
        "nombre": "Acopio Fino",
        "grupo_area": "AREA_SECA",
        "obtener_df": subarea_acopio_fino,
    },
    {
        "nombre": "Area Humeda",
        "grupo_area": "AREA_HUMEDA",
        "obtener_df": grupo_area_humeda,
    },
    {
        "nombre": "Relaves",
        "grupo_area": "RELAVES",
        "obtener_df": grupo_relaves,
    },
    {
        "nombre": "Servicios Generales",
        "grupo_area": "SERVICIOS_GENERALES",
        "obtener_df": grupo_servicios_generales,
    },
    {
        "nombre": "Concentraducto",
        "grupo_area": "CONCENTRADUCTO",
        "obtener_df": grupo_concentraducto,
    },
]


matriz_b_lock = asyncio.Lock()


async def procesar_grupo_matriz_b(
    configuracion_grupo,
    fecha_inicio,
    fecha_fin,
    periodo_muestreo_matriz_b,
    semaforo
):
    async with semaforo:
        t0 = perf_counter()

        nombre = configuracion_grupo["nombre"]
        grupo_area = configuracion_grupo["grupo_area"]
        obtener_df = configuracion_grupo["obtener_df"]

        df_matriz_a_grupo = obtener_df()

        if df_matriz_a_grupo.empty:
            logger.warning(f"Matriz B | grupo vacío: {nombre}")
            return None

        area = str(df_matriz_a_grupo["Area"].iloc[0]).strip()
        subarea = nombre

        if grupo_area == "AREA_SECA":
            subarea = str(df_matriz_a_grupo["Subarea"].iloc[0]).strip()

            logger.info(
                f"Construyendo Matriz B para área {area}, "
                f"subárea: {subarea}"
            )
        else:
            areas = (
                df_matriz_a_grupo["Area"]
                .astype(str)
                .str.strip()
                .dropna()
                .drop_duplicates()
                .tolist()
            )

            logger.info(
                f"Construyendo Matriz B para grupo {grupo_area} | "
                f"áreas: {areas} | instrumentos: {len(df_matriz_a_grupo)}"
            )

        df_matriz_a_datos = await generar_dataframe_datos_historicos(
            df_matriz=df_matriz_a_grupo,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            minutos_muestreo=periodo_muestreo_matriz_b,
            segundos_muestreo=0
        )

        if df_matriz_a_datos.empty:
            logger.warning(f"No hay datos históricos para grupo: {nombre}")
            return None

        df_matriz_b_datos = filtrar_datos_historicos(
            df_datos_historicos=df_matriz_a_datos,
            subarea=subarea,
            area=area,
            grupo_area=grupo_area
        )

        logger.info(
            f"{nombre} | Matriz B terminada en "
            f"{perf_counter() - t0:.2f} segundos"
        )

        return df_matriz_b_datos


async def construccion_datos_matriz_b():
    fecha_fin = tiempo_actual()
    fecha_inicio = fecha_fin - relativedelta(days=DIAS_HISTORICO_MATRIZ_B)

    semaforo = asyncio.Semaphore(MAX_GRUPOS_CONCURRENTES)

    tareas = [
        procesar_grupo_matriz_b(
            configuracion_grupo=configuracion_grupo,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            periodo_muestreo_matriz_b=PERIODO_MUESTREO_MATRIZ_B,
            semaforo=semaforo
        )
        for configuracion_grupo in GRUPOS_MATRIZ_B
    ]

    resultados = await asyncio.gather(*tareas)

    matrices_b = [
        df for df in resultados
        if df is not None and not df.empty
    ]

    if not matrices_b:
        logger.warning("No se construyó ninguna Matriz B")
        return pd.DataFrame()

    df_matriz_b_final = pd.concat(
        matrices_b,
        ignore_index=True
    )

    df_matriz_b_final = eliminar_instrumentos_control_operacional(
        df_matriz_b_final
    )

    logger.info(
        f"Matriz B final construida con "
        f"{len(df_matriz_b_final)} instrumentos"
    )

    return df_matriz_b_final


async def construccion_matriz_b():
    async with matriz_b_lock:
        t0 = perf_counter()

        df_datos_matriz_b = await construccion_datos_matriz_b()

        if df_datos_matriz_b.empty:
            logger.warning("Matriz B vacía. No se calcularon métricas.")
            return "No se construyó la matriz B porque no hay datos disponibles"

        df_medidas_estadisticas = await metricas_de_matrices(
            df_datos_matriz_b
        )

        if df_medidas_estadisticas.empty:
            logger.warning("No se calcularon métricas para Matriz B")
            return "No se calcularon métricas para Matriz B"

        guardar_metricas_matriz_b(df_medidas_estadisticas)

        logger.info(
            f"Matriz B total finalizada en "
            f"{perf_counter() - t0:.2f} segundos"
        )

        return (
            "Se construyó la matriz B con sus medidas estadísticas "
            "y se guardó en CSV"
        )