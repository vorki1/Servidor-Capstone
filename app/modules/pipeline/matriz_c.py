from .matriz_main_builder import tiempo_actual, obtener_historico, generar_dataframe_datos_historicos
from .metricas import metricas_de_matrices
from datetime import timedelta, datetime, timezone
from pathlib import Path
import pandas as pd

def save_data(df_data):
    print("====datos guardados=====")
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
    periodo_muestreo_matriz_c = 50000000 #Muestreo de interpolación, cantidad de muestra por minuto (50000000 son 5 segundos)
    df_matriz_c_datos = await generar_dataframe_datos_historicos(df_metricas_b,fecha_inicio,fecha_fin,periodo_muestreo_matriz_c)
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
    now = datetime.now(timezone.utc)
    periodo_muestreo_matriz_c = 50000000 #Muestreo de interpolación, cantidad de muestra por minuto (50000000 son 5 segundos)
    ultimas_filas = await generar_dataframe_datos_historicos(df_datos_matriz_c,now,now, periodo_muestreo_matriz_c)
    df_datos_matriz_c = df_datos_matriz_c.merge(
    ultimas_filas,
        on="Identificador",
        how="left"
    )
    save_data(df_datos_matriz_c)
    return

def diferencia_matriz_b_matriz_c(df_matriz_b, df_matriz_c):
    print("=========Estadísticos Matriz B =================")
    print(df_matriz_b)
    print("=========Estadísticos Matriz C =================")
    print(df_matriz_c)
    # Unir por identificador
    df_merge = df_matriz_b.merge(
        df_matriz_c,
        on="Identificador",
        suffixes=("_b", "_c")
    )

    # Crear dataframe resultado
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
    ).round(3)
    print("=========Diferencia Matriz B vs Matriz C =================")
    print(df_diferencia)
    return df_diferencia