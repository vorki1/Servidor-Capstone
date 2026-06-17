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

from app.core.logger import crear_logger
logger = crear_logger("Pipeline")
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

