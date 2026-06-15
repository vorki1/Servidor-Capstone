from app.core.config import settings
from datetime import datetime, timezone
import urllib3
import pandas as pd
from pathlib import Path
import numpy as np
from app.infrastructure.metrisapi.historian import (
    HistorianClient,
    TrendValuesParameters,
    AggregateFunction,
    InterpolationMethod,
    InterpolationResolutionType,
    ticks_from
)
#######CRITICO!!!!!!!!!!!!!!!##################################
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#===================================Historian================================================================
hc = HistorianClient(base_uri=settings.METRIS_BASE_URI,token=lambda: settings.METRIS_TOKEN)

def quality_code_metris_api(id):
    data = hc.get_tag_values(ids=int(id))
    return data

TIEMPO_CONGELADO = 0
def tiempo_actual():
    now = datetime.now(timezone.utc).replace(microsecond=0)
    TIEMPO_CONGELADO = now
    return TIEMPO_CONGELADO

def datos_historicos_por_instrumento(instrumento_id, fecha_inicio, fecha_fin, minutos_muestreo,segundos_muestreo):# datos historicos
    params = TrendValuesParameters(
        tag_id=instrumento_id,
        start=fecha_inicio,
        end=fecha_fin,

        interpolation_method=InterpolationMethod.linear,
        interpolation_resolution=ticks_from(minutes=minutos_muestreo,seconds=segundos_muestreo),
        interpolation_resolution_type=InterpolationResolutionType.ticks,
        aggregate_function=AggregateFunction.median
    )
    data = hc.get_trend_values(params)    
    return data

def ultimo_valor_interpolado_por_instrumento(instrumento_id,fecha_inicio,fecha_fin,minutos_muestreo,segundos_muestreo):

    data = datos_historicos_por_instrumento(
        instrumento_id,
        fecha_inicio,
        fecha_fin,
        minutos_muestreo,
        segundos_muestreo
    )

    if not data:
        return None
    ultimo = data[-1]
    return ultimo

#===================================================EXCEL Y GENERACION MATRIZ A ==========================================================
BASE_DIR = Path(__file__).resolve().parent.parent.parent
EXCEL_PATH = BASE_DIR / "data" / "TagsCNN_area_seca.xlsx"

_df_instrumentos_mapeados = None
_df_matriz_a = None
_ids_booleanos = None
INSTRUMENTOS_CONTROL_OPERACIONAL = [
    8954, 8975, 9092,
    8955, 9599,
    22258, 9016, 6265,
    22180, 9017, 9081,
    8986, 9242, 5756, 5754, 9066, 9144, 9145, 4569,

    # Acopio fino - colectores
    5752,

    # Acopio fino - feeders
    9175, 9176, 9177, 9178, 9179, 9180, 9181, 9182, 9183,
    9184, 9185, 9186, 9187, 9188, 9189, 9190, 9191, 9192,
    9193, 9194, 9195, 9196, 9197, 9198, 9199, 9200, 9201,
]

def datos_excel_instrumentos_mapeados():
    global _df_instrumentos_mapeados

    if _df_instrumentos_mapeados is None:
        _df_instrumentos_mapeados = pd.read_excel(EXCEL_PATH).convert_dtypes()

    return _df_instrumentos_mapeados.copy()

def ids_booleanos():
    global _ids_booleanos

    if _ids_booleanos is None:
        df = datos_excel_instrumentos_mapeados()

        ids_bool = set(
            df.loc[
                df["Unidad_de_Ingenieria"]
                .astype(str)
                .str.upper()
                .str.strip()
                .eq("BOOL"),
                "Identificador"
            ]
        )

        ids_control = set(INSTRUMENTOS_CONTROL_OPERACIONAL)

        _ids_booleanos = ids_bool - ids_control

    return _ids_booleanos.copy()


def datos_matriz_a():
    global _df_matriz_a

    if _df_matriz_a is None:
        df_mapeo_instrumentos = datos_excel_instrumentos_mapeados()

        df_mapeo_instrumentos["Identificador"] = pd.to_numeric(
            df_mapeo_instrumentos["Identificador"],
            errors="coerce"
        )

        df_mapeo_instrumentos = df_mapeo_instrumentos.dropna(
            subset=["Identificador"]
        )

        df_mapeo_instrumentos["Identificador"] = (
            df_mapeo_instrumentos["Identificador"]
            .astype(int)
        )

        df_mapeo_instrumentos = df_mapeo_instrumentos[
            df_mapeo_instrumentos["Identificador"] > 0
        ]

        cols_str = df_mapeo_instrumentos.select_dtypes(
            include=["object", "string"]
        ).columns

        df_mapeo_instrumentos[cols_str] = (
            df_mapeo_instrumentos[cols_str]
            .fillna("Vacio")
            .apply(lambda col: col.str.strip())
        )

        cols_num = df_mapeo_instrumentos.select_dtypes(
            include=[np.number]
        ).columns

        df_mapeo_instrumentos[cols_num] = (
            df_mapeo_instrumentos[cols_num]
            .fillna(0)
        )

        df_mapeo_instrumentos = df_mapeo_instrumentos[
            ~df_mapeo_instrumentos["Identificador"].isin(
                ids_booleanos()
            )
        ]

        _df_matriz_a = df_mapeo_instrumentos

    return _df_matriz_a.copy()