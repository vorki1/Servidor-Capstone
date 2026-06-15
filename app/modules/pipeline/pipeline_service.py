from ..pipeline.matriz_b import construccion_matriz_b
from ..pipeline.matriz_c import matriz_c_builder, obtener_metricas_matriz_c
from ..pipeline.storage import (
    leer_metricas_matriz_b,
)
from ..alertas.criterios_alertas import (
    tabla_alertas,
    datos_y_alertas_instrumentos
)
import numpy as np


async def matriz_b():
    info = await construccion_matriz_b()
    return {"message": info}


async def matriz_datos_c():
    df_medidas_estadisticas = await matriz_c_builder()
    df_medidas_estadisticas = df_medidas_estadisticas.replace({np.nan: None})
    return df_medidas_estadisticas


async def actualizar_tabla_ultimas_alertas():
    metricas_matriz_b = leer_metricas_matriz_b()
    metricas_matriz_c = await obtener_metricas_matriz_c()

    df_tabla_alertas = tabla_alertas(
        metricas_matriz_b,
        metricas_matriz_c
    )

    df_tabla_alertas = datos_y_alertas_instrumentos(
        df_tabla_alertas
    )

    return df_tabla_alertas.to_dict(orient="records")