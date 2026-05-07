import pandas as pd
import math
from io import StringIO
from fastapi.responses import StreamingResponse
from .instrumento_repository_metris import historico_instrumento_metris_api, quality_code_metris_api,datos_historicos_por_instrumento
from .pipeline.metricas import metricas_matriz_b
from .pipeline.data_loader import datos_matriz_a

def historico_instrumento():
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

async def matriz_b():
    df_datos_instrumentos, df_medidas_estadisticas = await metricas_matriz_b()
    data ={
        "datos_instrumentos": df_datos_instrumentos.to_dict(orient='records'),
        "medidas_estadisticas": df_medidas_estadisticas.to_dict(orient='records')
    }
    return data

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