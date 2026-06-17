from datetime import timedelta

import pandas as pd

from .data_loader import tiempo_actual
from .matriz_a import datos_matriz_a, INSTRUMENTOS_CONTROL_OPERACIONAL
from .filtros_iniciales import eliminar_instrumentos_control_operacional
from .historian_builder import (
    generar_dataframe_datos_historicos,
)
from .filtrar_datos import filtrar_datos_historicos
from .metricas import metricas_de_matrices
from .storage import (
    guardar_datos_matriz_c,
    leer_metricas_matriz_b,
    leer_datos_matriz_c
)
from app.core.logger import crear_logger


logger = crear_logger("Pipeline")


VENTANA_MINUTOS_MATRIZ_C = 30
PERIODO_MUESTREO_SEGUNDOS_MATRIZ_C = 10



def obtener_identificadores_matriz_c():
    df_metricas_b = leer_metricas_matriz_b()

    if df_metricas_b.empty:
        logger.warning("No se puede construir Matriz C: Matriz B vacía")
        return pd.DataFrame()

    df_identificadores_c = df_metricas_b[["Identificador"]]

    df_controles = pd.DataFrame({
        "Identificador": INSTRUMENTOS_CONTROL_OPERACIONAL
    })

    df_identificadores_c = (
        pd.concat(
            [df_identificadores_c, df_controles],
            ignore_index=True
        )
        .drop_duplicates(subset=["Identificador"])
    )

    df_matriz_a = datos_matriz_a()

    df_identificadores_c = df_identificadores_c.merge(
        df_matriz_a[["Identificador", "Subarea"]],
        on="Identificador",
        how="left"
    )

    return df_identificadores_c

async def matriz_c_builder():
    df_identificadores_c = obtener_identificadores_matriz_c()

    if df_identificadores_c.empty:
        return "No se construyó Matriz C porque no hay identificadores"

    fecha_fin = tiempo_actual()
    fecha_inicio = fecha_fin - timedelta(
        minutes=VENTANA_MINUTOS_MATRIZ_C
    )

    matrices_c = []

    for subarea, df_subarea in df_identificadores_c.groupby("Subarea"):
        if pd.isna(subarea):
            continue

        logger.info(f"Construyendo matriz C para subárea: {subarea}")

        df_matriz_c_subarea = await generar_dataframe_datos_historicos(
            df_matriz=df_subarea[["Identificador"]],
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            minutos_muestreo=0,
            segundos_muestreo=PERIODO_MUESTREO_SEGUNDOS_MATRIZ_C
        )

        if df_matriz_c_subarea.empty:
            continue

        df_matriz_c_subarea = filtrar_datos_historicos(
            df_matriz_c_subarea,
            subarea
        )

        if df_matriz_c_subarea.empty:
            continue

        columnas_tiempo = obtener_columnas_tiempo(df_matriz_c_subarea)

        if columnas_tiempo:
            df_matriz_c_subarea = df_matriz_c_subarea[
                ~df_matriz_c_subarea[columnas_tiempo]
                .isna()
                .all(axis=1)
            ]

        if not df_matriz_c_subarea.empty:
            matrices_c.append(df_matriz_c_subarea)

    if not matrices_c:
        logger.warning(
            "No se construyó matriz C: no hay instrumentos con datos"
        )
        return "No se construyó Matriz C: no hay instrumentos con datos"

    df_matriz_c_datos = pd.concat(
        matrices_c,
        ignore_index=True
    )

    df_matriz_c_datos = eliminar_instrumentos_control_operacional(
        df_matriz_c_datos
    )

    guardar_datos_matriz_c(df_matriz_c_datos)

    return "Historial de Matriz C construido y guardado en CSV"

def obtener_columnas_tiempo(df):
    return df.columns.drop("Identificador", errors="ignore").tolist()

def obtener_columnas_tiempo_ordenadas(df):
    columnas_tiempo = obtener_columnas_tiempo(df)

    if not columnas_tiempo:
        return []

    fechas = pd.to_datetime(
        columnas_tiempo,
        utc=True,
        errors="coerce"
    )

    df_columnas = pd.DataFrame({
        "columna": columnas_tiempo,
        "fecha": fechas
    })

    df_columnas = (
        df_columnas
        .dropna(subset=["fecha"])
        .sort_values("fecha")
    )

    return df_columnas["columna"].tolist()

def obtener_ultimo_timestamp_matriz_c(df_datos_matriz_c):
    columnas_tiempo = obtener_columnas_tiempo(df_datos_matriz_c)

    if not columnas_tiempo:
        return None

    fechas = pd.to_datetime(
        columnas_tiempo,
        utc=True,
        errors="coerce"
    )

    if fechas.isna().all():
        return None

    return fechas.max()

