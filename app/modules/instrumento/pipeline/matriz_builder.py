from .data_loader import datos_historicos_por_instrumento, tiempo_actual, datos_matriz_a, quality_code_metris_api
import pandas as pd
import asyncio

def quality_code(id):
    data = quality_code_metris_api()
    #Limpiar data para solo recibir el quality code
    quality_code_number = 1
    return quality_code_number

def filtrar_matriz_a():#Filtros que se aplican a la matriz [A] y genera la matriz [B]
    df_matriz_a = datos_matriz_a() #Entrega un objeto de python =records
    print("Filtramos la matriz A -----> Generando la matriz B")
    #Hacemos el llamado a la funcion de qualitycode y filtramos por los que tengan mejor calidad
    return df_matriz_a

async def completar_matriz_b_con_datos_historicos(identificador, matriz_datos, primer_muestreo): #Aux obsoleta (solo ejemplo)
    try:
        data = await datos_historicos_por_instrumento(identificador, primer_muestreo)
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

async def obtener_historico(identificador, primer_muestreo):#Aux para obtener los datos
    try:
        data = await datos_historicos_por_instrumento(
            identificador,
            primer_muestreo
        )

        return {
            "identificador": identificador,
            "data": data
        }
    except Exception as e:
        #Si no existe una fila con Y, tirara error
        print("No hay dato historico 'Y'")

async def construccion_matriz_b():#Se construye la matriz B con datos historicos
    primer_muestreo = tiempo_actual()
    df_matriz_b = filtrar_matriz_a() #Entrega un DF
    
    df_datos_instrumentos = pd.DataFrame({"Identificador": pd.Series(dtype="Int64")})
    
    #Trabajo n°1 filtrar por los instrumentos del chancado primario
    df_filtrado = df_matriz_b[df_matriz_b["Sub"] == "Chancado Primario"]
    #print(df_filtrado) #filtro exitoso

    #Trabajo n°2 añadir identificadores a cada df del chancado primario
    df_datos_instrumentos["Identificador"] = df_filtrado["Identificador"]

    #Trabajo n°3 añadir datos al df de instrumentos y hay datos de prueba 6192 y 6240.
    #Se añaden datos de ejemplo y aparecen NaN los que estan vacios
    df_datos_instrumentos = await completar_matriz_b_con_datos_historicos(6192,df_datos_instrumentos,primer_muestreo)
    df_datos_instrumentos = await completar_matriz_b_con_datos_historicos(6240,df_datos_instrumentos,primer_muestreo)
    
    #Se añaden correctamente los datos historicos a cada instrumento, aunque los que no tienen 'Y' quedan como NaN
    tasks = [#Esto crea ordenes de hacer algo, pero no lo hace aún
        obtener_historico(id, primer_muestreo)
        for id in df_datos_instrumentos["Identificador"]
    ]
    resultados = await asyncio.gather(*tasks)#Esto es el trabajo todo junto y concurrente
    for resultado in resultados:

        identificador = resultado["identificador"]
        data = resultado["data"]

        for d in data:

            x = d.get("x")
            y = d.get("y", None)

            df_datos_instrumentos.loc[df_datos_instrumentos["Identificador"] == identificador,x] = y
    
    #Trabajo n°4 añadir datos "vacios" o "0" a df de medidas estadisticas y de datos instrumentos que tienen NaN
    df_datos_instrumentos = df_datos_instrumentos.fillna(0)   
    print("Envio la matriz B Construida con datos historicos")
    return df_datos_instrumentos