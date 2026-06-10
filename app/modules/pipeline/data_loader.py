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

hc = HistorianClient(base_uri=settings.METRIS_BASE_URI,token=lambda: settings.METRIS_TOKEN)

async def quality_code_metris_api(id):
    hc = HistorianClient(base_uri=settings.METRIS_BASE_URI,token=lambda: settings.METRIS_TOKEN)
    data = hc.get_tag_values(ids=int(id))
    return data

#===========================================Lectura de datos historicos ==================================================================
TIEMPO_CONGELADO = 0
def tiempo_actual():
    now = datetime.now(timezone.utc).replace(microsecond=0)
    TIEMPO_CONGELADO = now
    return TIEMPO_CONGELADO

async def datos_historicos_por_instrumento(instrumento_id, fecha_inicio, fecha_fin, minutos_muestreo,segundos_muestreo):# datos historicos
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


async def ultimo_valor_interpolado_por_instrumento(instrumento_id,fecha_inicio,fecha_fin,minutos_muestreo,segundos_muestreo):

    data = await datos_historicos_por_instrumento(
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
    8986, 9242, 5756, 5754, 9066, 9144, 9145, 4569
]
def ids_booleanos():
    global _ids_booleanos

    if _ids_booleanos is None:

        df_matriz_a = datos_matriz_a()

        _ids_booleanos = set(
            df_matriz_a.loc[
                df_matriz_a["Unidad_de_Ingenieria"]
                .astype(str)
                .str.upper()
                .str.strip()
                == "BOOL",
                "Identificador"
            ]
        )

        _ids_booleanos -= set(
            INSTRUMENTOS_CONTROL_OPERACIONAL
        )
        print(
            f"Booleanos encontrados: {len(_ids_booleanos)}"
        )

    return _ids_booleanos.copy()
def datos_excel_instrumentos_mapeados():
    global _df_instrumentos_mapeados

    if _df_instrumentos_mapeados is None:
        _df_instrumentos_mapeados = pd.read_excel(EXCEL_PATH).convert_dtypes()

    return _df_instrumentos_mapeados.copy()

def datos_matriz_a():
    global _df_matriz_a

    if _df_matriz_a is None:
        df_mapeo_instrumentos = datos_excel_instrumentos_mapeados()

        cols_str = df_mapeo_instrumentos.select_dtypes(include=["object", "string"]).columns
        df_mapeo_instrumentos[cols_str] = (
            df_mapeo_instrumentos[cols_str]
            .fillna("Vacio")
            .apply(lambda col: col.str.strip())
        )

        cols_num = df_mapeo_instrumentos.select_dtypes(include=[np.number]).columns
        df_mapeo_instrumentos[cols_num] = df_mapeo_instrumentos[cols_num].fillna(0)

        df_mapeo_instrumentos = df_mapeo_instrumentos[
            df_mapeo_instrumentos["Identificador"] > 0
        ]

        _df_matriz_a = df_mapeo_instrumentos

    return _df_matriz_a.copy()
#===================================================Filtrados iniciales por subarea ==========================================================

def subarea_chancado_primario():
    df_general_a = datos_matriz_a()
    df_subarea_chancado_primario = df_general_a[df_general_a["Subarea"] == "Chancado Primario"]
    return df_subarea_chancado_primario
def subarea_chancado_secundario():
    df_general_a = datos_matriz_a()
    df_subarea_chancado_secundario = df_general_a[df_general_a["Subarea"] == "Chancado Secundario"]
    return df_subarea_chancado_secundario
def subarea_chancado_terciario():
    df_general_a = datos_matriz_a()
    df_subarea_chancado_terciario = df_general_a[df_general_a["Subarea"] == "Chancado Terciario"]
    return df_subarea_chancado_terciario
def subarea_chancado_cuaternario():
    df_general_a = datos_matriz_a()
    df_subarea_chancado_cuaternario = df_general_a[df_general_a["Subarea"] == "Chancado Cuaternario"]
    return df_subarea_chancado_cuaternario
def subarea_acopio_fino():
    df_general_a = datos_matriz_a()
    df_subarea_acopio_fino = df_general_a[df_general_a["Subarea"] == "Acopio Fino"]
    return df_subarea_acopio_fino

#Tags que no tienen datos de metris
#30695,26998,26995,78517,78503,27010,27007,27004,26996,27023,78518,32342,78502,24560,24556,24559,24558,23939,23935,23849,23848,9094,9092,9093
#9091,9066,9044,9060,8952,9023,9022,8949,6312,6297,6302,5275,5273,5274,5272,5269,5016,5012,5010,5268,5081,5009,5013,5270,5015,5011,5271,5014
#5267,5008,4938,4937,4904,4936,4903,4902,4901,4935,4900,4899

#Tags con datos que no llegan de metris
#89930,90519,90520,85446,8958,6299,6288