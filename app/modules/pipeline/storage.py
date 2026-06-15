from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd


DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

RUTA_METRICAS_MATRIZ_B = DATA_DIR / "metricas_matriz_b.csv"
RUTA_DATA_MATRIZ_C = DATA_DIR / "data_matriz_c.csv"


def guardar_metricas_matriz_b(df_metricas):
    RUTA_METRICAS_MATRIZ_B.parent.mkdir(parents=True, exist_ok=True)

    if not RUTA_METRICAS_MATRIZ_B.exists():
        df_metricas.to_csv(RUTA_METRICAS_MATRIZ_B, index=False)
        return

    fecha_modificacion = datetime.fromtimestamp(
        RUTA_METRICAS_MATRIZ_B.stat().st_mtime
    )

    if datetime.now() - fecha_modificacion < timedelta(minutes=1):
        return

    df_existente = pd.read_csv(RUTA_METRICAS_MATRIZ_B)

    ids_nuevos = set(df_metricas["Identificador"])

    df_existente = df_existente[
        ~df_existente["Identificador"].isin(ids_nuevos)
    ]

    df_final = pd.concat(
        [df_existente, df_metricas],
        ignore_index=True
    )

    df_final.to_csv(RUTA_METRICAS_MATRIZ_B, index=False)


def leer_metricas_matriz_b():
    return pd.read_csv(RUTA_METRICAS_MATRIZ_B)


def guardar_datos_matriz_c(df_data):
    RUTA_DATA_MATRIZ_C.parent.mkdir(parents=True, exist_ok=True)
    df_data.to_csv(RUTA_DATA_MATRIZ_C, index=False)


def leer_datos_matriz_c():
    return pd.read_csv(RUTA_DATA_MATRIZ_C)

def obtener_fecha_actualizacion_metricas_matriz_b():
    if not RUTA_METRICAS_MATRIZ_B.exists():
        return {
            "existe": False,
            "mensaje": "El archivo metricas_matriz_b.csv no existe",
            "fecha_ultima_actualizacion": None
        }

    fecha_modificacion = datetime.fromtimestamp(
        RUTA_METRICAS_MATRIZ_B.stat().st_mtime
    )

    return {
        "existe": True,
        "archivo": "metricas_matriz_b.csv",
        "fecha_ultima_actualizacion": fecha_modificacion.isoformat(),
        "fecha_ultima_actualizacion_formateada": fecha_modificacion.strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    }