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
# =========================Criterios de alertas=========================#
def detectar_cambio_brusco(df):#Aux
    # Evitar división por cero
    epsilon = 1e-6
    # =========================
    # Ratios
    # =========================
    df["Ratio_STD"] = (df["Desviacion_Estandar_c"]/(df["Desviacion_Estandar_b"] + epsilon)).round(3)
    #El promedio de variacion del instrumento
    df["Ratio_Gradiente"] = (df["Gradiente_Max_c"]/(df["Gradiente_Max_b"] + epsilon)).round(3)
    # =========================================================
    # Clasificación de severidad
    # =========================================================
    df["Alerta_Cambio_Brusco"] = "NORMAL"
    # -------------------------
    # Preventivo
    # -------------------------
    df.loc[((df["Ratio_STD"] >= 2)|(df["Ratio_Gradiente"] >= 2)),"Alerta_Cambio_Brusco"] = "PREVENTIVO"
    # -------------------------
    # Crítico
    # -------------------------
    df.loc[((df["Ratio_STD"] >= 5)|(df["Ratio_Gradiente"] >= 5)),"Alerta_Cambio_Brusco"] = "CRITICO"
    # -------------------------
    # Emergencia
    # -------------------------
    df.loc[((df["Ratio_STD"] >= 10)|(df["Ratio_Gradiente"] >= 10)),"Alerta_Cambio_Brusco"] = "EMERGENCIA"
    return df
def detectar_oscilacion(df):#Aux
    epsilon = 1e-6
    # =====================================================
    # Ratio de oscilación
    # =====================================================
    df["Ratio_Oscilacion"] = (
        df["Gradiente_Intensidad_c"]
        /
        (df["Gradiente_Intensidad_b"] + epsilon)
    ).round(3)
    # =====================================================
    # Clasificación
    # =====================================================
    df["Alerta_Oscilacion"] = "NORMAL"
    # Preventivo
    df.loc[
        df["Ratio_Oscilacion"] >= 2,
        "Alerta_Oscilacion"
    ] = "PREVENTIVO"
    # Crítico
    df.loc[
        df["Ratio_Oscilacion"] >= 5,
        "Alerta_Oscilacion"
    ] = "CRITICO"
    # Emergencia
    df.loc[
        df["Ratio_Oscilacion"] >= 10,
        "Alerta_Oscilacion"
    ] = "EMERGENCIA"
    return df
def detectar_sensor_congelado(df):#Aux

    df["Alerta_Senal_Congelada"] = "NORMAL"
    condicion_congelada = (
        (df["Desviacion_Estandar_b"] > 0.1) #No evalua sensores son ultra constantes, por lo tanto historicamente variaba
        &
        (df["Desviacion_Estandar_c"] <= 0.001)#std actual casi 0, lo que indica que la señal ahora está plana
        &
        (df["Gradiente_Intensidad_c"] <= 0.001)#gradiente actual casi 0, lo que indica que ahora no cambia entre muestras
    )
    df.loc[
        condicion_congelada,
        "Alerta_Senal_Congelada"
    ] = "CRITICO"
    return df
def tabla_alertas(df_matriz_b, df_matriz_c):#Tabla importante de alertas que se mandan al frontend
    # Unir por identificador
    df_merge = df_matriz_b.merge(
        df_matriz_c,
        on="Identificador",
        suffixes=("_b", "_c")
    )
    df_merge = detectar_cambio_brusco(df_merge)
    df_merge = detectar_oscilacion(df_merge)
    df_merge = detectar_sensor_congelado(df_merge)
    df_merge = df_merge.replace({np.nan: None})
    columnas_frontend = [
        "Identificador",
        "Alerta_Cambio_Brusco",
        "Alerta_Oscilacion",
        "Alerta_Senal_Congelada"
    ]

    df_merge = df_merge[columnas_frontend]
    return df_merge