def mantener_ventana_matriz_c(df_datos_matriz_c, fecha_fin):
    columnas_tiempo = obtener_columnas_tiempo(df_datos_matriz_c)

    if not columnas_tiempo:
        return df_datos_matriz_c

    fecha_limite = fecha_fin - timedelta(
        minutes=VENTANA_MINUTOS_MATRIZ_C
    )

    fechas = pd.to_datetime(
        columnas_tiempo,
        utc=True,
        errors="coerce"
    )

    df_columnas = pd.DataFrame({
        "columna": columnas_tiempo,
        "fecha": fechas
    })

    df_columnas = (
        df_columnas
        .dropna(subset=["fecha"])
        .loc[lambda df: df["fecha"] >= fecha_limite]
        .sort_values("fecha")
    )

    columnas_validas = df_columnas["columna"].tolist()

    return df_datos_matriz_c[
        ["Identificador"] + columnas_validas
    ]

async def actualizar_datos_matriz_c():
    df_datos_matriz_c = leer_datos_matriz_c()

    if df_datos_matriz_c.empty:
        logger.warning("No existe data_matriz_c.csv. Construyendo Matriz C completa")
        await matriz_c_builder()
        return leer_datos_matriz_c()

    ultimo_timestamp = obtener_ultimo_timestamp_matriz_c(
        df_datos_matriz_c
    )

    if ultimo_timestamp is None:
        logger.warning("Matriz C sin timestamps. Reconstruyendo Matriz C")
        await matriz_c_builder()
        return leer_datos_matriz_c()

    fecha_inicio = (
        ultimo_timestamp.to_pydatetime()
        + timedelta(seconds=PERIODO_MUESTREO_SEGUNDOS_MATRIZ_C)
    )
    fecha_fin = tiempo_actual()

    if fecha_inicio >= fecha_fin:
        logger.info("Matriz C ya está actualizada")
        return df_datos_matriz_c

    df_identificadores_c = obtener_identificadores_matriz_c()

    if df_identificadores_c.empty:
        logger.warning("No se actualizó Matriz C: no hay identificadores")
        return df_datos_matriz_c

    matrices_nuevas = []

    for subarea, df_subarea in df_identificadores_c.groupby("Subarea"):
        if pd.isna(subarea):
            continue

        logger.info(f"Actualizando Matriz C para subárea: {subarea}")

        df_nuevos_datos_subarea = await generar_dataframe_datos_historicos(
            df_matriz=df_subarea[["Identificador"]],
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            minutos_muestreo=0,
            segundos_muestreo=PERIODO_MUESTREO_SEGUNDOS_MATRIZ_C
        )

        if df_nuevos_datos_subarea.empty:
            continue

        df_nuevos_datos_subarea = filtrar_datos_historicos(
            df_nuevos_datos_subarea,
            subarea
        )

        if df_nuevos_datos_subarea.empty:
            continue

        columnas_tiempo = obtener_columnas_tiempo(
            df_nuevos_datos_subarea
        )

        if columnas_tiempo:
            df_nuevos_datos_subarea = df_nuevos_datos_subarea[
                ~df_nuevos_datos_subarea[columnas_tiempo]
                .isna()
                .all(axis=1)
            ]

        if not df_nuevos_datos_subarea.empty:
            matrices_nuevas.append(df_nuevos_datos_subarea)

    if not matrices_nuevas:
        logger.warning("No se obtuvieron nuevos datos para Matriz C")
        return df_datos_matriz_c

    df_nuevos_datos = pd.concat(
        matrices_nuevas,
        ignore_index=True
    )

    df_nuevos_datos = eliminar_instrumentos_control_operacional(
        df_nuevos_datos
    )

    df_datos_matriz_c_actualizada = df_datos_matriz_c.merge(
        df_nuevos_datos,
        on="Identificador",
        how="outer"
    )

    columnas_ordenadas = obtener_columnas_tiempo_ordenadas(
        df_datos_matriz_c_actualizada
    )

    df_datos_matriz_c_actualizada = df_datos_matriz_c_actualizada[
        ["Identificador"] + columnas_ordenadas
    ]

    df_datos_matriz_c_actualizada = mantener_ventana_matriz_c(
        df_datos_matriz_c_actualizada,
        fecha_fin
    )

    guardar_datos_matriz_c(df_datos_matriz_c_actualizada)

    logger.info(
        f"Matriz C actualizada. Columnas actuales: "
        f"{len(obtener_columnas_tiempo(df_datos_matriz_c_actualizada))}"
    )

    return df_datos_matriz_c_actualizada

async def obtener_metricas_matriz_c():
    df_datos_matriz_c = leer_datos_matriz_c()

    if df_datos_matriz_c.empty:
        return pd.DataFrame()

    return await metricas_de_matrices(
        df_datos_matriz_c
    )