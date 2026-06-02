from .matriz_main_builder import generar_dataframe_datos_historicos, generar_dataframe_ultima_columna
from .metricas import metricas_de_matrices
from .data_loader import tiempo_actual, datos_matriz_a
from datetime import timedelta, datetime, timezone
from pathlib import Path
import pandas as pd
import numpy as np
from app.db.database import SessionLocal
from app.modules.alertas.alerta_service import procesar_alertas_dataframe
from app.modules.alertas.alerta_repository import obtener_activas
from app.core.logger import crear_logger

logger = crear_logger("Pipeline")

def save_data(df_data):
    # Archivo actual
    ruta_actual = Path(__file__).resolve()
    ruta_csv = (
        ruta_actual.parent.parent.parent
        / "data"
        / "data_matriz_c.csv"
    )
    # Esto ya crea o sobreescribe el archivo
    df_data.to_csv(ruta_csv, index=False)
    return
def leer_metricas_matriz_b():
    ruta_actual = Path(__file__).resolve()
    ruta_metricas_matriz_b_csv = (
        ruta_actual.parent.parent.parent
        / "data"
        / "metricas_matriz_b.csv"
    )
    return pd.read_csv(ruta_metricas_matriz_b_csv)
async def matriz_c_builder():
    df_metricas_b = leer_metricas_matriz_b()#Dataframe metricas de la matriz B
    fecha_fin = tiempo_actual()
    fecha_inicio = fecha_fin - timedelta(minutes=15)
    periodo_muestreo_matriz_c = 5 #Muestreo de interpolación, cantidad de muestra por minuto (50000000 son 5 segundos)
    df_matriz_c_datos = await generar_dataframe_datos_historicos(df_metricas_b,fecha_inicio,fecha_fin,0,periodo_muestreo_matriz_c)
    save_data(df_matriz_c_datos)
    df_medidas_estadisticas = await metricas_de_matrices(df_matriz_c_datos)
    return df_medidas_estadisticas


def leer_datos_matriz_c_csv():
    ruta_actual = Path(__file__).resolve()
    ruta_metricas_matriz_b_csv = (
        ruta_actual.parent.parent.parent
        / "data"
        / "data_matriz_c.csv"
    )
    return pd.read_csv(ruta_metricas_matriz_b_csv)
async def actualizar_ultimo_dato_c():
    df_datos_matriz_c = leer_datos_matriz_c_csv()
    df_datos_matriz_c = df_datos_matriz_c.drop(df_datos_matriz_c.columns[1], axis=1)
    fecha_fin = datetime.now(timezone.utc)
    fecha_inicio = fecha_fin - timedelta(seconds=10)
    segundos_interpolacion  = 5 #Muestreo de interpolación, cantidad de muestra por minuto
    df_ultima_columna = await generar_dataframe_ultima_columna(df_datos_matriz_c["Identificador"],fecha_inicio,fecha_fin,0,segundos_interpolacion)
    df_datos_matriz_c = df_datos_matriz_c.merge(
        df_ultima_columna,
        on="Identificador",
        how="left"
    )
    save_data(df_datos_matriz_c)
    return df_datos_matriz_c
async def  obtener_metricas_matriz_c():#Funcion clave que lee datos csv, actualiza ultimo dato y manda las metricas de la matriz C
    df_datos_matriz_c = await actualizar_ultimo_dato_c()
    df_medidas_estadisticas_matriz_c = await metricas_de_matrices(df_datos_matriz_c)
    return df_medidas_estadisticas_matriz_c

def datos_y_alertas_instrumentos(df_tabla_alertas):
    df_info_instrumentos = datos_matriz_a()

    columnas_info = [
        "Identificador",
        "Nombre_TAG",
        "Descripcion",
        "Unidad_de_Ingenieria",
        "Area",
        "Subarea",
        "Sistema",
    ]

    df_info_instrumentos = df_info_instrumentos[columnas_info]

    df_tabla_alertas_enriquecida = df_tabla_alertas.merge(
        df_info_instrumentos,
        on="Identificador",
        how="left"
    )

    columnas_alertas = [
        "Alerta_Cambio_Brusco",
        "Alerta_Oscilacion",
        "Alerta_Senal_Congelada",
    ]

    df_tabla_alertas_enriquecida[columnas_alertas] = (
        df_tabla_alertas_enriquecida[columnas_alertas]
        .astype(str)
        .apply(lambda col: col.str.strip().str.upper())
    )

    df_tabla_alertas_enriquecida = df_tabla_alertas_enriquecida[
        (
            df_tabla_alertas_enriquecida["Alerta_Cambio_Brusco"] != "NORMAL"
        )
        |
        (
            df_tabla_alertas_enriquecida["Alerta_Oscilacion"] != "NORMAL"
        )
        |
        (
            df_tabla_alertas_enriquecida["Alerta_Senal_Congelada"] != "NORMAL"
        )
    ]

    db = SessionLocal()

    try:
        procesar_alertas_dataframe(db, df_tabla_alertas_enriquecida)

        alertas_activas = obtener_activas(db)

        data_alertas = []

        for alerta in alertas_activas:
            data_alertas.append({
                "Identificador": alerta.identificador,
                "Area": alerta.area,
                "Subarea": alerta.subarea,
                "Sistema": alerta.sistema,
                "Tipo_Alerta_DB": alerta.tipo_alerta,
                "Nivel_Alerta_DB": alerta.nivel_alerta,
                "Fecha_Inicio_Alarma": alerta.fecha_inicio,
                "Fecha_Ultima_Actualizacion": alerta.fecha_ultima_actualizacion,
                "Fecha_Fin": alerta.fecha_fin,
                "Ciclos_Alarma": alerta.ciclos,
                "Alarma_Activa": alerta.activa,
            })

        df_alertas_db = pd.DataFrame(data_alertas)

        if not df_alertas_db.empty:
            df_resumen_alertas = (
                df_alertas_db
                .groupby("Identificador")
                .agg({
                    "Tipo_Alerta_DB": lambda x: ", ".join(x),
                    "Nivel_Alerta_DB": lambda x: ", ".join(x),
                    "Fecha_Inicio_Alarma": "min",
                    "Fecha_Ultima_Actualizacion": "max",
                    "Ciclos_Alarma": "max",
                    "Alarma_Activa": "max",
                })
                .reset_index()
            )

            df_tabla_alertas_enriquecida = df_tabla_alertas_enriquecida.merge(
                df_resumen_alertas,
                on="Identificador",
                how="left"
            )

    finally:
        db.close()
    df_tabla_alertas_enriquecida = df_tabla_alertas_enriquecida.drop(
        columns=[
            "Alerta_Cambio_Brusco",
            "Alerta_Oscilacion",
            "Alerta_Senal_Congelada",
        ],
        errors="ignore"
    )

    df_tabla_alertas_enriquecida = df_tabla_alertas_enriquecida.rename(
        columns={
            "Tipo_Alerta_DB": "Tipo_Alerta",
            "Nivel_Alerta_DB": "Nivel_Alerta",
        }
    )
    df_tabla_alertas_enriquecida = (
        df_tabla_alertas_enriquecida
        .replace({np.nan: None})
    )

    return df_tabla_alertas_enriquecida