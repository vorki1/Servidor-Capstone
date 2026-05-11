import pandas as pd
import math
from io import StringIO
from fastapi.responses import StreamingResponse
from .instrumento_repository_metris import historico_instrumento_metris_api, quality_code_metris_api,datos_historicos_por_instrumento
from .pipeline.metricas import metricas_matriz_b, metricas_de_matrices
from .pipeline.data_loader import datos_matriz_a
from .pipeline.matriz_c import matriz_c_builder, leer_metricas_matriz_b,actualizar_ultimo_dato_c

def historico_instrumento():#Para datos si necesita el Gilbert, sino para la casa nomas
    #Llamada a la API de "Metris" para obtener datos historicos de un instrumento
    data = historico_instrumento_metris_api()
    df = pd.DataFrame(data)
    """
    df = df.astype(object).where(pd.notnull(df), None)
     # Asegurar solo columnas necesarias
    df = df[["x", "y"]]
    # Crear CSV en memoria
    buffer = StringIO()
    df.to_csv(buffer, index=False)

    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=6248_2026.csv"
        }    ) """
    return df.to_dict(orient='records')  # Convertir el DataFrame a una lista de diccionarios

def quality_code():
    
    return quality_code_metris_api()



async def areas_unicas():#A visualizador
    df_response = datos_matriz_a()
    areas_unicas = df_response["Area"].unique().tolist()
    data ={
        "areas":areas_unicas
    }
    return data
async def subareas_de_area(area):#A visualizador
    df_response = datos_matriz_a()
    df_filtrado = df_response[df_response["Area"] == area]        
    subareas = df_filtrado["Sub"].unique().tolist()
    print(subareas)
    data = {
        "area":area,
        "subareas":subareas
    }
    return data
async def instrumentos_por_subarea(subarea):#A visualizador
    df_response = datos_matriz_a()
    df_instrumentos = df_response[df_response["Sub"]==subarea]
    area = df_instrumentos["Area"].unique()
    obs = ""
    if len(area) > 1:
        obs = "Estan las siguientes areas asociadas a este instrumento", area
    else:
        obs = "Todo en orden"
        area = int(area[0])
    data = {
        "obs":obs,
        "area":area,
        "subarea":subarea,
        "instrumentos":df_instrumentos.to_dict(orient='records')
    }
    return data
async def datos_historicos_por_id(id,minutos):#A visualizador
    data = await datos_historicos_por_instrumento(id,minutos)
    print(data)
    return

async def matriz_b():
    df_datos_instrumentos, df_medidas_estadisticas = await metricas_matriz_b()
    data ={
        "Observacion":"Se genero el CSV con las medidas estadisticas",
        "datos_instrumentos": df_datos_instrumentos.to_dict(orient='records'),
        "medidas_estadisticas": df_medidas_estadisticas.to_dict(orient='records')
    }
    return data

async def matriz_datos_c():
    datos_historicos_c,df_medidas_estadisticas = await matriz_c_builder() #data frame de datos historicos matriz C
    return df_medidas_estadisticas

async def actualizar_datos_matriz_c():
    data = await actualizar_ultimo_dato_c()
    return data

async def diferencia_metricas():
    data_matriz_b = leer_metricas_matriz_b()#Leemos CSV con medidas estadisticas y genera el DataFrame
    data_matriz_c = await matriz_datos_c()#Leemos los ultimos datos de la matriz y traemos el DataFrame
    
    print("Matriz B \n",data_matriz_b)
    print("Matriz C \n",data_matriz_c)
    data = {
        "Metricas matriz B": data_matriz_b.to_dict(orient="records"),
        "Metricas matriz C": data_matriz_c.to_dict(orient="records")
    }
    return data