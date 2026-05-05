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

def metricas_matriz_b():
    df_datos_matriz_b = construccion_matriz_b()

    print(df_datos_matriz_b)
    ###########Este ejemplo esta enfocado en desarrollar una matriz basica de los instrumentos del Chancador primario ##########################
    df_medidas_estadisticas = pd.DataFrame({
        "Identificador": pd.Series(dtype="Int64"),  # entero
        "Media": pd.Series(dtype="float"),
        "Desviacion_Estandar": pd.Series(dtype="float"),
        "Minimo": pd.Series(dtype="float"),
        "Maximo": pd.Series(dtype="float"),
        "Gradiente": pd.Series(dtype="float")
    })

    #Trabajo n°1 añadir identificadores a cada fila de la matriz B
    df_medidas_estadisticas["Identificador"] = df_datos_matriz_b["Identificador"]
    df_medidas_estadisticas=df_medidas_estadisticas.fillna(0)
    
    #Trabajo n°2 calcular medidas estadisticas para cada instrumento
    for identificador in df_medidas_estadisticas["Identificador"]: #Media y desviación estandar
        fila = df_datos_matriz_b[df_datos_matriz_b["Identificador"] == identificador] #fila de los datos con el identificador
        df_medidas_estadisticas.loc[df_medidas_estadisticas["Identificador"] == identificador, "Media"] = round(fila.iloc[:, 1:].mean(axis=1).iloc[0], 2)
        df_medidas_estadisticas.loc[df_medidas_estadisticas["Identificador"] == identificador, "Desviacion_Estandar"] = round(fila.iloc[:, 1:].std(axis=1).iloc[0], 2)
    for identificador in df_datos_matriz_b["Identificador"]: #Calculo del z_score para el ultimo valor de cada instrumento
        desviacion_estandar = df_medidas_estadisticas.loc[df_medidas_estadisticas["Identificador"]== identificador, "Desviacion_Estandar"].values[0]
        if abs(desviacion_estandar) < 1e-10:
            desviacion_estandar = 0
        media = round(df_medidas_estadisticas.loc[df_medidas_estadisticas["Identificador"]==identificador, "Media"].values[0],4)
        fila_medidas = df_medidas_estadisticas.loc[df_medidas_estadisticas["Identificador"]==identificador]
        ultimo_valor = df_datos_matriz_b.loc[df_datos_matriz_b["Identificador"]==identificador].iloc[:, -1].values[0]
        z_score = calcular_z_score(ultimo_valor, media, desviacion_estandar) #Posible envio de alerta

    print("Envio la matriz B con sus métricas")
    return df_datos_matriz_b, df_medidas_estadisticas
