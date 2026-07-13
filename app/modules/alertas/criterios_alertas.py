import numpy as np
import pandas as pd

from app.core.logger import crear_logger
from app.modules.instrumento.instrumento_service import datos_matriz_a

logger = crear_logger("Alertas")


COLUMNAS_ALERTAS = [
    "Alerta_Cambio_Brusco",
    "Alerta_Oscilacion",
    "Alerta_Senal_Congelada",
    "Alerta_Todos_Cero",
    "Alerta_Media_Congelada",
    "Alerta_Senal_Recuperada",
]

UMBRALES_DELTA_CAMBIO_BRUSCO = {
    "TEMPERATURA": {
        "PREVENTIVO": 5,
        "CRITICO": 15,
        "EMERGENCIA": 30,
    },
    "CORRIENTE": {
        "PREVENTIVO": 15,
        "CRITICO": 40,
        "EMERGENCIA": 80,
    },
    "PORCENTAJE": {
        "PREVENTIVO": 10,
        "CRITICO": 25,
        "EMERGENCIA": 50,
    },
    "PRESION": {
        "PREVENTIVO": 5,
        "CRITICO": 15,
        "EMERGENCIA": 30,
    },
    "VELOCIDAD": {
        "PREVENTIVO": 0.5,
        "CRITICO": 1.5,
        "EMERGENCIA": 3,
    },
    "RPM": {
        "PREVENTIVO": 10,
        "CRITICO": 30,
        "EMERGENCIA": 60,
    },
    "MM/S": {
        "PREVENTIVO": 0.2,
        "CRITICO": 0.5,
        "EMERGENCIA": 1,
    },
    "TONELAJE": {
        "PREVENTIVO": 100,
        "CRITICO": 300,
        "EMERGENCIA": 600,
    },
    "POTENCIA": {
        "PREVENTIVO": 50,
        "CRITICO": 150,
        "EMERGENCIA": 300,
    },
    "DEFAULT": {
        "PREVENTIVO": 5,
        "CRITICO": 15,
        "EMERGENCIA": 30,
    },
}


UMBRALES_DELTA_OSCILACION = {
    "TEMPERATURA": {
        "PREVENTIVO": 2,
        "CRITICO": 5,
        "EMERGENCIA": 10,
    },
    "CORRIENTE": {
        "PREVENTIVO": 3,
        "CRITICO": 8,
        "EMERGENCIA": 15,
    },
    "PORCENTAJE": {
        "PREVENTIVO": 3,
        "CRITICO": 8,
        "EMERGENCIA": 15,
    },
    "PRESION": {
        "PREVENTIVO": 1,
        "CRITICO": 3,
        "EMERGENCIA": 6,
    },
    "VELOCIDAD": {
        "PREVENTIVO": 0.2,
        "CRITICO": 0.5,
        "EMERGENCIA": 1,
    },
    "RPM": {
        "PREVENTIVO": 1,
        "CRITICO": 3,
        "EMERGENCIA": 6,
    },
    "MM/S": {
        "PREVENTIVO": 0.05,
        "CRITICO": 0.2,
        "EMERGENCIA": 0.5,
    },
    "TONELAJE": {
        "PREVENTIVO": 20,
        "CRITICO": 50,
        "EMERGENCIA": 100,
    },
    "POTENCIA": {
        "PREVENTIVO": 20,
        "CRITICO": 50,
        "EMERGENCIA": 100,
    },
    "DEFAULT": {
        "PREVENTIVO": 0.5,
        "CRITICO": 2,
        "EMERGENCIA": 5,
    },
}

