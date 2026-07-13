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

GRUPOS_AREA = {
    "SERVICIOS_GENERALES": ["3100"],
    "AREA_SECA": ["3200"],
    "AREA_HUMEDA": ["3300", "3400", "3500", "3600", "3610"],
    "RELAVES": ["3700", "3800"],
    "CONCENTRADUCTO": ["4100"],
}


def obtener_grupo_area(area):
    area = str(area).strip()

    for grupo, areas in GRUPOS_AREA.items():
        if area in areas:
            return grupo

    return "SIN_GRUPO"




CONTROL_L1_TONELAJE = 9597
CONTROL_L1_RUNSIG = 9329

CONTROL_L2_TONELAJE = 9598
CONTROL_L2_RUNSIG = 9330


def agregar_descripcion_area_humeda(df_historico):
    df_info = datos_matriz_a()

    df_info = df_info[
        ["Identificador", "Descripcion"]
    ].copy()

    df_info["Descripcion"] = (
        df_info["Descripcion"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    return df_historico.merge(
        df_info,
        on="Identificador",
        how="left"
    )

CONTROLES_AREA_HUMEDA = {
    "l1_tonelaje": CONTROL_L1_TONELAJE,
    "l1_runsig": CONTROL_L1_RUNSIG,
    "l2_tonelaje": CONTROL_L2_TONELAJE,
    "l2_runsig": CONTROL_L2_RUNSIG,
}


def construir_controles_area_humeda(df_historico):
    controles = {}

    columnas_excluir = [
        "Identificador",
        "Descripcion"
    ]

    for nombre, identificador in CONTROLES_AREA_HUMEDA.items():
        fila = df_historico[
            df_historico["Identificador"] == identificador
        ]

        if fila.empty:
            logger.warning(f"No existe control area humeda {identificador}")
            return None

        serie = fila.iloc[0].drop(
            labels=columnas_excluir,
            errors="ignore"
        )

        controles[nombre] = pd.to_numeric(
            serie,
            errors="coerce"
        )

    return controles
def filtrar_area_humeda(df_historico, subarea, area):
    logger.info(
        f"Area humeda | dataframe completo recibido | "
        f"instrumentos: {len(df_historico)}"
    )

    df_historico = agregar_descripcion_area_humeda(df_historico)

    controles = construir_controles_area_humeda(df_historico)

    if controles is None:
        logger.warning(
            "Area humeda | no se pudieron construir controles"
        )

        return df_historico.drop(
            columns=["Descripcion"],
            errors="ignore"
        )

    linea_1_operando = (
        (controles["l1_tonelaje"] > 300)
        & (controles["l1_runsig"] == 1)
    )

    linea_2_operando = (
        (controles["l2_tonelaje"] > 300)
        & (controles["l2_runsig"] == 1)
    )

    columnas_tiempo = [
        col for col in df_historico.columns
        if col not in ["Identificador", "Descripcion"]
    ]

    valores = df_historico[columnas_tiempo].to_numpy(
        dtype=float,
        copy=True
    )

    descripcion = (
        df_historico["Descripcion"]
        .fillna("")
        .astype(str)
        .str.upper()
    )

    filas_l1 = descripcion.str.contains("L1", na=False).to_numpy()
    filas_l2 = descripcion.str.contains("L2", na=False).to_numpy()
    
    columnas_l1_detencion = (~linea_1_operando).to_numpy()
    columnas_l2_detencion = (~linea_2_operando).to_numpy()

    if filas_l1.any() and columnas_l1_detencion.any():
        valores[
            np.ix_(filas_l1, columnas_l1_detencion)
        ] = np.nan

    if filas_l2.any() and columnas_l2_detencion.any():
        valores[
            np.ix_(filas_l2, columnas_l2_detencion)
        ] = np.nan

    df_valores_filtrados = pd.DataFrame(
        valores,
        columns=columnas_tiempo,
        index=df_historico.index
    )

    df_historico.loc[:, columnas_tiempo] = df_valores_filtrados

    return df_historico.drop(
        columns=["Descripcion"],
        errors="ignore"
    )

# =========================
# CONTROLES RELAVES
# =========================

CONTROL_RELAVES_L1_RUNSIG = 9543
CONTROL_RELAVES_L1_TORQUE = 75535
CONTROL_RELAVES_L1_PU_04 = 9513
CONTROL_RELAVES_L1_PU_07 = 9519

CONTROL_RELAVES_L2_RUNSIG = 9544
CONTROL_RELAVES_L2_TORQUE = 75531
CONTROL_RELAVES_L2_PU_05 = 9515
CONTROL_RELAVES_L2_PU_08 = 9522

CONTROL_GEHO_01_RUNSIG = 9559
CONTROL_GEHO_02_RUNSIG = 9560
CONTROL_GEHO_03_RUNSIG = 9561

CONTROL_GEHO_03_VALVULA_L1 = 9283
CONTROL_GEHO_03_VALVULA_L2 = 9282
def agregar_info_relaves(df_historico):
    df_info = datos_matriz_a()

    df_info = df_info[
        ["Identificador", "Descripcion", "Sistema"]
    ].copy()

    df_info["Descripcion"] = (
        df_info["Descripcion"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    df_info["Sistema"] = (
        df_info["Sistema"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    return df_historico.merge(
        df_info,
        on="Identificador",
        how="left"
    )


def obtener_control_opcional(df_historico, identificador, nombre):
    fila = df_historico[
        df_historico["Identificador"] == identificador
    ]

    if fila.empty:
        logger.warning(
            f"Relaves | control no encontrado: {nombre} ({identificador})"
        )
        return None

    serie = fila.iloc[0].drop(
        labels=["Identificador", "Descripcion", "Sistema"],
        errors="ignore"
    )

    return pd.to_numeric(
        serie,
        errors="coerce"
    )


def control_activo(control):
    if control is None:
        return None

    return control == 1


def control_mayor(control, valor):
    if control is None:
        return None

    return control > valor


def serie_false_referencia(df_historico):
    columnas_tiempo = [
        col for col in df_historico.columns
        if col not in ["Identificador", "Descripcion", "Sistema"]
    ]

    return pd.Series(
        False,
        index=columnas_tiempo
    )


def filtrar_relaves(df_historico, subarea, area):
    logger.info(
        f"Relaves | dataframe completo recibido | "
        f"instrumentos: {len(df_historico)}"
    )

    df_historico = agregar_info_relaves(df_historico)
    
    columnas_tiempo = [
        col for col in df_historico.columns
        if col not in ["Identificador", "Descripcion", "Sistema"]
    ]

    valores = df_historico[columnas_tiempo].to_numpy(
        dtype=float,
        copy=True
    )

    descripcion = (
        df_historico["Descripcion"]
        .fillna("")
        .astype(str)
        .str.upper()
    )

    sistema = (
        df_historico["Sistema"]
        .fillna("")
        .astype(str)
        .str.upper()
    )

    false_ref = serie_false_referencia(df_historico)

    l1_runsig = obtener_control_opcional(
        df_historico,
        CONTROL_RELAVES_L1_RUNSIG,
        "L1 RunSig Espesador 1"
    )

    l1_torque = obtener_control_opcional(
        df_historico,
        CONTROL_RELAVES_L1_TORQUE,
        "L1 Torque Espesador 1"
    )

    l1_pu_04 = obtener_control_opcional(
        df_historico,
        CONTROL_RELAVES_L1_PU_04,
        "L1 PU_04"
    )

    l1_pu_07 = obtener_control_opcional(
        df_historico,
        CONTROL_RELAVES_L1_PU_07,
        "L1 PU_07"
    )

    l2_runsig = obtener_control_opcional(
        df_historico,
        CONTROL_RELAVES_L2_RUNSIG,
        "L2 RunSig Espesador 2"
    )

    l2_torque = obtener_control_opcional(
        df_historico,
        CONTROL_RELAVES_L2_TORQUE,
        "L2 Torque Espesador 2"
    )

    l2_pu_05 = obtener_control_opcional(
        df_historico,
        CONTROL_RELAVES_L2_PU_05,
        "L2 PU_05"
    )

    l2_pu_08 = obtener_control_opcional(
        df_historico,
        CONTROL_RELAVES_L2_PU_08,
        "L2 PU_08"
    )

    geho_01 = obtener_control_opcional(
        df_historico,
        CONTROL_GEHO_01_RUNSIG,
        "GEHO_01 RunSig"
    )

    geho_02 = obtener_control_opcional(
        df_historico,
        CONTROL_GEHO_02_RUNSIG,
        "GEHO_02 RunSig"
    )

    geho_03 = obtener_control_opcional(
        df_historico,
        CONTROL_GEHO_03_RUNSIG,
        "GEHO_03 RunSig"
    )

    geho_03_valvula_l1 = obtener_control_opcional(
        df_historico,
        CONTROL_GEHO_03_VALVULA_L1,
        "GEHO_03 Válvula L1"
    )

    geho_03_valvula_l2 = obtener_control_opcional(
        df_historico,
        CONTROL_GEHO_03_VALVULA_L2,
        "GEHO_03 Válvula L2"
    )

    l1_espesador_operando = (
        (control_activo(l1_runsig) if l1_runsig is not None else false_ref)
        & (control_mayor(l1_torque, 1) if l1_torque is not None else false_ref)
    )

    l2_espesador_operando = (
        (control_activo(l2_runsig) if l2_runsig is not None else false_ref)
        & (control_mayor(l2_torque, 1) if l2_torque is not None else false_ref)
    )

    pu_04_operando = (
        control_activo(l1_pu_04)
        if l1_pu_04 is not None
        else false_ref
    )

    pu_07_operando = (
        control_activo(l1_pu_07)
        if l1_pu_07 is not None
        else false_ref
    )

    pu_05_operando = (
        control_activo(l2_pu_05)
        if l2_pu_05 is not None
        else false_ref
    )

    pu_08_operando = (
        control_activo(l2_pu_08)
        if l2_pu_08 is not None
        else false_ref
    )

    l1_linea_operando = (
        l1_espesador_operando
        & (
            pu_04_operando
            | pu_07_operando
        )
    )

    l2_linea_operando = (
        l2_espesador_operando
        & (
            pu_05_operando
            | pu_08_operando
        )
    )

    geho_01_operando = (
        l1_espesador_operando
        & (
            control_activo(geho_01)
            if geho_01 is not None
            else false_ref
        )
    )

    geho_02_operando = (
        l2_espesador_operando
        & (
            control_activo(geho_02)
            if geho_02 is not None
            else false_ref
        )
    )

    geho_03_operando = (
        (
            l1_espesador_operando
            | l2_espesador_operando
        )
        & (
            control_activo(geho_03)
            if geho_03 is not None
            else false_ref
        )
    )

    geho_03_descarga_l1 = (
        geho_03_operando
        & (
            control_activo(geho_03_valvula_l1)
            if geho_03_valvula_l1 is not None
            else false_ref
        )
    )

    geho_03_descarga_l2 = (
        geho_03_operando
        & (
            control_activo(geho_03_valvula_l2)
            if geho_03_valvula_l2 is not None
            else false_ref
        )
    )

    filas_l1 = descripcion.str.contains("L1", na=False).to_numpy()
    filas_l2 = descripcion.str.contains("L2", na=False).to_numpy()

    filas_pu_04 = sistema.eq("PU_04").to_numpy()
    filas_pu_07 = sistema.eq("PU_07").to_numpy()
    filas_pu_05 = sistema.eq("PU_05").to_numpy()
    filas_pu_08 = sistema.eq("PU_08").to_numpy()

    filas_geho_01 = sistema.eq("GEHO_01").to_numpy()
    filas_geho_02 = sistema.eq("GEHO_02").to_numpy()
    filas_geho_03 = sistema.eq("GEHO_03").to_numpy()

    def aplicar_nan(filas, condicion_operando):
        columnas_detencion = (~condicion_operando).to_numpy()

        if filas.any() and columnas_detencion.any():
            valores[
                np.ix_(filas, columnas_detencion)
            ] = np.nan

    aplicar_nan(filas_l1, l1_linea_operando)
    aplicar_nan(filas_l2, l2_linea_operando)

    aplicar_nan(filas_pu_04, pu_04_operando)
    aplicar_nan(filas_pu_07, pu_07_operando)
    aplicar_nan(filas_pu_05, pu_05_operando)
    aplicar_nan(filas_pu_08, pu_08_operando)

    aplicar_nan(filas_geho_01, geho_01_operando)
    aplicar_nan(filas_geho_02, geho_02_operando)

    aplicar_nan(
        filas_geho_03 & filas_l1,
        geho_03_descarga_l1
    )

    aplicar_nan(
        filas_geho_03 & filas_l2,
        geho_03_descarga_l2
    )

    df_valores_filtrados = pd.DataFrame(
        valores,
        columns=columnas_tiempo,
        index=df_historico.index
    )

    df_historico.loc[:, columnas_tiempo] = df_valores_filtrados

    return df_historico.drop(
        columns=["Descripcion", "Sistema"],
        errors="ignore"
    )



CONTROL_CONCENTRADUCTO = 17657


def filtrar_concentraducto(df_historico, subarea, area):
    logger.info(
        f"Concentraducto | dataframe completo recibido | "
        f"instrumentos: {len(df_historico)}"
    )

    return aplicar_nan_por_detencion(
        df_historico=df_historico,
        controles=[CONTROL_CONCENTRADUCTO],
        condicion_detencion=lambda c: (
            c[CONTROL_CONCENTRADUCTO] != 1
        )
    )


ACCIONES_AREA_SECA = {
    "Chancado Primario": filtrar_chancado_primario,
    "Chancado Secundario": filtrar_chancado_secundario,
    "Chancado Terciario": filtrar_chancado_terciario,
    "Chancado Cuaternario": filtrar_chancado_cuaternario,
    "Acopio Fino": filtrar_acopio_fino,
}


ACCIONES_GRUPO_AREA = {
    "AREA_HUMEDA": filtrar_area_humeda,
    "RELAVES": filtrar_relaves,
    "CONCENTRADUCTO": filtrar_concentraducto,
}


def filtrar_datos_historicos(
    df_datos_historicos,
    subarea,
    area,
    grupo_area=None
):
    if grupo_area is None:
        grupo_area = obtener_grupo_area(area)

    if grupo_area == "AREA_SECA":
        funcion = ACCIONES_AREA_SECA.get(subarea)

        if funcion:
            return funcion(df_datos_historicos)

        logger.warning(
            f"Area seca | no existe accion para subarea: {subarea}"
        )

        return df_datos_historicos

    funcion_grupo = ACCIONES_GRUPO_AREA.get(grupo_area)

    if funcion_grupo:
        return funcion_grupo(
            df_datos_historicos,
            subarea,
            area
        )

    logger.warning(
        f"Area sin grupo definido: area {area}, subarea {subarea}"
    )

    return df_datos_historicos