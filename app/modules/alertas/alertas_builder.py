import numpy as np
import pandas as pd

from app.db.database import SessionLocal
from app.core.logger import crear_logger

from app.modules.alertas.alerta_service import procesar_alertas_dataframe
from app.modules.alertas.alerta_repository import obtener_activas
from app.modules.pipeline.matriz_a import datos_matriz_a
from app.modules.alertas.criterios_alertas import COLUMNAS_ALERTAS


logger = crear_logger("Alertas")


COLUMNAS_INFO_INSTRUMENTOS = [
    "Identificador",
    "Nombre_TAG",
    "Descripcion",
    "Unidad_de_Ingenieria",
    "Area",
    "Subarea",
    "Sistema",
]


def obtener_info_instrumentos():
    df_matriz_a = datos_matriz_a()

    columnas_existentes = [
        col for col in COLUMNAS_INFO_INSTRUMENTOS
        if col in df_matriz_a.columns
    ]

    return df_matriz_a[columnas_existentes].copy()


def normalizar_columnas_alertas(df_alertas):
    columnas_existentes = [
        col for col in COLUMNAS_ALERTAS
        if col in df_alertas.columns
    ]

    if not columnas_existentes:
        return df_alertas

    df_alertas = df_alertas.copy()

    df_alertas[columnas_existentes] = (
        df_alertas[columnas_existentes]
        .fillna("NORMAL")
        .astype(str)
        .apply(lambda col: col.str.strip().str.upper())
    )

    return df_alertas


def enriquecer_alertas_para_guardado(df_tabla_alertas):
    if df_tabla_alertas.empty:
        return pd.DataFrame()

    df_info_instrumentos = obtener_info_instrumentos()

    if df_info_instrumentos.empty:
        logger.warning("No se pudo obtener información de instrumentos")
        return pd.DataFrame()

    df_alertas_enriquecidas = df_tabla_alertas.merge(
        df_info_instrumentos,
        on="Identificador",
        how="left"
    )

    df_alertas_enriquecidas = normalizar_columnas_alertas(
        df_alertas_enriquecidas
    )

    return df_alertas_enriquecidas


def convertir_alertas_activas_a_dataframe(alertas_activas):
    if not alertas_activas:
        return pd.DataFrame()

    return pd.DataFrame([
        {
            "Identificador": alerta.identificador,
            "Nombre_TAG": alerta.nombre_tag,
            "Descripcion": alerta.descripcion,
            "Unidad_de_Ingenieria": alerta.unidad_de_ingenieria,
            "Area": alerta.area,
            "Subarea": alerta.subarea,
            "Sistema": alerta.sistema,
            "Tipo_Alerta": alerta.tipo_alerta,
            "Nivel_Alerta": alerta.nivel_alerta,
            "Fecha_Inicio_Alarma": alerta.fecha_inicio,
            "Fecha_Ultima_Actualizacion": alerta.fecha_ultima_actualizacion,
            "Fecha_Fin": alerta.fecha_fin,
            "Ciclos_Alarma": alerta.ciclos,
            "Alarma_Activa": alerta.activa,
        }
        for alerta in alertas_activas
    ]).replace({np.nan: None})


def obtener_alertas_activas_dataframe(db):
    alertas_activas = obtener_activas(db)

    return convertir_alertas_activas_a_dataframe(
        alertas_activas
    )


def procesar_y_obtener_alertas_activas(df_tabla_alertas):
    if df_tabla_alertas.empty:
        return pd.DataFrame()

    df_alertas_para_guardar = enriquecer_alertas_para_guardado(
        df_tabla_alertas
    )

    if df_alertas_para_guardar.empty:
        return pd.DataFrame()

    db = SessionLocal()

    try:
        procesar_alertas_dataframe(
            db,
            df_alertas_para_guardar
        )

        return obtener_alertas_activas_dataframe(db)

    finally:
        db.close()