UMBRALES_MEDIA_CONGELADA = {
    "TEMPERATURA": 0.1,
    "CORRIENTE": 0.1,
    "PORCENTAJE": 0.1,
    "PRESION": 0.05,
    "VELOCIDAD": 0.01,
    "RPM": 1,
    "MM/S": 0.001,
    "TONELAJE": 1,
    "POTENCIA": 1,
    "M^3/H": 1,
    "MM": 0.1,
    "M": 0.01,
    "N/MM": 0.01,
    "DEFAULT": 0.01,
}
def obtener_umbral_delta(unidad_normalizada, tipo_alerta, nivel):
    if tipo_alerta == "CAMBIO_BRUSCO":
        umbrales = UMBRALES_DELTA_CAMBIO_BRUSCO
    elif tipo_alerta == "OSCILACION":
        umbrales = UMBRALES_DELTA_OSCILACION
    else:
        return None

    return umbrales.get(
        unidad_normalizada,
        umbrales["DEFAULT"]
    )[nivel]

def normalizar_unidad(unidad):
    if pd.isna(unidad):
        return "SIN_UNIDAD"

    unidad = str(unidad).strip().lower()

    equivalencias = {
        "°c": "TEMPERATURA",
        "c": "TEMPERATURA",
        "degc": "TEMPERATURA",
        "%": "PORCENTAJE",
        "porcentaje": "PORCENTAJE",
        "amp": "CORRIENTE",
        "a": "CORRIENTE",
        "rpm": "RPM",
        "m/s": "VELOCIDAD",
        "m/seg": "VELOCIDAD",
        "kw": "POTENCIA",
        "bar": "PRESION",
        "psi": "PRESION",
        "kpa": "PRESION",
        "pa": "PRESION",
        "ton": "TONELAJE",
        "vacio": "SIN_UNIDAD",
        "": "SIN_UNIDAD",
    }

    return equivalencias.get(unidad, unidad.upper())


def agregar_unidad_ingenieria(df_merge):
    df_matriz_a = datos_matriz_a()

    columnas_info = [
        "Identificador",
        "Unidad_de_Ingenieria",
        "Area"
    ]

    columnas_disponibles = [
        col for col in columnas_info
        if col in df_matriz_a.columns
    ]

    if "Unidad_de_Ingenieria" not in df_matriz_a.columns:
        logger.warning("Matriz A no contiene Unidad_de_Ingenieria")
        df_merge["Unidad_de_Ingenieria"] = None
        df_merge["Unidad_Normalizada"] = "SIN_UNIDAD"
        return df_merge

    df_info = (
        df_matriz_a[columnas_disponibles]
        .drop_duplicates(subset=["Identificador"])
    )

    df_merge = df_merge.merge(
        df_info,
        on="Identificador",
        how="left"
    )

    df_merge["Unidad_Normalizada"] = (
        df_merge["Unidad_de_Ingenieria"]
        .apply(normalizar_unidad)
    )

    return df_merge

def aplicar_restricciones_servicios_generales(df):
    if "Area" not in df.columns:
        logger.warning(
            "No existe Area para aplicar restricciones de Servicios Generales"
        )
        return df

    mascara_servicios_generales = (
        df["Area"]
        .astype(str)
        .str.strip()
        .eq("3100")
    )

    df.loc[
        mascara_servicios_generales,
        "Alerta_Cambio_Brusco"
    ] = "NORMAL"

    df.loc[
        mascara_servicios_generales,
        "Alerta_Oscilacion"
    ] = "NORMAL"

    df.loc[
        mascara_servicios_generales,
        "Alerta_Senal_Recuperada"
    ] = "NORMAL"

    return df

def guardar_reporte_unidades(df_merge):
    if "Unidad_de_Ingenieria" not in df_merge.columns:
        logger.warning("No existe Unidad_de_Ingenieria en df_merge")
        return

    df_reporte = df_merge.copy()

    df_reporte["Unidad_Normalizada"] = (
        df_reporte["Unidad_de_Ingenieria"]
        .apply(normalizar_unidad)
    )

    resumen = (
        df_reporte
        .groupby("Unidad_Normalizada")
        .agg(
            total=("Identificador", "count"),
            alertas_cambio_brusco=(
                "Alerta_Cambio_Brusco",
                lambda x: (x != "NORMAL").sum()
            ),
            alertas_oscilacion=(
                "Alerta_Oscilacion",
                lambda x: (x != "NORMAL").sum()
            ),
            promedio_delta_gradiente=("Delta_Gradiente", "mean"),
            max_delta_gradiente=("Delta_Gradiente", "max"),
            promedio_delta_oscilacion=("Delta_Oscilacion", "mean"),
            max_delta_oscilacion=("Delta_Oscilacion", "max"),
            max_ratio_gradiente=("Ratio_Gradiente", "max"),
            max_ratio_oscilacion=("Ratio_Oscilacion", "max"),
        )
        .reset_index()
        .sort_values(by="total", ascending=False)
    )

    resumen.to_csv(
        "reporte_unidades.csv",
        index=False,
        encoding="utf-8-sig"
    )


