import pandas as pd
from .instrumento_repository_metris import historico_instrumento_metris_api
from ..pipeline.data_loader import datos_matriz_a, datos_historicos_por_instrumento, tiempo_actual
from ..pipeline.matriz_c import leer_metricas_matriz_b
from datetime import timedelta

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
async def informacion_instrumento(id):#A visualizador info del sensor y metricas
    df_response = datos_matriz_a()
    datos_instrumento = df_response[df_response["Identificador"] == id]
    df_metricas_matriz_b = leer_metricas_matriz_b()
    datos_metricas_instrumento = df_metricas_matriz_b[df_metricas_matriz_b["Identificador"] == id]
    data = {
        "informacion_general": datos_instrumento.to_dict(orient='records'),
        "metricas_instrumento":datos_metricas_instrumento.to_dict(orient='records')
    }
    return data
async def datos_historicos_por_id(id,minutos):#A visualizador
    fecha_fin = tiempo_actual()
    fecha_inicio = fecha_fin - timedelta(minutes=minutos)
    periodo_muestreo_matriz_c = 50000000 #Muestreo de interpolación, cantidad de muestra por minuto (50000000 son 5 segundos)
    data = await datos_historicos_por_instrumento(id,fecha_inicio,fecha_fin, periodo_muestreo_matriz_c)
    return {"Datos historicos":data}
