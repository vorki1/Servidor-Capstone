from app.core.logger import crear_logger
import pandas as pd
import numpy as np

logger = crear_logger("Pipeline")

def limpiar_columna(columna):
    print("Limpiamos los datos de la columna")
    return columna

def filtrar_chancado_primario(df_historico):

    print("Soy el chancado primario")

    # Eliminar instrumento no deseado
    df_historico = df_historico[
        df_historico["Identificador"] != 89932
    ]

    # Obtener fila de control chancador primario
    fila_8954 = df_historico[
        df_historico["Identificador"] == 8954
    ].iloc[0]

    # Obtener fila de control correa-01
    fila_8975 = df_historico[
        df_historico["Identificador"] == 8975
    ].iloc[0]
    #Obtener fila de control del tonelaje de la correa 1
    fila_9092 = df_historico[
        df_historico["Identificador"] == 9092
    ].iloc[0]

    # Quitar columna Identificador
    control_8954 = fila_8954.drop(labels=["Identificador"])
    control_8975 = fila_8975.drop(labels=["Identificador"])
    control_9092 = fila_9092.drop(labels=["Identificador"])

    # Recorrer timestamps
    for timestamp in control_8954.index:

        valor_8954 = control_8954[timestamp]
        valor_8975 = control_8975[timestamp]
        valor_9092 = control_9092[timestamp]
        # Si cualquiera está detenido
        if valor_8954 <= 0.5 or valor_8975 <= 0.5 or valor_9092 <= 700:
            #print(f"En timestamp {timestamp} alguno de los controles está detenido. Marcando como NaN.{valor_8954}, {valor_8975}, {valor_9092}")
            # No modificar las filas de control
            mascara = ~df_historico["Identificador"].isin([8954, 8975, 9092])
            # Poner NaN
            df_historico.loc[mascara, timestamp] = np.nan
    return df_historico

def filtrar_chancado_secundario(df_historico):
    print("Soy el chancado secundario")
    return df_historico

ACCIONES_SUBAREA = {
    "Chancado Primario": filtrar_chancado_primario,
    "Chancado Secundario": filtrar_chancado_secundario,
}
def filtrar_datos_historicos(df_datos_historicos, subarea):
    funcion = ACCIONES_SUBAREA.get(subarea)
    if funcion:
        resultado = funcion(df_datos_historicos)
        #print("Resultado del filtrado:\n", resultado)
        return resultado
    else:
        logger.warning(f"No existe accion para subarea: {subarea}")
    logger.info("Filtramos la matriz A -----> Generando la matriz B")
    return df_datos_historicos