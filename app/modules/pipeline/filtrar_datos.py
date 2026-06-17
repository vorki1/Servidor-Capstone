from app.core.logger import crear_logger
import pandas as pd
import numpy as np
from .matriz_a import datos_matriz_a
import matplotlib.pyplot as plt

logger = crear_logger("Pipeline")

def graficar_instrumento_filtrado(df_historico, identificador, titulo):
    df_fila = df_historico[
        df_historico["Identificador"] == identificador
    ]

    if df_fila.empty:
        print(f"No existe el instrumento {identificador} para graficar")
        return

    fila = df_fila.iloc[0]

    serie = fila.drop(labels=["Identificador"])

    serie.index = pd.to_datetime(
        serie.index,
        errors="coerce"
    )

    serie = pd.to_numeric(
        serie,
        errors="coerce"
    )

    plt.figure(figsize=(15, 5))

    plt.plot(
        serie.index,
        serie.values
    )

    plt.title(titulo)
    plt.xlabel("Timestamp")
    plt.ylabel("Corriente")
    plt.grid(True)

    plt.show()

def obtener_serie_control(df_historico, identificador):
    fila = df_historico[
        df_historico["Identificador"] == identificador
    ]

    if fila.empty:
        logger.warning(f"No existe control {identificador}")
        return None

    return fila.iloc[0].drop(labels=["Identificador"])

def aplicar_nan_por_detencion(df_historico,controles,condicion_detencion):
    df_historico = df_historico.copy()

    series_control = {}

    for identificador in controles:
        serie = obtener_serie_control(df_historico, identificador)

        if serie is None:
            return df_historico

        series_control[identificador] = pd.to_numeric(
            serie,
            errors="coerce"
        )

    timestamps_detencion = condicion_detencion(series_control)

    columnas_a_nan = timestamps_detencion[
        timestamps_detencion
    ].index

    if len(columnas_a_nan) == 0:
        return df_historico

    mascara_instrumentos = ~df_historico["Identificador"].isin(
        controles
    )

    df_historico.loc[
        mascara_instrumentos,
        columnas_a_nan
    ] = np.nan

    return df_historico

def filtrar_chancado_primario(df_historico):
    df_historico = df_historico[
        df_historico["Identificador"] != 89932
    ]

    return aplicar_nan_por_detencion(
        df_historico=df_historico,
        controles=[8954, 8975, 9092],
        condicion_detencion=lambda c: (
            (c[8954] <= 0.5)
            | (c[8975] <= 0.5)
            | (c[9092] <= 700)
        )
    )

def filtrar_chancado_secundario(df_historico):
    return aplicar_nan_por_detencion(
        df_historico=df_historico,
        controles=[8955, 9599],
        condicion_detencion=lambda c: (
            (c[8955] != 1)
            | (c[9599] <= 500)
        )
    )

def filtrar_chancado_terciario(df_historico):
    return aplicar_nan_por_detencion(
        df_historico=df_historico,
        controles=[22258, 9016, 6265],
        condicion_detencion=lambda c: (
            (c[22258] != 1)
            | (c[9016] != 1)
            | (c[6265] <= 1000)
        )
    )


def filtrar_chancado_cuaternario(df_historico):
    return aplicar_nan_por_detencion(
        df_historico=df_historico,
        controles=[22180, 9017, 9081],
        condicion_detencion=lambda c: (
            (c[22180] != 1)
            | (c[9017] != 1)
            | (c[9081] <= 1000)
        )
    )

BH_09 = 5752

CONTROLES_ACOPIO_FINO = {
    "cv12_run": 8986,
    "cv12_tonelaje": 9242,
    "cv13_run": 5756,
    "tr01_run": 5754,
    "sk01_run": 9066,
    "cv14_run": 9144,
    "cv15_run": 9145,
    "cv15_tonelaje": 4569,
    "bh09_run": BH_09,
}

FEEDERS_ACOPIO_FINO = [
    {"sistema": "FE_17", "id_feeder": 9175},
    {"sistema": "FE_18", "id_feeder": 9176},
    {"sistema": "FE_19", "id_feeder": 9177},
    {"sistema": "FE_20", "id_feeder": 9178},
    {"sistema": "FE_21", "id_feeder": 9179},
    {"sistema": "FE_22", "id_feeder": 9180},
    {"sistema": "FE_23", "id_feeder": 9181},
    {"sistema": "FE_24", "id_feeder": 9182},
    {"sistema": "FE_25", "id_feeder": 9183},
    {"sistema": "FE_26", "id_feeder": 9184},
    {"sistema": "FE_27", "id_feeder": 9185},
    {"sistema": "FE_28", "id_feeder": 9186},
    {"sistema": "FE_29", "id_feeder": 9187},
    {"sistema": "FE_30", "id_feeder": 9188},
    {"sistema": "FE_31", "id_feeder": 9189},
    {"sistema": "FE_32", "id_feeder": 9190},
    {"sistema": "FE_33", "id_feeder": 9191},
    {"sistema": "FE_34", "id_feeder": 9192},
    {"sistema": "FE_35", "id_feeder": 9193},
    {"sistema": "FE_36", "id_feeder": 9194},
    {"sistema": "FE_37", "id_feeder": 9195},
    {"sistema": "FE_38", "id_feeder": 9196},
    {"sistema": "FE_39", "id_feeder": 9197},
    {"sistema": "FE_40", "id_feeder": 9198},
    {"sistema": "FE_41", "id_feeder": 9199},
    {"sistema": "FE_42", "id_feeder": 9200},
    {"sistema": "FE_43", "id_feeder": 9201},
]


def agregar_sistema_acopio_fino(df_historico):
    df_info = datos_matriz_a()

    df_info = df_info[
        df_info["Subarea"] == "Acopio Fino"
    ][["Identificador", "Sistema"]]

    return df_historico.merge(
        df_info,
        on="Identificador",
        how="left"
    )

