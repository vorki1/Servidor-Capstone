from ..pipeline.matriz_b import construccion_matriz_b
from ..pipeline.matriz_c import matriz_c_builder, leer_metricas_matriz_b,obtener_metricas_matriz_c
from ..alertas.criterios_alertas import tabla_alertas,datos_y_alertas_instrumentos
from . import pipeline_state
import numpy as np
from pathlib import Path
from datetime import datetime


async def matriz_b():#Matriz B, historico, metricas y metricas en CSV
    info = await construccion_matriz_b()
    #await matriz_datos_c()
    return { "message": info }

def obtener_fecha_actualizacion_metricas_matriz_b():
    ruta_actual = Path(__file__).resolve()

    ruta_csv = (
        ruta_actual.parent.parent.parent
        / "data"
        / "metricas_matriz_b.csv"
    )

    if not ruta_csv.exists():
        return {
            "existe": False,
            "mensaje": "El archivo metricas_matriz_b.csv no existe",
            "fecha_ultima_actualizacion": None
        }

    fecha_modificacion = datetime.fromtimestamp(
        ruta_csv.stat().st_mtime
    )

    return {
        "existe": True,
        "archivo": "metricas_matriz_b.csv",
        "fecha_ultima_actualizacion": fecha_modificacion.isoformat(),
        "fecha_ultima_actualizacion_formateada": fecha_modificacion.strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    }
async def matriz_datos_c():#Metricas de matriz C
    df_medidas_estadisticas = await matriz_c_builder() #data frame de datos historicos matriz C
    df_medidas_estadisticas = df_medidas_estadisticas.replace({np.nan: None})
    return df_medidas_estadisticas

async def actualizar_tabla_ultimas_alertas(): #Diferencia para analizar matriz B y matriz C
    metricas_matriz_b = leer_metricas_matriz_b()#Leemos CSV con medidas estadisticas y genera el DataFrame
    metricas_matriz_c = await obtener_metricas_matriz_c()#Obtenemos las metricas de la matriz C, con el ultimo dato actualizado
    df_tabla_alertas = tabla_alertas(metricas_matriz_b,metricas_matriz_c)
    df_tabla_alertas = datos_y_alertas_instrumentos(df_tabla_alertas)
    return df_tabla_alertas.to_dict(orient="records")