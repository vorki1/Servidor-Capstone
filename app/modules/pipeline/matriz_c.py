from .matriz_main_builder import generar_dataframe_datos_historicos, generar_dataframe_ultima_columna
from .metricas import metricas_de_matrices
from .data_loader import tiempo_actual
from datetime import timedelta, datetime, timezone
from pathlib import Path
import pandas as pd
import numpy as np

from app.core.logger import crear_logger

logger = crear_logger("Pipeline")

def save_data(df_data):
    # Archivo actual
    ruta_actual = Path(__file__).resolve()
    ruta_csv = (
        ruta_actual.parent.parent.parent
        / "data"
        / "data_matriz_c.csv"
    )
    # Esto ya crea o sobreescribe el archivo
    df_data.to_csv(ruta_csv, index=False)
    return
def leer_metricas_matriz_b():
    ruta_actual = Path(__file__).resolve()
    ruta_metricas_matriz_b_csv = (
        ruta_actual.parent.parent.parent
        / "data"
        / "metricas_matriz_b.csv"
    )
    return pd.read_csv(ruta_metricas_matriz_b_csv)
async def matriz_c_builder():
    df_metricas_b = leer_metricas_matriz_b()#Dataframe metricas de la matriz B
    fecha_fin = tiempo_actual()
    fecha_inicio = fecha_fin - timedelta(minutes=15)
    periodo_muestreo_matriz_c = 5 #Muestreo de interpolación, cantidad de muestra por minuto (50000000 son 5 segundos)
    df_matriz_c_datos = await generar_dataframe_datos_historicos(df_metricas_b,fecha_inicio,fecha_fin,0,periodo_muestreo_matriz_c)
    save_data(df_matriz_c_datos)
    df_medidas_estadisticas = await metricas_de_matrices(df_matriz_c_datos)
    return df_medidas_estadisticas


def leer_datos_matriz_c_csv():
    ruta_actual = Path(__file__).resolve()
    ruta_metricas_matriz_b_csv = (
        ruta_actual.parent.parent.parent
        / "data"
        / "data_matriz_c.csv"
    )
    return pd.read_csv(ruta_metricas_matriz_b_csv)
async def actualizar_ultimo_dato_c():
    df_datos_matriz_c = leer_datos_matriz_c_csv()
    df_datos_matriz_c = df_datos_matriz_c.drop(df_datos_matriz_c.columns[1], axis=1)
    fecha_fin = datetime.now(timezone.utc)
    fecha_inicio = fecha_fin - timedelta(seconds=10)
    segundos_interpolacion  = 5 #Muestreo de interpolación, cantidad de muestra por minuto
    df_ultima_columna = await generar_dataframe_ultima_columna(df_datos_matriz_c["Identificador"],fecha_inicio,fecha_fin,0,segundos_interpolacion)
    df_datos_matriz_c = df_datos_matriz_c.merge(
        df_ultima_columna,
        on="Identificador",
        how="left"
    )
    save_data(df_datos_matriz_c)
    return df_datos_matriz_c
async def  obtener_metricas_matriz_c():#Funcion clave que lee datos csv, actualiza ultimo dato y manda las metricas de la matriz C
    df_datos_matriz_c = await actualizar_ultimo_dato_c()
    df_medidas_estadisticas_matriz_c = await metricas_de_matrices(df_datos_matriz_c)
    return df_medidas_estadisticas_matriz_c

