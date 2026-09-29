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
from time import perf_counter
from statistics import mean, median

from app.core.logger import crear_logger
logger = crear_logger("Pipeline")
TIEMPOS_CONSULTA = []
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

def datos_historicos_por_instrumento(
    instrumento_id,
    fecha_inicio,
    fecha_fin,
    minutos_muestreo,
    segundos_muestreo
):
    params = TrendValuesParameters(
        tag_id=instrumento_id,
        start=fecha_inicio,
        end=fecha_fin,
        interpolation_method=InterpolationMethod.linear,
        interpolation_resolution=ticks_from(
            minutes=minutos_muestreo,
            seconds=segundos_muestreo
        ),
        interpolation_resolution_type=InterpolationResolutionType.ticks,
        aggregate_function=AggregateFunction.median
    )

    inicio = perf_counter()

    try:
        data = hc.get_trend_values(params)

        tiempo = perf_counter() - inicio

        TIEMPOS_CONSULTA.append({
            "id": instrumento_id,
            "tiempo": tiempo,
            "puntos": len(data) if data else 0
        })

        return data

    except Exception as e:
        tiempo = perf_counter() - inicio

        TIEMPOS_CONSULTA.append({
            "id": instrumento_id,
            "tiempo": tiempo,
            "puntos": 0
        })

        logger.error(
            f"[{instrumento_id}] Error Historian "
            f"tras {tiempo:.2f}s -> {e}"
        )

        raise


def limpiar_estadisticas_consultas():
    TIEMPOS_CONSULTA.clear()


def imprimir_estadisticas_consultas():
    if not TIEMPOS_CONSULTA:
        logger.warning("No existen estadísticas de consultas Historian.")
        return

    tiempos = [x["tiempo"] for x in TIEMPOS_CONSULTA]

    logger.info("=" * 60)
    logger.info("ESTADÍSTICAS HISTORIAN")
    logger.info("=" * 60)
    logger.info(f"Consultas      : {len(tiempos)}")
    logger.info(f"Promedio       : {mean(tiempos):.2f}s")
    logger.info(f"Mediana        : {median(tiempos):.2f}s")
    logger.info(f"Mínimo         : {min(tiempos):.2f}s")
    logger.info(f"Máximo         : {max(tiempos):.2f}s")

    # Mostrar solamente consultas que realmente destaquen
    lentos = sorted(
        TIEMPOS_CONSULTA,
        key=lambda x: x["tiempo"],
        reverse=True
    )

    logger.info("-" * 60)
    logger.info("5 CONSULTAS MÁS LENTAS")

    for item in lentos[:5]:
        logger.info(
            f"ID={item['id']} | "
            f"{item['tiempo']:.2f}s | "
            f"{item['puntos']} puntos"
        )

    logger.info("=" * 60)
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

