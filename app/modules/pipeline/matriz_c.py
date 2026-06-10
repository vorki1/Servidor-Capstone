from .matriz_main_builder import (generar_dataframe_datos_historicos, generar_dataframe_ultima_columna,
                                  eliminar_booleanos_control)
from .metricas import metricas_de_matrices
from .data_loader import tiempo_actual, datos_matriz_a,INSTRUMENTOS_CONTROL_OPERACIONAL
from .filtrar_datos import filtrar_datos_historicos
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
    df_metricas_b = leer_metricas_matriz_b()

    df_identificadores_c = df_metricas_b[
        ["Identificador"]
    ].copy()

    df_controles = pd.DataFrame({
        "Identificador": INSTRUMENTOS_CONTROL_OPERACIONAL
    })

    df_identificadores_c = pd.concat(
        [df_identificadores_c, df_controles],
        ignore_index=True
    )

    df_identificadores_c = df_identificadores_c.drop_duplicates(
        subset=["Identificador"]
    )

    df_matriz_a = datos_matriz_a()

    df_identificadores_c = df_identificadores_c.merge(
        df_matriz_a[["Identificador", "Subarea"]],
        on="Identificador",
        how="left"
    )

    fecha_fin = tiempo_actual()
    fecha_inicio = fecha_fin - timedelta(minutes=30)

    periodo_muestreo_matriz_c = 10

    matrices_c = []

    for subarea, df_subarea in df_identificadores_c.groupby("Subarea"):

        if pd.isna(subarea):
            continue

        logger.info(f"Construyendo matriz C para subárea: {subarea}")

        df_subarea_identificadores = df_subarea[
            ["Identificador"]
        ].copy()

        df_matriz_c_subarea = await generar_dataframe_datos_historicos(
            df_subarea_identificadores,
            fecha_inicio,
            fecha_fin,
            0,
            periodo_muestreo_matriz_c
        )

        df_matriz_c_subarea = filtrar_datos_historicos(
            df_matriz_c_subarea,
            subarea
        )

        columnas_tiempo = [
            c for c in df_matriz_c_subarea.columns
            if c != "Identificador"
        ]

        sin_datos = (
            df_matriz_c_subarea[columnas_tiempo]
            .isna()
            .all(axis=1)
        )

        df_matriz_c_subarea = df_matriz_c_subarea[
            ~sin_datos
        ]

        if not df_matriz_c_subarea.empty:
            matrices_c.append(df_matriz_c_subarea)

    if not matrices_c:
        logger.warning("No se construyó matriz C: no hay instrumentos con datos")
        return pd.DataFrame()

    df_matriz_c_datos = pd.concat(
        matrices_c,
        ignore_index=True
    )

    df_matriz_c_datos = eliminar_booleanos_control(
        df_matriz_c_datos
    )

    save_data(df_matriz_c_datos)

    df_medidas_estadisticas = await metricas_de_matrices(
        df_matriz_c_datos
    )

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

