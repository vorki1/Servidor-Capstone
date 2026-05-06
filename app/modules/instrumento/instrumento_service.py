import pandas as pd
import math
from io import StringIO
from fastapi.responses import StreamingResponse
from .instrumento_repository_metris import historico_instrumento_metris_api, quality_code_metris_api
from .pipeline.metricas import metricas_matriz_b

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

def matriz_b():
    df_datos_instrumentos, df_medidas_estadisticas = metricas_matriz_b()
    data ={
        "datos_instrumentos": df_datos_instrumentos.to_dict(orient='records'),
        "medidas_estadisticas": df_medidas_estadisticas.to_dict(orient='records')
    }
    return data