def guardar_candidatos_alertas(df_merge):
    if "Unidad_de_Ingenieria" not in df_merge.columns:
        logger.warning("No existe Unidad_de_Ingenieria para candidatos")
        return

    df_reporte = df_merge.copy()

    df_reporte["Unidad_Normalizada"] = (
        df_reporte["Unidad_de_Ingenieria"]
        .apply(normalizar_unidad)
    )

    columnas = [
        "Identificador",
        "Unidad_de_Ingenieria",
        "Unidad_Normalizada",

        "Desviacion_Estandar_b",
        "Desviacion_Estandar_c",
        "Delta_STD",
        "Ratio_STD",

        "Gradiente_Max_b",
        "Gradiente_Max_c",
        "Delta_Gradiente",
        "Ratio_Gradiente",
        "Alerta_Cambio_Brusco",

        "Gradiente_Intensidad_b",
        "Gradiente_Intensidad_c",
        "Delta_Oscilacion",
        "Ratio_Oscilacion",
        "Alerta_Oscilacion",

        "Media_b",
        "Media_c",
        "Delta_Media",
        "Tolerancia_Media_Congelada",
        "Alerta_Media_Congelada",
    ]

    columnas_existentes = [
        col for col in columnas
        if col in df_reporte.columns
    ]

    df_reporte[columnas_existentes].to_csv(
        "candidatos_alertas.csv",
        index=False,
        encoding="utf-8-sig"
    )

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

    df.loc[condicion, "Alerta_Todos_Cero"] = "PREVENTIVO"

    return df


def obtener_tolerancia_media(unidad_normalizada):
    return UMBRALES_MEDIA_CONGELADA.get(
        unidad_normalizada,
        UMBRALES_MEDIA_CONGELADA["DEFAULT"]
    )
def detectar_media_congelada(df):
    df["Alerta_Media_Congelada"] = "NORMAL"

    if "Unidad_Normalizada" not in df.columns:
        df["Unidad_Normalizada"] = "SIN_UNIDAD"

    df["Tolerancia_Media_Congelada"] = df["Unidad_Normalizada"].apply(
        obtener_tolerancia_media
    )

    df["Delta_Media"] = (
        df["Media_b"] - df["Media_c"]
    ).abs().round(6)

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
        & (df["Delta_Media"] <= df["Tolerancia_Media_Congelada"])
    )

    df.loc[condicion, "Alerta_Media_Congelada"] = "PREVENTIVO"

    return df

