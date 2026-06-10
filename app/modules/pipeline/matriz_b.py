from .data_loader import (
    tiempo_actual,
    subarea_chancado_primario,
    subarea_chancado_secundario,
    subarea_chancado_terciario,
    subarea_chancado_cuaternario,
    subarea_acopio_fino
)
import matplotlib.pyplot as plt
import pandas as pd
import asyncio
from dateutil.relativedelta import relativedelta
from .filtrar_datos import filtrar_datos_historicos
from .matriz_main_builder import generar_dataframe_datos_historicos, eliminar_booleanos_control, INSTRUMENTOS_CONTROL_OPERACIONAL
from .metricas import metricas_de_matrices, metrics_save
from app.core.logger import crear_logger
from . import pipeline_state
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

        logger.info(f"Iniciando matriz B para subárea: {subarea}")

        logger.info(f"Consultando históricos para subárea: {subarea}")

        df_matriz_a_datos = await generar_dataframe_datos_historicos(
            df_matriz_a_subarea,
            fecha_inicio,
            fecha_fin,
            periodo_muestreo_matriz_b,
            segundos_muestreo=0
        )

        logger.info(f"Históricos obtenidos para subárea: {subarea}")

        logger.info(f"Aplicando filtros para subárea: {subarea}")

        df_matriz_b_datos = filtrar_datos_historicos(
            df_matriz_a_datos,
            subarea
        )

        logger.info(f"Filtros aplicados para subárea: {subarea}")

        logger.info(f"Matriz B lista para subárea: {subarea}")

        return df_matriz_b_datos

async def construccion_datos_matriz_b():
    fecha_fin = tiempo_actual()
    fecha_inicio = fecha_fin - relativedelta(days=30)

    periodo_muestreo_matriz_b = 1

    semaforo = asyncio.Semaphore(2)

    tareas = [
        procesar_subarea_matriz_b(
            obtener_subarea,
            fecha_inicio,
            fecha_fin,
            periodo_muestreo_matriz_b,
            semaforo
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

    df_matriz_b_final = eliminar_booleanos_control(df_matriz_b_final)

    logger.info(
        f"Matriz B final construida con {len(df_matriz_b_final)} instrumentos"
    )

    return df_matriz_b_final
    # ==========================================
    # GRAFICAR INSTRUMENTO Corriente CR-01:8949, CR-02:8950, PP-01 corriente del fijo 9049, PP-02 corriente del fijo 9053
    #Acopio fino: corriente cv-12 9141, cv-13 8977, cv-14 8978, cv-15 8979, tr-01 4803
    # ==========================================
    """     fila_8949 = df_matriz_b_datos[
        df_matriz_b_datos["Identificador"] == 8978
    ].iloc[0]

    # Quitar identificador
    serie_8949 = fila_8949.drop(labels=["Identificador"])

    # Convertir timestamps
    serie_8949.index = pd.to_datetime(serie_8949.index)

    # Convertir valores numéricos
    serie_8949 = pd.to_numeric(
        serie_8949,
        errors="coerce"
    )

    # Graficar
    plt.figure(figsize=(15, 5))

    plt.plot(
        serie_8949.index,
        serie_8949.values
    )

    plt.title("Instrumento 9053")
    plt.xlabel("Timestamp")
    plt.ylabel("Valor")
    plt.grid(True)

    plt.show() """
def analizar_metricas_matriz_b(df_metricas):
    logger.info("===== Análisis métricas Matriz B =====")

    total = len(df_metricas)

    media_nula = df_metricas["Media"].isna().sum()
    media_cero = (df_metricas["Media"] == 0).sum()

    desviacion_nula = df_metricas["Desviacion_Estandar"].isna().sum()
    desviacion_cero = (df_metricas["Desviacion_Estandar"] == 0).sum()

    quality_nulo = df_metricas["Quality_code"].isna().sum()

    gradiente_max_nulo = df_metricas["Gradiente_Max"].isna().sum()
    gradiente_max_cero = (df_metricas["Gradiente_Max"] == 0).sum()

    logger.info(f"Total instrumentos: {total}")
    logger.info(f"Media nula: {media_nula}")
    logger.info(f"Media en cero: {media_cero}")
    logger.info(f"Desviación nula: {desviacion_nula}")
    logger.info(f"Desviación en cero: {desviacion_cero}")
    logger.info(f"Quality_code nulo: {quality_nulo}")
    logger.info(f"Gradiente_Max nulo: {gradiente_max_nulo}")
    logger.info(f"Gradiente_Max en cero: {gradiente_max_cero}")

    df_sospechosos = df_metricas[
        (
            df_metricas["Media"].isna()
        )
        |
        (
            df_metricas["Media"] == 0
        )
        |
        (
            df_metricas["Desviacion_Estandar"].isna()
        )
        |
        (
            df_metricas["Desviacion_Estandar"] == 0
        )
    ]

    logger.info(f"Instrumentos sospechosos: {len(df_sospechosos)}")

    logger.info(
        df_sospechosos[
            [
                "Identificador",
                "Media",
                "Desviacion_Estandar",
                "Quality_code",
                "Gradiente_Max",
                "Gradiente_Intensidad"
            ]
        ].head(50).to_string(index=False)
    )
async def construccion_matriz_b():
    async with matriz_b_lock:
        df_datos_matriz_b = await construccion_datos_matriz_b()

        df_medidas_estadisticas = await metricas_de_matrices(
            df_datos_matriz_b
        )
        analizar_metricas_matriz_b(df_medidas_estadisticas)
        metrics_save(df_medidas_estadisticas)

        info = (
            "Se construyo la matriz B con sus medidas estadisticas "
            "y la matriz C con los datos historicos. Ambos se guardaron en CSV"
        )

        logger.info(info)

        return info