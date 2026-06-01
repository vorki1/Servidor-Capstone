from .data_loader import (
    tiempo_actual,
    subarea_chancado_primario,
    subarea_chancado_secundario,
    subarea_chancado_terciario,
    subarea_chancado_cuaternario,
    subarea_molienda_cuaternaria,
    subarea_acopio_fino
)
import matplotlib.pyplot as plt
import pandas as pd
from dateutil.relativedelta import relativedelta
from .filtrar_datos import filtrar_datos_historicos
from .matriz_main_builder import generar_dataframe_datos_historicos
from .metricas import metricas_de_matrices, metrics_save
from app.core.logger import crear_logger
logger = crear_logger("Pipeline")

async def construccion_datos_matriz_b():#Se construye la matriz B con datos historicos
    fecha_fin = tiempo_actual()
    fecha_inicio = fecha_fin - relativedelta(days=2)
    periodo_muestreo_matriz_b = 1 #Muestreo de interpolación, cantidad de muestra por minuto (600000000 es un minuto)
    df_matriz_a_chancado_primario = subarea_chancado_primario() #Entrega un DF
    df_matriz_a_datos = await generar_dataframe_datos_historicos(df_matriz_a_chancado_primario, fecha_inicio, fecha_fin, periodo_muestreo_matriz_b,segundos_muestreo=0)
    subarea = df_matriz_a_chancado_primario["Subarea"].iloc[0]
    df_matriz_b_datos = filtrar_datos_historicos(df_matriz_a_datos,subarea)
    # ==========================================
    # GRAFICAR INSTRUMENTO 8949
    # ==========================================

    fila_8949 = df_matriz_b_datos[
        df_matriz_b_datos["Identificador"] == 8949
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

    plt.title("Instrumento 8949")
    plt.xlabel("Timestamp")
    plt.ylabel("Valor")
    plt.grid(True)

    plt.show()
    logger.info("Envio la matriz B Construida con datos historicos")
    return df_matriz_b_datos

async def construccion_matriz_b():
    df_datos_matriz_b = await construccion_datos_matriz_b() #Datos historicos matriz B
    df_medidas_estadisticas = await metricas_de_matrices(df_datos_matriz_b) #Medidas estadisticas
    metrics_save(df_medidas_estadisticas)#Almacenar medidas estadisticas
    info = "Se construyo la matriz B con sus medidas estadisticas y se guardaron en CSV"
    logger.info(info)
    return info