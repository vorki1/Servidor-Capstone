from app.core.logger import crear_logger
import pandas as pd
import numpy as np
from .data_loader import datos_matriz_a

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
    return df_historico

def filtrar_acopio_fino(df_historico):
    print("Soy acopio fino")

    df_info = datos_matriz_a()

    df_info = df_info[
        df_info["Subarea"] == "Acopio Fino"
    ][["Identificador", "Sistema"]]

    df_historico = df_historico.merge(
        df_info,
        on="Identificador",
        how="left"
    )

    fila_8986 = df_historico[
        df_historico["Identificador"] == 8986
    ].iloc[0]  # CV-12

    fila_9242 = df_historico[
        df_historico["Identificador"] == 9242
    ].iloc[0]  # Tonelaje CV-12

    fila_5756 = df_historico[
        df_historico["Identificador"] == 5756
    ].iloc[0]  # CV-13

    fila_5754 = df_historico[
        df_historico["Identificador"] == 5754
    ].iloc[0]  # TR-01

    fila_9066 = df_historico[
        df_historico["Identificador"] == 9066
    ].iloc[0]  # SK-01

    fila_9144 = df_historico[
        df_historico["Identificador"] == 9144
    ].iloc[0]  # CV-14

    fila_9145 = df_historico[
        df_historico["Identificador"] == 9145
    ].iloc[0]  # CV-15

    fila_4569 = df_historico[
        df_historico["Identificador"] == 4569
    ].iloc[0]  # Tonelaje CV-15

    control_8986 = fila_8986.drop(labels=["Identificador", "Sistema"])
    control_9242 = fila_9242.drop(labels=["Identificador", "Sistema"])
    control_5756 = fila_5756.drop(labels=["Identificador", "Sistema"])
    control_5754 = fila_5754.drop(labels=["Identificador", "Sistema"])
    control_9066 = fila_9066.drop(labels=["Identificador", "Sistema"])
    control_9144 = fila_9144.drop(labels=["Identificador", "Sistema"])
    control_9145 = fila_9145.drop(labels=["Identificador", "Sistema"])
    control_4569 = fila_4569.drop(labels=["Identificador", "Sistema"])

    cv14_valor_anterior = 0
    cv14_iteraciones_arranque = 0
    cv14_iteraciones_parada = 0

    ventana_arranque_cv14 = 40
    ventana_parada_cv14 = 5
    for timestamp in control_8986.index:

        valor_8986 = control_8986[timestamp]
        valor_9242 = control_9242[timestamp]
        valor_5756 = control_5756[timestamp]
        valor_5754 = control_5754[timestamp]
        valor_9066 = control_9066[timestamp]
        valor_9144 = control_9144[timestamp]
        valor_9145 = control_9145[timestamp]
        valor_4569 = control_4569[timestamp]

        cv12_operando = (
            valor_8986 == 1
            and valor_9242 > 500
        )

        cv13_operando = (
            cv12_operando
            and valor_5756 == 1
        )

        tr01_operando = (
            cv12_operando
            and valor_5754 == 1
        )

        sk01_operando = (
            tr01_operando
            and valor_9066 == 1
        )

        cv14_operando = (
            valor_9144 == 1
        )

        cv15_operando = (
            valor_9145 == 1
            and valor_4569 > 950
            and (
                cv13_operando
                or cv14_operando
            )
        )
        if not cv12_operando:
            mascara = df_historico["Sistema"].isin(["CV_12"])
            df_historico.loc[mascara, timestamp] = np.nan
            

        if not cv13_operando:
            mascara = df_historico["Sistema"].isin(["CV_13"])
            df_historico.loc[mascara, timestamp] = np.nan

        if not tr01_operando:
            mascara = df_historico["Sistema"].isin(["TR_01"])
            df_historico.loc[mascara, timestamp] = np.nan

        if not sk01_operando:
            mascara = df_historico["Sistema"].isin(["SK_01"])
            df_historico.loc[mascara, timestamp] = np.nan


        # Detectar arranque
        if cv14_valor_anterior != 1 and valor_9144 == 1:
            cv14_iteraciones_arranque = ventana_arranque_cv14

        # Detectar parada
        if cv14_valor_anterior == 1 and valor_9144 != 1:
            cv14_iteraciones_parada = ventana_parada_cv14

        if not cv14_operando:
            mascara = df_historico["Sistema"].isin(["CV_14"])
            df_historico.loc[mascara, timestamp] = np.nan

        if cv14_iteraciones_arranque > 0:
            mascara = df_historico["Sistema"].isin(["CV_14"])
            df_historico.loc[mascara, timestamp] = np.nan
            cv14_iteraciones_arranque -= 1

        if cv14_iteraciones_parada > 0:
            mascara = df_historico["Sistema"].isin(["CV_14"])
            df_historico.loc[mascara, timestamp] = np.nan
            cv14_iteraciones_parada -= 1

        cv14_valor_anterior = valor_9144


        if not cv15_operando:
            mascara = df_historico["Sistema"].isin(["CV_15"])
            df_historico.loc[mascara, timestamp] = np.nan

    df_historico = df_historico.drop(columns=["Sistema"])

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