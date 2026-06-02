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
    #areas_unicas = df_response["Area"].unique().tolist()
    areas = (
        df_response["Area"]
        .dropna()
        .loc[lambda x: x != 0]
        .unique()
        .tolist()
    ) 
    data ={
        "areas":areas
    }
    return data
async def subareas_de_area(area):#A visualizador
    df_response = datos_matriz_a()
    df_filtrado = df_response[df_response["Area"] == area]        
    subareas = df_filtrado["Subarea"].unique().tolist()
    data = {
        "area":area,
        "subareas":subareas
    }
    return data
async def sistemas_por_subarea(subarea):
    df = datos_matriz_a()

    sistemas = (
        df[df["Subarea"] == subarea]["Sistema"]
        .dropna()
        .unique()
        .tolist()
    )
    print(
    df[
        ["Subarea", "Sistema"]
    ].drop_duplicates()
)

    return sistemas
async def instrumentos_por_sistema(sistema):
    df = datos_matriz_a()

    instrumentos = df[
        df["Sistema"] == sistema
    ]

    return instrumentos.to_dict(orient="records")

async def informacion_instrumento(id):#A visualizador info del sensor y metricas
    df_response = datos_matriz_a()
    datos_instrumento = df_response[df_response["Identificador"] == id]
    data = {
        "informacion_general": datos_instrumento.to_dict(orient='records'),
    }
    return data
async def datos_historicos_por_id(id,minutos):#A visualizador
    fecha_fin = tiempo_actual()
    fecha_inicio = fecha_fin - timedelta(minutes=minutos)
    minutos_muestreo = 0
    segundos_muestreo = 0
    
    if minutos < 60:
        minutos_muestreo = 0
        segundos_muestreo = 30
        data = await datos_historicos_por_instrumento(id,fecha_inicio,fecha_fin, minutos_muestreo=minutos_muestreo,segundos_muestreo=segundos_muestreo)
        return data
    elif minutos >= 60 and minutos <= 720:
        minutos_muestreo = 1
        segundos_muestreo = 0
        data = await datos_historicos_por_instrumento(id,fecha_inicio,fecha_fin, minutos_muestreo=minutos_muestreo,segundos_muestreo=segundos_muestreo)
        return data
    elif minutos <= 0:
        return {"error": "El número de minutos debe ser mayor que cero."}
    return {"error": "Intervalo de minutos no válido."}