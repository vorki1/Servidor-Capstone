from .data_loader import datos_historicos_por_instrumento,ultimo_valor_interpolado_por_instrumento,INSTRUMENTOS_CONTROL_OPERACIONAL,ids_booleanos
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

""" def eliminar_booleanos_antes(df):
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

        if not es_booleano or identificador in INSTRUMENTOS_CONTROL_OPERACIONAL:
            filas_a_mantener.append(fila)
    return pd.DataFrame(filas_a_mantener) """
def eliminar_booleanos(df):

    ids_a_eliminar = ids_booleanos()

    return df[
        ~df["Identificador"].isin(ids_a_eliminar)
    ]
def eliminar_booleanos_control(df):

    df = df[
        ~df["Identificador"].isin(INSTRUMENTOS_CONTROL_OPERACIONAL)
    ].copy()
    

    return df
async def generar_dataframe_datos_historicos(
    df_matriz,
    fecha_inicio,
    fecha_fin,
    minutos_muestreo,
    segundos_muestreo
):
    identificadores = df_matriz["Identificador"].tolist()

    logger.info(f"IDs solicitados al historian: {len(identificadores)}")

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

    tasks = [
        obtener_historico_limitado(id)
        for id in identificadores
    ]

    resultados = await asyncio.gather(*tasks)

    ids_con_respuesta = []
    ids_sin_respuesta = []
    ids_sin_data = []

    registros = []

    for resultado in resultados:
        if resultado is None:
            ids_sin_respuesta.append(None)
            continue

        identificador = resultado["identificador"]
        data = resultado["data"]

        if not data:
            ids_sin_data.append(identificador)
            continue

        ids_con_respuesta.append(identificador)

        for punto in data:
            registros.append({
                "Identificador": identificador,
                "timestamp": punto.get("x"),
                "valor": float(punto.get("y")) if punto.get("y") is not None else None
            })

    logger.info(f"IDs con data historian: {len(ids_con_respuesta)}")
    logger.info(f"IDs sin data historian: {len(ids_sin_data)}")

    if ids_sin_data:
        logger.info(f"IDs sin data: {ids_sin_data}")

    df_historicos = pd.DataFrame(registros)

    if df_historicos.empty:
        logger.warning("df_historicos viene vacío")
        return pd.DataFrame(columns=["Identificador"])

    df_matriz_datos = df_historicos.pivot_table(
        index="Identificador",
        columns="timestamp",
        values="valor",
        aggfunc="last"
    ).reset_index()

    df_matriz_datos.columns.name = None

    logger.info(f"IDs después del pivot: {len(df_matriz_datos)}")

    ids_antes_booleanos = set(
        df_matriz_datos["Identificador"].dropna().astype(int).tolist()
    )

    df_matriz_datos = eliminar_booleanos(df_matriz_datos)

    ids_despues_booleanos = set(
        df_matriz_datos["Identificador"].dropna().astype(int).tolist()
    )

    ids_eliminados_booleanos = sorted(
        ids_antes_booleanos - ids_despues_booleanos
    )

    logger.info(
        f"IDs después de eliminar_booleanos: {len(df_matriz_datos)}"
    )

    logger.info(
        f"IDs eliminados por eliminar_booleanos: {len(ids_eliminados_booleanos)}"
    )

    if ids_eliminados_booleanos:
        logger.info(f"IDs eliminados: {ids_eliminados_booleanos}")

    df_matriz_datos["Identificador"] = (
        df_matriz_datos["Identificador"].astype("Int64")
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
