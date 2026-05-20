from .data_loader import (
    datos_historicos_por_instrumento,
    tiempo_actual,
    datos_matriz_a, 
    quality_code_metris_api,
    subarea_chancado_primario,
    subarea_chancado_secundario,
    subarea_chancado_terciario,
    subarea_chancado_cuaternario,
    subarea_molienda_cuaternaria,
    subarea_acopio_fino
)
from .filtrar_datos import filtrar_datos_historicos
import pandas as pd
import matplotlib.pyplot as plt
import asyncio
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import httpx
from app.core.logger import crear_logger

logger = crear_logger("Pipeline")

async def obtener_historico(identificador, fecha_inicio, fecha_fin, periodo_muestreo):#Aux para obtener los datos historicos de cualquier instrumento
    try:
        data = await datos_historicos_por_instrumento(
            identificador,
            fecha_inicio,
            fecha_fin,
            periodo_muestreo,
        )
        if identificador == 8954:
            print(f"Datos históricos para el identificador {identificador}:\n", data[:10])
        return {
            
            "identificador": identificador,
            "data": data
        }
    except Exception as e:
        if identificador == 8954:
            print(f"Error al obtener datos históricos para el identificador {identificador}")
        #Si no existe una fila con Y, tirara error
        logger.error(f"No hay dato historico 'Y' para: ,{identificador}")

def eliminar_booleanos(df):

    filas_a_mantener = []

    for _, fila in df.iterrows():

        identificador = fila["Identificador"]
        # Sacar valores históricos
        # Excluir columna identificador explícitamente
        valores = fila.drop(labels=["Identificador"])

        # Convertir a numérico
        valores = pd.to_numeric(valores, errors="coerce")

        # Eliminar NaN
        valores = valores.dropna()

        # Redondear floats
        valores = valores.round(1)
        # Valores únicos
        valores_unicos = set(valores.unique())
        #print(f"Valores únicos para el identificador {identificador}: {list(valores_unicos)[:5]}")
        # Detectar booleanos
        es_booleano = valores_unicos.issubset({0.0, 1.0,-1.0})
        #print(f"Procesando: {identificador}, BOOLEANO: {es_booleano}")

        if not es_booleano:
            filas_a_mantener.append(fila)

    return pd.DataFrame(filas_a_mantener)

async def generar_dataframe_datos_historicos(df_matriz,fecha_inicio,fecha_fin, periodo_muestreo):#Aux historicos para cualquier matriz
    #=================== Lista de identificadores==========================
    identificadores = df_matriz["Identificador"].tolist()
    # =========================
    # Obtención concurrente
    # =========================
    semaphore = asyncio.Semaphore(50)
    async def obtener_historico_limitado(identificador):

        async with semaphore:

            return await obtener_historico(
                identificador,
                fecha_inicio,
                fecha_fin,
                periodo_muestreo
            )
    tasks = [#Esto crea ordenes de hacer algo, pero no lo hace aún
        obtener_historico_limitado(id)
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
                    "valor": float(punto.get("y")) if punto.get("y") is not None else None
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
        .reset_index()
    )
    df_matriz_b_datos.columns.name = None
    df_matriz_b_datos = eliminar_booleanos(df_matriz_b_datos)
    df_matriz_b_datos["Identificador"] = (
        df_matriz_b_datos["Identificador"]
        .astype("Int64")
    )
    return df_matriz_b_datos

async def construccion_matriz_b():#Se construye la matriz B con datos historicos
    fecha_fin = tiempo_actual()
    fecha_inicio = fecha_fin - relativedelta(months=4)
    periodo_muestreo_matriz_b = 600000000 #Muestreo de interpolación, cantidad de muestra por minuto (600000000 es un minuto)
    df_matriz_a = subarea_chancado_primario() #Entrega un DF
    df_matriz_a_datos = await generar_dataframe_datos_historicos(df_matriz_a, fecha_inicio, fecha_fin, periodo_muestreo_matriz_b)
    subarea = df_matriz_a["Subarea"].iloc[0]
    df_matriz_b_datos = filtrar_datos_historicos(df_matriz_a_datos,subarea)

    logger.info("Envio la matriz B Construida con datos historicos")
    return df_matriz_b_datos