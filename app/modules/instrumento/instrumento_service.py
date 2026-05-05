import pandas as pd
import math
from io import StringIO
from fastapi.responses import StreamingResponse
from .instrumento_repository_csv import leer_csv_info_general_instrumentos,matriz_a
from .instrumento_repository_metris import historico_instrumento_metris_api, historico_individual_por_instrumento, tiempo_actual, quality_code_metris_api
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

def filtrar_matriz_a():
    matriz_a_data = matriz_a() #Entrega un objeto de python =records
    df_matriz_a = pd.DataFrame(matriz_a_data)#Este es un datafram
    print("Filtramos la matriz A -----> Generando la matriz B \n" ,df_matriz_a)
    return df_matriz_a.to_dict(orient='records') 

def completar_matriz_b_con_datos_historicos(identificador, matriz_datos, primer_muestreo): #Aux......
    try:
        data = historico_individual_por_instrumento(identificador, primer_muestreo)
        if identificador not in matriz_datos["Identificador"].values:
            nueva_fila = pd.DataFrame({
                "Identificador": pd.Series([identificador], dtype="Int64")
            })
            matriz_datos = pd.concat([matriz_datos, nueva_fila], ignore_index=True)

        for d in data:
            x = d["x"]   # timestamp
            y = d["y"]   # valor real

            matriz_datos.loc[
                matriz_datos["Identificador"] == identificador, x
            ] = y
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

def procesamiento_matriz_b():
    primer_muestreo = tiempo_actual()
    matriz_b_data = filtrar_matriz_a() #Entrega un objeto de python =records
    df_matriz_b = pd.DataFrame(matriz_b_data)#Este es un dataframe
    print("Recibo la matriz B filtrada")
    ###########Este ejemplo esta enfocado en desarrollar una matriz basica de los instrumentos del Chancador primario ##########################
    df_datos_instrumentos = pd.DataFrame({"Identificador": pd.Series(dtype="Int64")})
    df_medidas_estadisticas = pd.DataFrame({
        "Identificador": pd.Series(dtype="Int64"),  # entero
        "Media": pd.Series(dtype="float"),
        "Desviacion_Estandar": pd.Series(dtype="float"),
        "Minimo": pd.Series(dtype="float"),
        "Maximo": pd.Series(dtype="float"),
        "Gradiente": pd.Series(dtype="float")
    })
    
    #Trabajo n°1 filtrar por los instrumentos del chancado primario
    df_filtrado = df_matriz_b[df_matriz_b["Sub"] == "Chancado Primario"]
    #print(df_filtrado) #filtro exitoso

    #Trabajo n°2 añadir identificadores a cada df del chancado primario
    df_datos_instrumentos["Identificador"] = df_filtrado["Identificador"]
    df_medidas_estadisticas["Identificador"] = df_filtrado["Identificador"]
    #print(df_datos_instrumentos,"\n", df_medidas_estadisticas)  #Se copian correctamente los identificadores a cada df

    #Trabajo n°3 añadir datos al df de instrumentos y hay datos de prueba 6192 y 6240.
    #Se añaden datos de ejemplo y aparecen NaN los que estan vacios
    df_datos_instrumentos = completar_matriz_b_con_datos_historicos(6192,df_datos_instrumentos,primer_muestreo)
    df_datos_instrumentos = completar_matriz_b_con_datos_historicos(6240,df_datos_instrumentos,primer_muestreo)
    
    nuevas_filas = pd.DataFrame([{
            "Identificador": 6192,
            "Media": 0.0,
            "Desviacion_Estandar": 0.0,
            "Minimo": 0.0,
            "Maximo": 0.0,
            "Gradiente": 0.0
        },
        {
            "Identificador": 6240,
            "Media": 0.0,
            "Desviacion_Estandar": 0.0,
            "Minimo": 0.0,
            "Maximo": 0.0,
            "Gradiente": 0.0
        }
    ])

    df_medidas_estadisticas = pd.concat(
        [df_medidas_estadisticas, nuevas_filas],
        ignore_index=True
    )
    
    #Se añaden correctamente los datos historicos a cada instrumento, aunque los que no tienen 'Y' quedan como NaN
    for identificador in df_datos_instrumentos["Identificador"]:
        identificador = int(identificador)
        df_datos_instrumentos = completar_matriz_b_con_datos_historicos(identificador,df_datos_instrumentos,primer_muestreo)
        pass

    #Trabajo n°4 añadir datos "vacios" o "0" a df de medidas estadisticas y de datos instrumentos que tienen NaN
    df_datos_instrumentos = df_datos_instrumentos.fillna(0)
    df_medidas_estadisticas=df_medidas_estadisticas.fillna(0)
    
    #Trabajo n°5 calcular medidas estadisticas para cada instrumento
    for identificador in df_medidas_estadisticas["Identificador"]: #Media y desviación estandar
        fila = df_datos_instrumentos[df_datos_instrumentos["Identificador"] == identificador] #fila de los datos con el identificador
        df_medidas_estadisticas.loc[df_medidas_estadisticas["Identificador"] == identificador, "Media"] = round(fila.iloc[:, 1:].mean(axis=1).iloc[0], 2)
        df_medidas_estadisticas.loc[df_medidas_estadisticas["Identificador"] == identificador, "Desviacion_Estandar"] = round(fila.iloc[:, 1:].std(axis=1).iloc[0], 2)
    
    for identificador in df_datos_instrumentos["Identificador"]: #Calculo del z_score para el ultimo valor de cada instrumento
        desviacion_estandar = df_medidas_estadisticas.loc[df_medidas_estadisticas["Identificador"]== identificador, "Desviacion_Estandar"].values[0]
        if abs(desviacion_estandar) < 1e-10:
            desviacion_estandar = 0
        media = round(df_medidas_estadisticas.loc[df_medidas_estadisticas["Identificador"]==identificador, "Media"].values[0],4)
        fila_medidas = df_medidas_estadisticas.loc[df_medidas_estadisticas["Identificador"]==identificador]
        ultimo_valor = df_datos_instrumentos.loc[df_datos_instrumentos["Identificador"]==identificador].iloc[:, -1].values[0]
        z_score = calcular_z_score(ultimo_valor, media, desviacion_estandar)

        

    return df_datos_instrumentos.to_dict(orient='records'), df_medidas_estadisticas.to_dict(orient='records')

def quality_code():
    
    return quality_code_metris_api()

def matriz_b():
    df_datos_instrumentos, df_medidas_estadisticas = metricas_matriz_b()
    data ={
        "datos_instrumentos": df_datos_instrumentos.to_dict(orient='records'),
        "medidas_estadisticas": df_medidas_estadisticas.to_dict(orient='records')
    }
    return data