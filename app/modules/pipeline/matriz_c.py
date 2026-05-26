from .matriz_main_builder import obtener_historico, generar_dataframe_datos_historicos
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
    return df_matriz_c_datos,df_medidas_estadisticas
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
    fecha_inicio = fecha_fin - timedelta(seconds=5)
    periodo_muestreo_matriz_c = 50000000 #Muestreo de interpolación, cantidad de muestra por minuto (50000000 son 5 segundos)
    ultimas_filas = await generar_dataframe_datos_historicos(df_datos_matriz_c,fecha_inicio,fecha_fin, periodo_muestreo_matriz_c)
    df_datos_matriz_c = df_datos_matriz_c.merge(
    ultimas_filas,
        on="Identificador",
        how="left"
    )
    save_data(df_datos_matriz_c)
    return "Información actualizada"

def detectar_cambio_brusco(df):
    print(df.head())
    # Evitar división por cero
    epsilon = 1e-6
    # =========================
    # Ratios
    # =========================
    df["Ratio_STD"] = (
        df["Desviacion_Estandar_c"]
        /
        (df["Desviacion_Estandar_b"] + epsilon)
    ).round(3)

    df["Ratio_Gradiente"] = ( #El promedio de variacion del instrumento
        df["Gradiente_Intensidad_c"]
        /
        (df["Gradiente_Intensidad_b"] + epsilon)
    ).round(3)
    print(
        df[
            [
                "Identificador",
                "Ratio_STD",
                "Ratio_Gradiente"
            ]
        ]
    )

    return df

def detectar_oscilacion(df):
    return df
def detectar_sensor_congelado(df):
    return df

def diferencia_matriz_b_matriz_c(df_matriz_b, df_matriz_c):
    # Unir por identificador
    df_merge = df_matriz_b.merge(
        df_matriz_c,
        on="Identificador",
        suffixes=("_b", "_c")
    )
    df_merge = detectar_cambio_brusco(df_merge)
    df_merge = df_merge.replace({np.nan: None})
    return df_merge

"""     # Crear dataframe resultado
    df_diferencia = pd.DataFrame()
    # Mantener identificador
    df_diferencia["Identificador"] = df_merge["Identificador"]
    # Diferencias
    df_diferencia["Diff_Media"] = (
        df_merge["Media_c"] - df_merge["Media_b"]
    ).round(3)
    df_diferencia["Diff_Desviacion"] = (
        df_merge["Desviacion_Estandar_c"] -
        df_merge["Desviacion_Estandar_b"]
    ).round(3)
    df_diferencia["Diff_Gradiente_Promedio"] = (
        df_merge["Gradiente_Promedio_c"] -
        df_merge["Gradiente_Promedio_b"]
    ).round(3)
    df_diferencia["Diff_Gradiente_Max"] = (
        df_merge["Gradiente_Max_c"] -
        df_merge["Gradiente_Max_b"]
    ).round(3)
    df_diferencia["Diff_Gradiente_Intensidad"] = (
        df_merge["Gradiente_Intensidad_c"] -
        df_merge["Gradiente_Intensidad_b"]
    ).round(3) """