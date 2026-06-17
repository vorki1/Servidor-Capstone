import numpy as np
import pandas as pd

from app.core.logger import crear_logger

logger = crear_logger("Alertas")


COLUMNAS_ALERTAS = [
    "Alerta_Cambio_Brusco",
    "Alerta_Oscilacion",
    "Alerta_Senal_Congelada",
    "Alerta_Todos_Cero",
    "Alerta_Media_Congelada",
    "Alerta_Senal_Recuperada",
]


def detectar_todos_cero(df):
    df["Alerta_Todos_Cero"] = "NORMAL"

    condicion = (
        (df["Media_b"] == 0)
        & (df["Desviacion_Estandar_b"] == 0)
        & (df["Gradiente_Max_b"] == 0)
        & (df["Gradiente_Intensidad_b"] == 0)
        & (df["Media_c"] == 0)
        & (df["Desviacion_Estandar_c"] == 0)
        & (df["Gradiente_Max_c"] == 0)
        & (df["Gradiente_Intensidad_c"] == 0)
    )

    df.loc[condicion, "Alerta_Todos_Cero"] = "CRITICO"

    return df


def detectar_media_congelada(df):
    df["Alerta_Media_Congelada"] = "NORMAL"

    tolerancia_media = 0.01

    condicion = (
        (df["Media_b"].notna())
        & (df["Media_c"].notna())
        & (df["Media_b"] != 0)
        & (df["Media_c"] != 0)
        & (df["Desviacion_Estandar_b"] == 0)
        & (df["Desviacion_Estandar_c"] == 0)
        & (df["Gradiente_Max_b"] == 0)
        & (df["Gradiente_Max_c"] == 0)
        & (df["Gradiente_Intensidad_b"] == 0)
        & (df["Gradiente_Intensidad_c"] == 0)
        & (abs(df["Media_b"] - df["Media_c"]) <= tolerancia_media)
    )

    df.loc[condicion, "Alerta_Media_Congelada"] = "CRITICO"

    return df


def detectar_cambio_brusco(df):
    epsilon = 1e-6

    df["Ratio_STD"] = (
        df["Desviacion_Estandar_c"]
        / (df["Desviacion_Estandar_b"] + epsilon)
    ).round(3)

    df["Ratio_Gradiente"] = (
        df["Gradiente_Max_c"]
        / (df["Gradiente_Max_b"] + epsilon)
    ).round(3)

    df["Alerta_Cambio_Brusco"] = "NORMAL"

    df.loc[
        (df["Ratio_STD"] >= 2) | (df["Ratio_Gradiente"] >= 2),
        "Alerta_Cambio_Brusco"
    ] = "PREVENTIVO"

    df.loc[
        (df["Ratio_STD"] >= 5) | (df["Ratio_Gradiente"] >= 5),
        "Alerta_Cambio_Brusco"
    ] = "CRITICO"

    df.loc[
        (df["Ratio_STD"] >= 10) | (df["Ratio_Gradiente"] >= 10),
        "Alerta_Cambio_Brusco"
    ] = "EMERGENCIA"

    return df


def detectar_oscilacion(df):
    epsilon = 1e-6

    df["Ratio_Oscilacion"] = (
        df["Gradiente_Intensidad_c"]
        / (df["Gradiente_Intensidad_b"] + epsilon)
    ).round(3)

    df["Alerta_Oscilacion"] = "NORMAL"

    df.loc[
        df["Ratio_Oscilacion"] >= 2,
        "Alerta_Oscilacion"
    ] = "PREVENTIVO"

    df.loc[
        df["Ratio_Oscilacion"] >= 5,
        "Alerta_Oscilacion"
    ] = "CRITICO"

    df.loc[
        df["Ratio_Oscilacion"] >= 10,
        "Alerta_Oscilacion"
    ] = "EMERGENCIA"

    return df


def detectar_sensor_congelado(df):
    df["Alerta_Senal_Congelada"] = "NORMAL"

    condicion = (
        (df["Desviacion_Estandar_b"] > 0.1)
        & (df["Desviacion_Estandar_c"] <= 0.001)
        & (df["Gradiente_Intensidad_c"] <= 0.001)
    )

    df.loc[condicion, "Alerta_Senal_Congelada"] = "CRITICO"

    return df


def detectar_senal_recuperada(df):
    df["Alerta_Senal_Recuperada"] = "NORMAL"

    condicion_recuperada_desde_cero = (
        (df["Media_b"] == 0)
        & (df["Desviacion_Estandar_b"] == 0)
        & (df["Gradiente_Max_b"] == 0)
        & (df["Gradiente_Intensidad_b"] == 0)
        & (
            (df["Desviacion_Estandar_c"] > 0.001)
            | (df["Gradiente_Max_c"] > 0.001)
            | (df["Gradiente_Intensidad_c"] > 0.001)
        )
    )

    condicion_recuperada_desde_media = (
        (df["Media_b"].notna())
        & (df["Media_b"] != 0)
        & (df["Desviacion_Estandar_b"] == 0)
        & (df["Gradiente_Max_b"] == 0)
        & (df["Gradiente_Intensidad_b"] == 0)
        & (
            (df["Desviacion_Estandar_c"] > 0.001)
            | (df["Gradiente_Max_c"] > 0.001)
            | (df["Gradiente_Intensidad_c"] > 0.001)
        )
    )

    df.loc[
        condicion_recuperada_desde_cero | condicion_recuperada_desde_media,
        "Alerta_Senal_Recuperada"
    ] = "PREVENTIVO"

    return df


def tabla_alertas(df_matriz_b, df_matriz_c):
    if df_matriz_b.empty or df_matriz_c.empty:
        logger.warning("No se pueden calcular alertas: métricas B o C vacías")
        return pd.DataFrame()

    df_merge = df_matriz_b.merge(
        df_matriz_c,
        on="Identificador",
        suffixes=("_b", "_c")
    )

    logger.info(f"Métricas B: {len(df_matriz_b)}")
    logger.info(f"Métricas C: {len(df_matriz_c)}")
    logger.info(f"Merge B-C: {len(df_merge)}")

    if df_merge.empty:
        logger.warning("No hay coincidencias entre Matriz B y Matriz C")
        return pd.DataFrame()

    df_merge = detectar_cambio_brusco(df_merge)
    df_merge = detectar_oscilacion(df_merge)
    df_merge = detectar_sensor_congelado(df_merge)
    df_merge = detectar_todos_cero(df_merge)
    df_merge = detectar_media_congelada(df_merge)
    df_merge = detectar_senal_recuperada(df_merge)

    df_merge = df_merge.replace({np.nan: None})

    columnas_salida = ["Identificador"] + COLUMNAS_ALERTAS

    return df_merge[columnas_salida]