def detectar_cambio_brusco(df):
    epsilon = 1e-6

    df["Ratio_STD"] = (
        df["Desviacion_Estandar_c"]
        / (df["Desviacion_Estandar_b"] + epsilon)
    ).round(3)

    df["Delta_STD"] = (
        df["Desviacion_Estandar_c"]
        - df["Desviacion_Estandar_b"]
    ).abs().round(3)

    df["Ratio_Gradiente"] = (
        df["Gradiente_Max_c"]
        / (df["Gradiente_Max_b"] + epsilon)
    ).round(3)

    df["Delta_Gradiente"] = (
        df["Gradiente_Max_c"]
        - df["Gradiente_Max_b"]
    ).abs().round(3)

    df["Alerta_Cambio_Brusco"] = "NORMAL"

    df["Delta_Min_Cambio_Preventivo"] = df["Unidad_Normalizada"].apply(
        lambda unidad: obtener_umbral_delta(
            unidad,
            "CAMBIO_BRUSCO",
            "PREVENTIVO"
        )
    )

    df["Delta_Min_Cambio_Critico"] = df["Unidad_Normalizada"].apply(
        lambda unidad: obtener_umbral_delta(
            unidad,
            "CAMBIO_BRUSCO",
            "CRITICO"
        )
    )

    df["Delta_Min_Cambio_Emergencia"] = df["Unidad_Normalizada"].apply(
        lambda unidad: obtener_umbral_delta(
            unidad,
            "CAMBIO_BRUSCO",
            "EMERGENCIA"
        )
    )

    df.loc[
        (df["Ratio_Gradiente"] >= 2)
        & (df["Delta_Gradiente"] >= df["Delta_Min_Cambio_Preventivo"]),
        "Alerta_Cambio_Brusco"
    ] = "PREVENTIVO"

    df.loc[
        (df["Ratio_Gradiente"] >= 5)
        & (df["Delta_Gradiente"] >= df["Delta_Min_Cambio_Critico"]),
        "Alerta_Cambio_Brusco"
    ] = "CRITICO"

    df.loc[
        (df["Ratio_Gradiente"] >= 10)
        & (df["Delta_Gradiente"] >= df["Delta_Min_Cambio_Emergencia"]),
        "Alerta_Cambio_Brusco"
    ] = "EMERGENCIA"

    return df

def detectar_oscilacion(df):
    epsilon = 1e-6

    df["Ratio_Oscilacion"] = (
        df["Gradiente_Intensidad_c"]
        / (df["Gradiente_Intensidad_b"] + epsilon)
    ).round(3)

    df["Delta_Oscilacion"] = (
        df["Gradiente_Intensidad_c"]
        - df["Gradiente_Intensidad_b"]
    ).abs().round(3)

    df["Alerta_Oscilacion"] = "NORMAL"

    df["Delta_Min_Osc_Preventivo"] = df["Unidad_Normalizada"].apply(
        lambda unidad: obtener_umbral_delta(
            unidad,
            "OSCILACION",
            "PREVENTIVO"
        )
    )

    df["Delta_Min_Osc_Critico"] = df["Unidad_Normalizada"].apply(
        lambda unidad: obtener_umbral_delta(
            unidad,
            "OSCILACION",
            "CRITICO"
        )
    )

    df["Delta_Min_Osc_Emergencia"] = df["Unidad_Normalizada"].apply(
        lambda unidad: obtener_umbral_delta(
            unidad,
            "OSCILACION",
            "EMERGENCIA"
        )
    )

    df.loc[
        (df["Ratio_Oscilacion"] >= 3)
        & (df["Delta_Oscilacion"] >= df["Delta_Min_Osc_Preventivo"]),
        "Alerta_Oscilacion"
    ] = "PREVENTIVO"

    df.loc[
        (df["Ratio_Oscilacion"] >= 6)
        & (df["Delta_Oscilacion"] >= df["Delta_Min_Osc_Critico"]),
        "Alerta_Oscilacion"
    ] = "CRITICO"

    df.loc[
        (df["Ratio_Oscilacion"] >= 12)
        & (df["Delta_Oscilacion"] >= df["Delta_Min_Osc_Emergencia"]),
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

    df.loc[condicion, "Alerta_Senal_Congelada"] = "PREVENTIVO"

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

    df_merge = agregar_unidad_ingenieria(df_merge)

    df_merge = detectar_cambio_brusco(df_merge)
    df_merge = detectar_oscilacion(df_merge)
    df_merge = detectar_sensor_congelado(df_merge)
    df_merge = detectar_todos_cero(df_merge)
    df_merge = detectar_media_congelada(df_merge)
    df_merge = detectar_senal_recuperada(df_merge)
    df_merge = aplicar_restricciones_servicios_generales(df_merge)
    guardar_reporte_unidades(df_merge)
    guardar_candidatos_alertas(df_merge)

    df_merge = df_merge.replace({np.nan: None})

    columnas_salida = ["Identificador"] + COLUMNAS_ALERTAS

    return df_merge[columnas_salida]