from .matriz_main_builder import tiempo_actual, obtener_historico, generar_dataframe_datos_historicos
from .metricas import metricas_de_matrices
import asyncio
from datetime import timedelta, datetime, timezone
from pathlib import Path
import pandas as pd

def save_data(df_data):
    print("====datos guardados=====")
    # Archivo actual
    ruta_actual = Path(__file__).resolve()
    ruta_csv = (
        ruta_actual.parent.parent.parent.parent
        / "data"
        / "data_matriz_c.csv"
    )
    # Esto ya crea o sobreescribe el archivo
    df_data.to_csv(ruta_csv, index=False)
    return

def leer_metricas_matriz_b():
    ruta_actual = Path(__file__).resolve()
    ruta_metricas_matriz_b_csv = (
        ruta_actual.parent.parent.parent.parent
        / "data"
        / "metricas_matriz_b.csv"
    )
    return pd.read_csv(ruta_metricas_matriz_b_csv)


async def matriz_c_builder():
    df_metricas_b = leer_metricas_matriz_b()#Dataframe metricas de la matriz B
    fecha_fin = tiempo_actual()
    fecha_inicio = fecha_fin - timedelta(minutes=15)
    df_matriz_c_datos = await generar_dataframe_datos_historicos(df_metricas_b,fecha_inicio,fecha_fin)
    save_data(df_matriz_c_datos)
    print(df_matriz_c_datos.shape)
    df_medidas_estadisticas = metricas_de_matrices(df_matriz_c_datos)
    return df_matriz_c_datos,df_medidas_estadisticas

def leer_datos_matriz_c_csv():
    ruta_actual = Path(__file__).resolve()
    ruta_metricas_matriz_b_csv = (
        ruta_actual.parent.parent.parent.parent
        / "data"
        / "data_matriz_c.csv"
    )
    return pd.read_csv(ruta_metricas_matriz_b_csv)

def obtener_ultima_fila_datos():
    return

async def actualizar_ultimo_dato_c():
    df_datos_matriz_c = leer_datos_matriz_c_csv()
    df_datos_matriz_c = df_datos_matriz_c.drop(df_datos_matriz_c.columns[1], axis=1)
    print(df_datos_matriz_c.shape)
    now = datetime.now(timezone.utc)
    ultimas_filas = await generar_dataframe_datos_historicos(df_datos_matriz_c,now,now)
    df_datos_matriz_c = df_datos_matriz_c.merge(
    ultimas_filas,
        on="Identificador",
        how="left"
    )
    print(df_datos_matriz_c.shape)
    save_data(df_datos_matriz_c)
    return