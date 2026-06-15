from datetime import timedelta, datetime, timezone
import pandas as pd
from .data_loader import (
    tiempo_actual,
    datos_matriz_a,
    INSTRUMENTOS_CONTROL_OPERACIONAL
)
from .filtros_iniciales import eliminar_instrumentos_control_operacional
from .historian_builder import (
    generar_dataframe_datos_historicos,
    generar_dataframe_ultima_columna,
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


async def matriz_c_builder():
    df_metricas_b = leer_metricas_matriz_b()

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
    fecha_fin = tiempo_actual()
    fecha_inicio = fecha_fin - timedelta(minutes=30)

    periodo_muestreo_matriz_c = 10
    matrices_c = []

    for subarea, df_subarea in df_identificadores_c.groupby("Subarea"):
        if pd.isna(subarea):
            continue

        logger.info(f"Construyendo matriz C para subárea: {subarea}")

        df_matriz_c_subarea = await generar_dataframe_datos_historicos(
            df_subarea[["Identificador"]],
            fecha_inicio,
            fecha_fin,
            0,
            periodo_muestreo_matriz_c
        )

        if df_matriz_c_subarea.empty:
            continue

        df_matriz_c_subarea = filtrar_datos_historicos(
            df_matriz_c_subarea,
            subarea
        )

        if df_matriz_c_subarea.empty:
            continue

        columnas_tiempo = [
            col for col in df_matriz_c_subarea.columns
            if col != "Identificador"
        ]

        if columnas_tiempo:
            df_matriz_c_subarea = df_matriz_c_subarea[
                ~df_matriz_c_subarea[columnas_tiempo]
                .isna()
                .all(axis=1)
            ]

        if not df_matriz_c_subarea.empty:
            matrices_c.append(df_matriz_c_subarea)

    if not matrices_c:
        logger.warning("No se construyó matriz C: no hay instrumentos con datos")
        return pd.DataFrame()

    df_matriz_c_datos = pd.concat(
        matrices_c,
        ignore_index=True
    )

    df_matriz_c_datos = eliminar_instrumentos_control_operacional(
        df_matriz_c_datos
    )

    guardar_datos_matriz_c(df_matriz_c_datos)

    df_medidas_estadisticas = await metricas_de_matrices(
        df_matriz_c_datos
    )

    return df_medidas_estadisticas


async def actualizar_ultimo_dato_c():
    df_datos_matriz_c = leer_datos_matriz_c()

    if df_datos_matriz_c.empty:
        return df_datos_matriz_c

    if len(df_datos_matriz_c.columns) > 1:
        df_datos_matriz_c = df_datos_matriz_c.drop(
            columns=df_datos_matriz_c.columns[1]
        )

    fecha_fin = datetime.now(timezone.utc)
    fecha_inicio = fecha_fin - timedelta(seconds=10)

    segundos_interpolacion = 5

    df_ultima_columna = await generar_dataframe_ultima_columna(
        df_datos_matriz_c["Identificador"],
        fecha_inicio,
        fecha_fin,
        0,
        segundos_interpolacion
    )

    df_datos_matriz_c = df_datos_matriz_c.merge(
        df_ultima_columna,
        on="Identificador",
        how="left"
    )

    guardar_datos_matriz_c(df_datos_matriz_c)

    return df_datos_matriz_c


async def obtener_metricas_matriz_c():
    df_datos_matriz_c = await actualizar_ultimo_dato_c()

    if df_datos_matriz_c.empty:
        return pd.DataFrame()

    df_medidas_estadisticas_matriz_c = await metricas_de_matrices(
        df_datos_matriz_c
    )

    return df_medidas_estadisticas_matriz_c