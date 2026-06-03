from .data_loader import datos_historicos_por_instrumento,ultimo_valor_interpolado_por_instrumento
import pandas as pd
from datetime import datetime, timezone
import asyncio
from app.core.logger import crear_logger
logger = crear_logger("Pipeline")

async def obtener_historico(identificador, fecha_inicio, fecha_fin, minutos_muestreo,segundos_muestreo):#Aux para obtener los datos historicos de cualquier instrumento
    try:
        data = await datos_historicos_por_instrumento(
            identificador,
            fecha_inicio,
            fecha_fin,
            minutos_muestreo,
            segundos_muestreo
        )
        #print(f"Datos históricos para el identificador {identificador}:\n", data[:3])
        if identificador == 8954:
            #print(f"Datos históricos para el identificador {identificador}:\n", data[:10])
            #print(json.dumps(data[:3], indent=2))
            pass
        if identificador == 8955:
            #print(f"Datos históricos para el identificador {identificador}:\n", data[:10])
            #print(json.dumps(data[:3], indent=2))
            pass
            
        return {
            
            "identificador": identificador,
            "data": data
        }
    except Exception as e:
        if identificador == 8954:
            print(f"Error al obtener datos históricos para el identificador {identificador}")
        #Si no existe una fila con Y, tirara error
        logger.error(f"No hay dato historico 'Y' para: ,{identificador}: {e}")
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
        #-------------Chancado primario-Chancado secundario:8955-Chancado Terciario:8956,9016-Chancado cuaternario 22180,9017
        #-------------Acopio fino:8986,9145
        no_eliminar = [8954,8975,9092,8955,22258,9016,22180,9017,8986,9145]
        if not es_booleano or identificador in no_eliminar:
            filas_a_mantener.append(fila)
    return pd.DataFrame(filas_a_mantener)
async def generar_dataframe_datos_historicos(df_matriz,fecha_inicio,fecha_fin, minutos_muestreo,segundos_muestreo):#Aux historicos para cualquier matriz
    #=================== Lista de identificadores==========================
    identificadores = df_matriz["Identificador"].tolist()
    # =========================
    # Obtención concurrente
    # =========================
    semaphore = asyncio.Semaphore(10)
    async def obtener_historico_limitado(identificador):

        async with semaphore:

            return await obtener_historico(
                identificador,
                fecha_inicio,
                fecha_fin,
                minutos_muestreo,
                segundos_muestreo
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
    df_matriz_datos = df_historicos.pivot_table(
        index="Identificador",
        columns="timestamp",
        values="valor",
        aggfunc="last"
    )
    df_matriz_datos = (
        df_matriz_datos
        .reset_index()
    )
    df_matriz_datos.columns.name = None
    
    df_matriz_datos = eliminar_booleanos(df_matriz_datos)
    df_matriz_datos["Identificador"] = (
        df_matriz_datos["Identificador"]
        .astype("Int64")
    )


    return df_matriz_datos

#Solo para actualizar la ultima fila del dataframe de la matriz C
async def generar_dataframe_ultima_columna(df_identificadores,fecha_inicio,fecha_fin,minutos_muestreo,segundos_muestreo):
    identificadores = df_identificadores.tolist()
    timestamp_global = (datetime.now().replace(microsecond=0).astimezone().isoformat())
    tasks = [
        ultimo_valor_interpolado_por_instrumento(id,fecha_inicio,fecha_fin,minutos_muestreo,segundos_muestreo)
        for id in identificadores]
    resultados = await asyncio.gather(*tasks,return_exceptions=True)
    registros = []
    for id, resultado in zip(identificadores, resultados):
        if isinstance(resultado, Exception):
            print(f"Error en instrumento {id}: {resultado}")
            continue
        if resultado is None:
            print(f"Sin datos para instrumento {id}")
            continue
        valor = resultado["y"]
        registros.append({"Identificador": id,timestamp_global: valor})
    df_ultima_columna = pd.DataFrame(registros)
    return df_ultima_columna
