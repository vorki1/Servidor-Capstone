import pandas as pd
import math
from .instrumento_repository_csv import leer_csv_info_general_instrumentos
from .instrumento_repository_metris import historico_instrumento_metris_api, historico_individual_por_instrumento, tiempo_actual


def historico_instrumento():
    #Llamada a la API de "Metris" para obtener datos historicos de un instrumento
    data = historico_instrumento_metris_api()
    df = pd.DataFrame(data)
    
    return df.to_dict(orient='records')  # Convertir el DataFrame a una lista de diccionarios

def completar_matriz_con_datos_historicos(identificador, matriz_datos, primer_muestreo): #Aux......
    try:
        data = historico_individual_por_instrumento(identificador, primer_muestreo)
        for d in data:
            x = d["x"]   # timestamp
            y = d["y"]   # valor real
            if identificador not in matriz_datos["Identificador"].values:
                matriz_datos.loc[len(matriz_datos), "Identificador"] = identificador
                matriz_datos.loc[matriz_datos["Identificador"] == identificador,x] = y

            matriz_datos.loc[(matriz_datos["Identificador"]  ) == identificador, x] = y
        return matriz_datos
    except Exception as e:
        #Si no existe una fila con Y, tirara error
        print("No hay dato historico 'Y'")
        return matriz_datos
def redondeo_arriba_abs(x):#Aux........
    return math.ceil(x * 100) / 100
def calcular_z_score(valor, media, desviacion_estandar): #Aux........
    if desviacion_estandar == 0:
        return 0  # Evitar división por cero, si la desviación estándar es cero, el z-score es 0
    z_score = redondeo_arriba_abs((valor - media) / desviacion_estandar)
    if abs(z_score) >= 3:
        pass
        # activar alerta
    return z_score

def obtener_csv():
    data = leer_csv_info_general_instrumentos()
    primer_muestreo = tiempo_actual()
    df = pd.DataFrame(data)

    ###########Este ejemplo esta enfocado en desarrollar una matriz basica de los instrumentos del Chancador primario ##########################
    df_datos_instrumentos = pd.DataFrame(columns=["Identificador"])
    df_medidas_estadisticas = pd.DataFrame(
        columns=[
            "Identificador", "Media", 
            "Desviacion_Estandar", 
            "Minimo", "Maximo", 
            "Gradiente"
            ])
    #Trabajo n°1 filtrar por los instrumentos del chancado primario
    df_filtrado = df[df["Subárea"] == "3200 - 1 - CHANCADO PRIMARIO"]
    #print(df_filtrado) filtro exitoso

    #Trabajo n°2 añadir identificadores a cada df del chancado primario
    df_datos_instrumentos["Identificador"] = df_filtrado["Identificador"]
    df_medidas_estadisticas["Identificador"] = df_filtrado["Identificador"]
    #print(df_datos_instrumentos, df_medidas_estadisticas)  #Se copian correctamente los identificadores a cada df

    #Trabajo n°3 añadir datos al df de instrumentos
    df_datos_instrumentos = completar_matriz_con_datos_historicos(6192,df_datos_instrumentos,primer_muestreo)
    df_datos_instrumentos = completar_matriz_con_datos_historicos(6240,df_datos_instrumentos,primer_muestreo)
    for identificador in df_datos_instrumentos["Identificador"]:
        #df_historico_instrumento = completar_matriz_con_datos_historicos(identificador,df_datos_instrumentos,primer_muestreo)
        pass
    #print(df_historico_instrumento) #Se añaden correctamente los datos historicos a cada instrumento, aunque los que no tienen 'Y' quedan como NaN
    df_medidas_estadisticas = df_medidas_estadisticas.merge(
        df_datos_instrumentos[["Identificador"]],
        on="Identificador",
        how="right"
    )

    #Trabajo n°4 añadir datos al df de medidas estadisticas
    df_datos_instrumentos = df_datos_instrumentos.fillna(0)  # Rellenar los valores NaN con 0 para evitar errores en los cálculos
    df_medidas_estadisticas=df_medidas_estadisticas.fillna(0)  # Rellenar los valores NaN con 0 para evitar errores en los cálculos
    
    #Trabajo n°5 calcular desviación estandar para cada instrumento
    for identificador in df_medidas_estadisticas["Identificador"]:
        fila = df_datos_instrumentos[df_datos_instrumentos["Identificador"] == identificador] #fila de los datos con el identificador
        df_medidas_estadisticas.loc[df_medidas_estadisticas["Identificador"] == identificador, "Media"] = fila.iloc[:, 1:].mean(axis=1).item()
        df_medidas_estadisticas.loc[df_medidas_estadisticas["Identificador"] == identificador, "Desviacion_Estandar"] = fila.iloc[:, 1:].std(axis=1).values[0]


        #print(df_medidas_estadisticas["Desviacion_Estandar"])
    for identificador in df_datos_instrumentos["Identificador"]:
        desviacion_estandar = df_medidas_estadisticas.loc[df_medidas_estadisticas["Identificador"]== identificador, "Desviacion_Estandar"].values[0]
        if abs(desviacion_estandar) < 1e-10:
            desviacion_estandar = 0
        print("Desviacion estandar ",desviacion_estandar)
        media = round(df_medidas_estadisticas.loc[df_medidas_estadisticas["Identificador"]==identificador, "Media"].values[0],4)
        print("Media ",media)
        fila_medidas = df_medidas_estadisticas.loc[df_medidas_estadisticas["Identificador"]==identificador]
        ultimo_valor = df_datos_instrumentos.loc[df_datos_instrumentos["Identificador"]==identificador].iloc[:, -1].values[0]
        print("Último valor ",ultimo_valor)
        z_score = calcular_z_score(ultimo_valor, media, desviacion_estandar)
        print("Z-score ",z_score)
    print(df_datos_instrumentos)
    print(df_medidas_estadisticas)

    return df.to_dict(orient='records')  # Convertir el DataFrame a una lista de diccionarios que fastAPI transforma a JSON automáticamente