from .data_loader import datos_historicos_por_instrumento, tiempo_actual, datos_matriz_a, quality_code_metris_api
import pandas as pd
import math

def quality_code(id):
    data = quality_code_metris_api()
    #Limpiar data para solo recibir el quality code
    quality_code_number = 1
    return quality_code_number

def filtrar_matriz_a():
    df_matriz_a = datos_matriz_a() #Entrega un objeto de python =records
    print("Filtramos la matriz A -----> Generando la matriz B")
    #Hacemos el llamado a la funcion de qualitycode y filtramos por los que tengan mejor calidad
    return df_matriz_a

def completar_matriz_b_con_datos_historicos(identificador, matriz_datos, primer_muestreo): #Aux rellenado de Matriz B con datos historicos
    try:
        data = datos_historicos_por_instrumento(identificador, primer_muestreo)
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

def construccion_matriz_b():#Se construye la matriz B con datos historicos
    primer_muestreo = tiempo_actual()
    df_matriz_b = filtrar_matriz_a() #Entrega un objeto de python =records
    
    ###########Este ejemplo esta enfocado en desarrollar una matriz basica de los instrumentos del Chancador primario ##########################
    df_datos_instrumentos = pd.DataFrame({"Identificador": pd.Series(dtype="Int64")})
    
    #Trabajo n°1 filtrar por los instrumentos del chancado primario
    df_filtrado = df_matriz_b[df_matriz_b["Sub"] == "Chancado Primario"]
    #print(df_filtrado) #filtro exitoso

    #Trabajo n°2 añadir identificadores a cada df del chancado primario
    df_datos_instrumentos["Identificador"] = df_filtrado["Identificador"]
    #print(df_datos_instrumentos,"\n", df_medidas_estadisticas)  #Se copian correctamente los identificadores a cada df

    #Trabajo n°3 añadir datos al df de instrumentos y hay datos de prueba 6192 y 6240.
    #Se añaden datos de ejemplo y aparecen NaN los que estan vacios
    df_datos_instrumentos = completar_matriz_b_con_datos_historicos(6192,df_datos_instrumentos,primer_muestreo)
    df_datos_instrumentos = completar_matriz_b_con_datos_historicos(6240,df_datos_instrumentos,primer_muestreo)
    
    #Se añaden correctamente los datos historicos a cada instrumento, aunque los que no tienen 'Y' quedan como NaN
    for identificador in df_datos_instrumentos["Identificador"]:
        identificador = int(identificador)
        df_datos_instrumentos = completar_matriz_b_con_datos_historicos(identificador,df_datos_instrumentos,primer_muestreo)
        pass

    #Trabajo n°4 añadir datos "vacios" o "0" a df de medidas estadisticas y de datos instrumentos que tienen NaN
    df_datos_instrumentos = df_datos_instrumentos.fillna(0)
        
    print("Envio la matriz B Construida con datos historicos")
    return df_datos_instrumentos