from ..pipeline.matriz_b import construccion_matriz_b
from ..pipeline.matriz_c import matriz_c_builder, leer_metricas_matriz_b,obtener_metricas_matriz_c,datos_y_alertas_instrumentos
from ..alertas.criterios_alertas import tabla_alertas
import numpy as np


async def matriz_b():#Matriz B, historico, metricas y metricas en CSV
    info = await construccion_matriz_b()
    return { "message": info }
async def matriz_datos_c():#Metricas de matriz C
    df_medidas_estadisticas = await matriz_c_builder() #data frame de datos historicos matriz C
    df_medidas_estadisticas = df_medidas_estadisticas.replace({np.nan: None})
    return df_medidas_estadisticas

async def tabla_ultimas_alertas(): #Diferencia para analizar matriz B y matriz C
    metricas_matriz_b = leer_metricas_matriz_b()#Leemos CSV con medidas estadisticas y genera el DataFrame
    metricas_matriz_c = await obtener_metricas_matriz_c()#Obtenemos las metricas de la matriz C, con el ultimo dato actualizado
    df_tabla_alertas = tabla_alertas(metricas_matriz_b,metricas_matriz_c)
    print(df_tabla_alertas)
    df_tabla_alertas = datos_y_alertas_instrumentos(df_tabla_alertas)
    return df_tabla_alertas.to_dict(orient="records")