def obtener_serie_control_acopio(df_historico, identificador):
    fila = df_historico[
        df_historico["Identificador"] == identificador
    ]

    if fila.empty:
        logger.warning(f"No existe control {identificador} en Acopio Fino")
        return None

    serie = fila.iloc[0].drop(
        labels=["Identificador", "Sistema"],
        errors="ignore"
    )

    return pd.to_numeric(
        serie,
        errors="coerce"
    )

def construir_controles_acopio(df_historico):
    controles = {}

    for nombre, identificador in CONTROLES_ACOPIO_FINO.items():
        serie = obtener_serie_control_acopio(
            df_historico,
            identificador
        )

        if serie is None:
            return None

        controles[nombre] = serie

    return controles

def construir_controles_feeders(df_historico):
    controles_feeders = {}

    for feeder in FEEDERS_ACOPIO_FINO:
        serie = obtener_serie_control_acopio(
            df_historico,
            feeder["id_feeder"]
        )

        if serie is None:
            continue

        controles_feeders[feeder["sistema"]] = serie

    return controles_feeders

def construir_mascaras_sistema(df_historico):
    sistemas = [
        "CV_12",
        "CV_13",
        "TR_01",
        "SK_01",
        "CV_14",
        "CV_15",
    ]

    sistemas += [
        feeder["sistema"]
        for feeder in FEEDERS_ACOPIO_FINO
    ]

    return {
        sistema: df_historico["Sistema"].eq(sistema)
        for sistema in sistemas
    }

def filtrar_acopio_fino(df_historico):
    df_historico = agregar_sistema_acopio_fino(df_historico)

    controles = construir_controles_acopio(df_historico)

    if controles is None:
        logger.warning("Acopio Fino | no se pudieron construir controles")

        return df_historico.drop(
            columns=["Sistema"],
            errors="ignore"
        )

    controles_feeders = construir_controles_feeders(df_historico)

    mascaras_sistema = construir_mascaras_sistema(df_historico)

    timestamps = controles["cv12_run"].index

    cv12_operando = (
        (controles["cv12_run"] == 1)
        & (controles["cv12_tonelaje"] > 500)
    )

    cv13_operando = (
        cv12_operando
        & (controles["cv13_run"] == 1)
    )

    tr01_operando = (
        cv12_operando
        & (controles["tr01_run"] == 1)
    )

    sk01_operando = (
        tr01_operando
        & (controles["sk01_run"] == 1)
    )

    cv14_operando_base = (
        controles["cv14_run"] == 1
    )

    cv15_operando = (
        (controles["cv15_run"] == 1)
        & (controles["cv15_tonelaje"] > 950)
        & (
            cv13_operando
            | cv14_operando_base
        )
    )

    bh09_operando = (
        controles["bh09_run"] == 1
    )

    base_feeders_operando = (
        cv14_operando_base
        & cv15_operando
        & bh09_operando
    )

    cv14_run = controles["cv14_run"]

    arranque_cv14 = (
        (cv14_run.shift(1).fillna(0) != 1)
        & (cv14_run == 1)
    )

    parada_cv14 = (
        (cv14_run.shift(1).fillna(0) == 1)
        & (cv14_run != 1)
    )

    ventana_arranque_cv14 = 40
    ventana_parada_cv14 = 5

    cv14_bloqueo_arranque = pd.Series(
        False,
        index=timestamps
    )

    cv14_bloqueo_parada = pd.Series(
        False,
        index=timestamps
    )

    posiciones_arranque = [
        i for i, valor in enumerate(arranque_cv14.to_numpy())
        if valor
    ]

    posiciones_parada = [
        i for i, valor in enumerate(parada_cv14.to_numpy())
        if valor
    ]

    for pos in posiciones_arranque:
        cv14_bloqueo_arranque.iloc[
            pos:pos + ventana_arranque_cv14
        ] = True

    for pos in posiciones_parada:
        cv14_bloqueo_parada.iloc[
            pos:pos + ventana_parada_cv14
        ] = True

    cv14_operando = (
        cv14_operando_base
        & ~cv14_bloqueo_arranque
        & ~cv14_bloqueo_parada
    )

    columnas_tiempo = [
        col for col in df_historico.columns
        if col not in ["Identificador", "Sistema"]
    ]

    valores = df_historico[columnas_tiempo].to_numpy(
        dtype=float,
        copy=True
    )

    sistemas_array = df_historico["Sistema"].to_numpy()

    def aplicar_nan_numpy(sistema, condicion_operando):
        filas = sistemas_array == sistema
        columnas = (~condicion_operando).to_numpy()

        if filas.any() and columnas.any():
            valores[np.ix_(filas, columnas)] = np.nan

    aplicar_nan_numpy("CV_12", cv12_operando)
    aplicar_nan_numpy("CV_13", cv13_operando)
    aplicar_nan_numpy("TR_01", tr01_operando)
    aplicar_nan_numpy("SK_01", sk01_operando)
    aplicar_nan_numpy("CV_14", cv14_operando)
    aplicar_nan_numpy("CV_15", cv15_operando)

    for sistema_feeder, control_feeder in controles_feeders.items():
        feeder_operando = (
            base_feeders_operando
            & (control_feeder == 1)
        )

        aplicar_nan_numpy(
            sistema_feeder,
            feeder_operando
        )

    df_valores_filtrados = pd.DataFrame(
        valores,
        columns=columnas_tiempo,
        index=df_historico.index
    )

    df_historico.loc[:, columnas_tiempo] = df_valores_filtrados

    df_historico = df_historico.drop(
        columns=["Sistema"],
        errors="ignore"
    )

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
