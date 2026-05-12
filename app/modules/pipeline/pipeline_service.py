from ..pipeline.metricas import metricas_matriz_b
from ..pipeline.matriz_c import matriz_c_builder, leer_metricas_matriz_b,actualizar_ultimo_dato_c, diferencia_matriz_b_matriz_c


async def matriz_b():#Matriz B, historico, metricas y metricas en CSV
    df_datos_instrumentos, df_medidas_estadisticas = await metricas_matriz_b()
    data ={
        "Observacion":"Se genero el CSV con las medidas estadisticas",
        "datos_instrumentos": df_datos_instrumentos.to_dict(orient='records'),
        "medidas_estadisticas": df_medidas_estadisticas.to_dict(orient='records')
    }
    return data

async def matriz_datos_c():#Metricas de matriz C
    datos_historicos_c,df_medidas_estadisticas = await matriz_c_builder() #data frame de datos historicos matriz C
    return df_medidas_estadisticas

async def actualizar_datos_matriz_c():#Actualiza solo la historia de tiempo
    data = await actualizar_ultimo_dato_c()
    return data

async def diferencia_metricas():
    data_matriz_b = leer_metricas_matriz_b()#Leemos CSV con medidas estadisticas y genera el DataFrame
    data_matriz_c = await matriz_datos_c()#Leemos los ultimos datos de la matriz y traemos el DataFrame
    df_diferencia_matriz_b_matriz_c = diferencia_matriz_b_matriz_c(data_matriz_b,data_matriz_c)
    data = {
        "Metricas matriz B": data_matriz_b.to_dict(orient="records"),
        "Metricas matriz C": data_matriz_c.to_dict(orient="records")
    }
    return data