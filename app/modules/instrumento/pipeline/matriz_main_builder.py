from .data_loader import (datos_historicos_por_instrumento, tiempo_actual, datos_matriz_a, quality_code_metris_api)
import pandas as pd
import asyncio
from datetime import timedelta
from dateutil.relativedelta import relativedelta

def quality_code(id):
    data = quality_code_metris_api()
    #Limpiar data para solo recibir el quality code
    quality_code_number = 1
    return quality_code_number

def filtrar_matriz_a():#Filtros que se aplican a la matriz [A] y genera la matriz [B]
    df_matriz_a = datos_matriz_a() #Entrega un objeto de python =records
    print("Filtramos la matriz A -----> Generando la matriz B")
    #Trabajo n°1 filtrar por los instrumentos del chancado primario
    df_filtrado = df_matriz_a[df_matriz_a["Sub"] == "Chancado Primario"]
    #Hacemos el llamado a la funcion de qualitycode y filtramos por los que tengan mejor calidad
    return df_filtrado

async def obtener_historico(identificador, fecha_inicio, fecha_fin):#Aux para obtener los datos historicos de cualquier instrumento
    try:
        data = await datos_historicos_por_instrumento(
            identificador,
            fecha_inicio,
            fecha_fin
        )

        return {
            "identificador": identificador,
            "data": data
        }
    except Exception as e:
        #Si no existe una fila con Y, tirara error
        print("No hay dato historico 'Y' para, ",identificador)

async def generar_dataframe_datos_historicos(df_matriz,fecha_inicio,fecha_fin):#Aux historicos para cualquier matriz
    
    #=================== Lista de identificadores==========================
    identificadores = df_matriz["Identificador"].tolist()

    # =========================
    # Obtención concurrente
    # =========================
    
    tasks = [#Esto crea ordenes de hacer algo, pero no lo hace aún
        obtener_historico(id, fecha_inicio, fecha_fin)
        for id in identificadores
    ]
    resultados = await asyncio.gather(*tasks)#Esto es el trabajo todo junto y concurrente
    # =========================
    # Construcción registros
    # =========================
    registros = []
    for resultado in resultados:
        if resultado is None:
            continue
        else:
            identificador = resultado["identificador"]

            for punto in resultado["data"]:
                #df_datos_instrumentos.loc[df_datos_instrumentos["Identificador"] == identificador,x] = y
                registros.append({
                    "Identificador": identificador,
                    "timestamp": punto.get("x"),
                    "valor": punto.get("y", 0)
                })
    
    # =========================
    # DataFrame largo
    # =========================
    df_historicos  = pd.DataFrame(registros)
    # =========================
    # Matriz pivotada
    # =========================
    df_matriz_b_datos = df_historicos.pivot_table(
        index="Identificador",
        columns="timestamp",
        values="valor",
        aggfunc="last"
    )
    df_matriz_b_datos = (
        df_matriz_b_datos
        .fillna(0)
        .reset_index()
    )
    return df_matriz_b_datos

async def construccion_matriz_b():#Se construye la matriz B con datos historicos
    fecha_fin = tiempo_actual()
    fecha_inicio = fecha_fin - relativedelta(months=4)
    df_matriz_b = filtrar_matriz_a() #Entrega un DF
    df_matriz_b_datos = await generar_dataframe_datos_historicos(df_matriz_b,fecha_inicio,fecha_fin)
    print("Envio la matriz B Construida con datos historicos")
    return df_matriz_b_datos