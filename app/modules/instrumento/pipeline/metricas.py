import math
import pandas as pd
from .matriz_builder import construccion_matriz_b

def redondeo_arriba_abs(x):#Aux para redondear el z-score
    return math.ceil(x * 100) / 100
def calcular_z_score(valor, media, desviacion_estandar): #Aux para calcular z-score
    if desviacion_estandar == 0:
        return 0  # Evitar división por cero, si la desviación estándar es cero, el z-score es 0
    z_score = redondeo_arriba_abs((valor - media) / desviacion_estandar)
    if abs(z_score) >= 3:
        pass
        # activar alerta
    return z_score

async def metricas_matriz_b():
    df_datos_matriz_b = await construccion_matriz_b()
    #df_datos_matriz_b = df_datos_matriz_b.sort_index(axis=1) #De menor a mayor
    #df_datos_matriz_b = df_datos_matriz_b.sort_index(axis=1, ascending=False) #De mayor a menor
    #=================================Acscendente=========================================
    cols = df_datos_matriz_b.columns.drop("Identificador")
    cols_sorted = sorted(cols)  # ascendente
    df_datos_matriz_b = df_datos_matriz_b[["Identificador"] + cols_sorted]
    #=====================================================================================
    
    df_medidas_estadisticas = pd.DataFrame({
        "Identificador": pd.Series(dtype="Int64"),  # entero
        "Media": pd.Series(dtype="float"),
        "Desviacion_Estandar": pd.Series(dtype="float"),
    })

    #Trabajo n°1 añadir identificadores a cada fila de la matriz B
    df_medidas_estadisticas["Identificador"] = df_datos_matriz_b["Identificador"]
    df_medidas_estadisticas=df_medidas_estadisticas.fillna(0)
    
    
    #Trabajo n°2 calcular medidas estadisticas para cada instrumento
    valores = df_datos_matriz_b.drop(columns=["Identificador"])

    #============ media y desviación estándar====================================
    df_medidas_estadisticas["Media"] = valores.mean(axis=1).round(3)
    df_medidas_estadisticas["Desviacion_Estandar"] = valores.std(axis=1).round(3)

    #============ Gradiente ====================================================
    valores = df_datos_matriz_b.drop(columns=["Identificador"])
    valores_sorted = valores[cols_sorted]  # Datos ordenados, sin la columna identificador
    gradiente = valores_sorted.diff(axis=1)
    gradiente = gradiente.fillna(0)

    df_gradiente = pd.DataFrame({
        "Identificador": df_datos_matriz_b["Identificador"],
        "Gradiente_Promedio": gradiente.mean(axis=1).round(3),
        "Gradiente_Max": gradiente.abs().max(axis=1).round(3),
        "Gradiente_Intensidad": gradiente.abs().mean(axis=1).round(3),
    })
    df_medidas_estadisticas = df_medidas_estadisticas.merge(
        df_gradiente,
        on="Identificador",
        how="left"
    )

    for identificador in df_datos_matriz_b["Identificador"]: #Calculo del z_score para el ultimo valor de cada instrumento
        desviacion_estandar = df_medidas_estadisticas.loc[df_medidas_estadisticas["Identificador"]== identificador, "Desviacion_Estandar"].values[0]
        if abs(desviacion_estandar) < 1e-10:
            desviacion_estandar = 0
        media = round(df_medidas_estadisticas.loc[df_medidas_estadisticas["Identificador"]==identificador, "Media"].values[0],3)
        fila_medidas = df_medidas_estadisticas.loc[df_medidas_estadisticas["Identificador"]==identificador]
        ultimo_valor = df_datos_matriz_b.loc[df_datos_matriz_b["Identificador"]==identificador].iloc[:, -1].values[0]
        z_score = calcular_z_score(ultimo_valor, media, desviacion_estandar) #Posible envio de alerta

    print("Envio la matriz B con sus métricas")
    return df_datos_matriz_b, df_medidas_estadisticas
