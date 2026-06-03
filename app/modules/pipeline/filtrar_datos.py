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

    # Obtener fila de control correa CR-02
    fila_8955 = df_historico[
        df_historico["Identificador"] == 8955
    ].iloc[0]
    print(f"Valores de control para CR-02:\n{fila_8955.head()}")

    # Obtener fila de control tonelaje / peso
    fila_9599 = df_historico[
        df_historico["Identificador"] == 9599
    ].iloc[0]
    print(f"Valores de control para tonelaje:\n{fila_9599.head()}")
    # Quitar columna Identificador
    control_8955 = fila_8955.drop(labels=["Identificador"])
    control_9599 = fila_9599.drop(labels=["Identificador"])

    # Recorrer timestamps
    for timestamp in control_8955.index:

        valor_8955 = control_8955[timestamp]
        valor_9599 = control_9599[timestamp]

        # Chancado secundario detenido:
        # CR-02 distinto de 1 o tonelaje menor/igual a 500
        if valor_8955 != 1 or valor_9599 <= 500:

            # No modificar las filas de control
            mascara = ~df_historico["Identificador"].isin([8955, 9599])
            # Poner NaN
            df_historico.loc[mascara, timestamp] = np.nan
    return df_historico

def filtrar_chancado_terciario(df_historico):
    print("Soy el chancado terciario")

    fila_22258 = df_historico[
        df_historico["Identificador"] == 22258
    ].iloc[0]

    fila_9016 = df_historico[
        df_historico["Identificador"] == 9016
    ].iloc[0]

    fila_6265 = df_historico[
        df_historico["Identificador"] == 6265
    ].iloc[0]

    control_22258 = fila_22258.drop(labels=["Identificador"])
    control_9016 = fila_9016.drop(labels=["Identificador"])
    control_6265 = fila_6265.drop(labels=["Identificador"])

    for timestamp in control_22258.index:

        valor_22258 = control_22258[timestamp]
        valor_9016 = control_9016[timestamp]
        valor_6265 = control_6265[timestamp]

        if valor_22258 != 1 or valor_9016 != 1 or valor_6265 <= 1000:

            mascara = ~df_historico["Identificador"].isin(
                [22258, 9016, 6265]
            )

            df_historico.loc[mascara, timestamp] = np.nan

    return df_historico

def filtrar_chancado_cuaternario(df_historico):
    print("Soy el chancado cuaternario")

    fila_22180 = df_historico[#Rodillo fijo
        df_historico["Identificador"] == 22180
    ].iloc[0]

    fila_9017 = df_historico[#Feeder 16
        df_historico["Identificador"] == 9017
    ].iloc[0]

    fila_9081 = df_historico[#Tonelaje
        df_historico["Identificador"] == 9081
    ].iloc[0]

    control_22180 = fila_22180.drop(labels=["Identificador"])
    control_9017 = fila_9017.drop(labels=["Identificador"])
    control_9081 = fila_9081.drop(labels=["Identificador"])

    for timestamp in control_22180.index:

        valor_22180 = control_22180[timestamp]
        valor_9017 = control_9017[timestamp]
        valor_9081 = control_9081[timestamp]

        if valor_22180 != 1 or valor_9017 != 1 or valor_9081 <= 1000:
            mascara = ~df_historico["Identificador"].isin(
                [22180, 9017, 9081]
            )

            df_historico.loc[mascara, timestamp] = np.nan
            print(
                df_historico[
                    ["Identificador", timestamp]
                ]
            )
    return df_historico

def filtrar_acopio_fino(df_historico):
    print("Soy acopio fino")

    # Pendiente lógica operacional

    return df_historico

ACCIONES_SUBAREA = {
    "Chancado Primario": filtrar_chancado_primario,
    "Chancado Secundario": filtrar_chancado_secundario,
    "Chancado Terciario": filtrar_chancado_terciario,
    "Chancado Cuaternario": filtrar_chancado_cuaternario,
    "Acopio Fino": filtrar_acopio_fino
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